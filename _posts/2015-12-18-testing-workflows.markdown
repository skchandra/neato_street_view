---
layout: post
title:  "Testing Work flows in ROS, C++, and Python."
date:   2015-12-18 01:28:25
categories: blog
---

Hey there!  This is Ryan and I would like to present the approach to testing my team found, when trying to re-implement a SLAM algorithm written into C++ into Python.

This should serve as a great starter for teams who want to try an efficient process to testing a robotics algorithm.  Here's an outline of the workflow my team found to be most effective.

- Collecting replayable robot sensor data using `rosbag`.
- Logging program state values from an existing implementation
- Using Python's `unittest` library to quickly implement larger and larger code blocks.

##Recording and Playing ROS bags
A `rosbag` is a capture of ROS topics which, when replayed in the absence of the physical robot, publishes those same topics.  This is helpful when you want real data to test your algorithm with, but do not want the overhead of starting up the physical robot.  Since creating a SLAM map requires a robot to drive around and explore an entire area, this process could take upwards of minutes! Recording a `rosbag` of this exploration makes the process infinitely easier and repeatable.

In order to record all sensor data into a rosbag, one can use

`rosbag record -a -O path/to/rosbag/file.bag`

Often, one might not want all topics, as collecting the camera feed, for example, will result in files that are unnecessarily large if your application does not require images.

For the Neato ROS topics, the command to record all data but the camera feed is

`rosbag record -x "(.*)/camera_image(.*)"`.

In order to play the `rosbag`, one can use the command

`rosbag play path/to/rosbag/file.bag`

or to have the bag playing on loop,

`rosbag play -l path/to/rosbag/file.bag`

More info can be found on the [ROS website](http://wiki.ros.org/rosbag/Commandline).

##Logging program state values from an existing implementation
Our work with test-driven development of existing algorithmic implementations required a very specific agenda:

1. Record the program states of an existing implementation.  This could include values of input arguments, output arguments, and/or variables during intermediate computations.
2. Write new implementations that could take the same input and produce the same outputs.

Not every robotics project that can be tested should be tested this way. But if you have an idea of what the input and output states of methods or objects should be, collecting the ground truth outputs is a great way to know if your implementation is producing the expected outputs.

The top-level method that we were trying to implement in the Hector SLAM algorithm was called `ScanMatcher::matchData`.  This method was called many times over the course of playing through the SLAM collection ROS bag.

We used the JSON (Javascript Object Notation) format to store our program state, with each uniquely name JSON file representing the particular state of the algorithm through one call of the `matchData` method. JSON became the right choice for our use-case, because loading a JSON file into Python returns a highly usable Python dictionary which has all the program state names as `dict.keys()` and variable values as `dict.values()`.  In addition, if your program states are matrices or vectors, these are stored just as easily as flattened lists or nested lists. We used randomly-generated 16-bit hashes as the file names to create a uniquely named file.

Here are two files, with the same 16-bit hash, representing the dataContainer, or laser scan values, and other input and outputs states through one call of the `ScanMatcher::matchData` method.

__01AFNWIWO5Tyknv3_dataContainer.json__
{% highlight json %}
{
"origo": [-1.016,0],
"size": 161,
"dataPoints": [
[13.244,3.65935e-05],
[12.6919,0.239308],
...
[11.8127,-0.897036],
[13.244,3.58995e-05]
]
}
{% endhighlight %}

__01AFNWIWO5Tyknv3_io.json__
{% highlight json %}
{
"beginEstimateWorld" : [
1.26894,0.152306,-0.883637
],
"covMatrixIn" : [
15.6009,-0.675218,-35.5471,-0.675218,29.1469,-216.242,-35.5471,-216.242,6552.29
],
"maxIterations" : 3,
"beginEstimateMap" : [
524.689,513.523,-0.883637
],
"covMatrixOut" : [
18.1631,-0.14603,12.4166,-0.14603,32.7221,-129.747,12.4166,-129.747,2577.22
],
"newEstimateMap" : [
524.906,513.226,-0.918397
],
"newEstimateWorld" : [
1.29057,0.122601,-0.918397
]
}
{% endhighlight %}

If you ever need to edit your logging code, there should be no issue because you can replay the ROS bag, collecting these new values.  Speeding-up the process of collecting variables, seeing which ones are useful to measure, and recollecting more useful values based on your work is essential for efficient development!

##Unit-testing in Python

Test-driven development "is a software development process that relies on the repetition of a very short development cycle: first the developer writes an (initially failing) automated test case that defines a desired improvement or new function, then produces the minimum amount of code to pass that test, and finally refactors the new code to acceptable standards" ([Wikipedia, 2015](https://en.wikipedia.org/wiki/Test-driven_development)).  If we can write tests for different abstractions in our code, we can quickly be confident about the little pieces that compose the overall algorithm we might be implementing.

The approach is to find a small function in the algorithm, log the expected inputs and outputs, and then make a test case for that function! For example, there was a utility function in the C++ hector slam code called `normalize_angle` which constrains an angle in radians between the interval `[0, pi) U [-pi, 0)`.  To write an equivalent function in Python, we will create the skeleton of this utility method in order to use it in a unit-test.

Skeleton for Python `normalize_angle` function in the implementation file `slam_v1.py`:
{% highlight python %}
class Util(object):
    @staticmethod
    def normalize_angle(angle):
        """ Constrains the angles to the range [0, pi) U [-pi, 0) """
        # TODO: write method to constrain the angle to the interval
        return angle
{% endhighlight %}

Then, we can write our test. Since the method should constrain the angles within the interval between `[-pi, pi]`, we can feed in several different angles on the interval `[-2*pi, 2*pi]` and hope that the angle outputs will never be lower than `-pi` or higher than `pi`.

A python unit test for `normalize_angle` in the test file `test_ScanMatcher.py`:
{% highlight python %}
class TestUtil(unittest.TestCase):
    def test_normalize_angle(self):
        x1 = np.linspace(-2*np.pi, 2*np.pi, 25)
        f = np.vectorize(Util.normalize_angle)
        x2 = f(x1)
        print "\n", np.column_stack((x1,x2))
        self.assertTrue(x2.min() >= -np.pi)
        self.assertTrue(x2.max() >= np.pi)
{% endhighlight %}

Then it is simply about writing the minimum implementation in `Util.normalize_angle` for the test case to pass!  To run the test, python has a test runner called [`nosetests`](https://nose.readthedocs.org/en/latest/), which will find all python `unittest` classes and run those methods whose names start with `test_`.

To test it, I changed to the directory of the the test file and typed

`nosetests test_ScanMatcher.py`.

Here was the output for the dummy implementation which fails the test case, as expected

    ...F
    ======================================================================
    FAIL: test_normalize_angle (test_ScanMatcher.TestUtil)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/ryan/catkin_ws/src/neato_street_view/hector_slam/python_slam/test_ScanMatcher.py", line 48, in test_normalize_angle
        self.assertTrue(x2.min() >= -np.pi)
    AssertionError: False is not true
    -------------------- >> begin captured stdout << ---------------------

    [[-6.28318531 -6.28318531]
     [-5.75958653 -5.75958653]
     [-5.23598776 -5.23598776]
     [-4.71238898 -4.71238898]
     [-4.1887902  -4.1887902 ]
     [-3.66519143 -3.66519143]
     [-3.14159265 -3.14159265]
     [-2.61799388 -2.61799388]
     [-2.0943951  -2.0943951 ]
     [-1.57079633 -1.57079633]
     [-1.04719755 -1.04719755]
     [-0.52359878 -0.52359878]
     [ 0.          0.        ]
     [ 0.52359878  0.52359878]
     [ 1.04719755  1.04719755]
     [ 1.57079633  1.57079633]
     [ 2.0943951   2.0943951 ]
     [ 2.61799388  2.61799388]
     [ 3.14159265  3.14159265]
     [ 3.66519143  3.66519143]
     [ 4.1887902   4.1887902 ]
     [ 4.71238898  4.71238898]
     [ 5.23598776  5.23598776]
     [ 5.75958653  5.75958653]
     [ 6.28318531  6.28318531]]

    --------------------- >> end captured stdout << ----------------------

    ----------------------------------------------------------------------
    Ran 4 tests in 0.004s

    FAILED (failures=1)

You can then use print statements to stdout as well as the assertion errors that the test case gives you to iterate towards a passing implementation!  The passsing implementation for this function can be found at the [most recent state of our github tree](https://github.com/youralien/hector_slam/blob/python/python_slam/slam_v1.py#L24).

You can see that some functions, like `normalize_angle`, are so easy to create expected input and output pairs.  Other methods we found in the SLAM algorithm had function inputs and outputs that were much more particular to the parameters and context of the SLAM algorithm. For these types, the unit-test will likely load the values of the expected inputs and outputs from the logged JSON files.

Below is a slightly longer test case which uses loaded JSON ground-truth program states used as a comparison.

{% highlight python %}
io = json.load(open('01AFNWIWO5Tyknv3_io.json', 'r'))
dc = json.load(open('01AFNWIWO5Tyknv3_dataContainer.json', 'r'))

class TestScanMatcher(unittest.TestCase):
    def test_matchData(self):
        scanMatcher = ScanMatcher(io=io, dc=dc)
        out = scanMatcher.matchData(
              beginEstimateWorld=scanMatcher.io['beginEstimateWorld']
            , gridMapUtil=None
            , dataContainer=scanMatcher.dc
            , covMatrix=scanMatcher.io['covMatrixIn']
            , maxIterations=scanMatcher.io['maxIterations']
            )
        newEstimateWorld, newEstimateMap, covMatrixOut = out
        vector3ify = lambda arr: np.array(arr).reshape((3,))
        matrix3ify = lambda arr: np.array(arr).reshape((3,3))
        print "test values"
        print vector3ify(scanMatcher.io['newEstimateWorld'])
        print vector3ify(scanMatcher.io['newEstimateMap'])
        print matrix3ify(scanMatcher.io['covMatrixOut'])

        print "output values"
        print newEstimateWorld
        print newEstimateMap
        print covMatrixOut
        self.assertTrue(np.allclose(newEstimateWorld, vector3ify(scanMatcher.io['newEstimateWorld'])))
        self.assertTrue(np.allclose(newEstimateMap, vector3ify(scanMatcher.io['newEstimateMap'])))
        self.assertTrue(np.allclose(covMatrixOut, matrix3ify(scanMatcher.io['covMatrixOut'])))
{% endhighlight %}

Notice that inserting the inputs from the JSON log files is a very readable process via the Python dictionary API. The more human readable and less arbitrary the name of the program state variables, the better.

{% highlight python %}
out = scanMatcher.matchData(
      beginEstimateWorld=scanMatcher.io['beginEstimateWorld']
    , gridMapUtil=None
    , dataContainer=scanMatcher.dc
    , covMatrix=scanMatcher.io['covMatrixIn']
    , maxIterations=scanMatcher.io['maxIterations']
    )
{% endhighlight %}

The last lines of this snippet which have the `self.asserTrue` statements are comparing the NumPy vectors for the new estimate of the world post, `newEstimateWorld`, with the ground truth value given by the JSON logs.

{% highlight python %}
self.assertTrue(np.allclose(newEstimateWorld, vector3ify(scanMatcher.io['newEstimateWorld'])))
{% endhighlight %}

Check out the final state of our unit tests for the Hector SLAM scan matcher, and [what could be Olin's first Python unit-test](https://github.com/youralien/hector_slam/blob/python/python_slam/test_ScanMatcher.py)!

## Conclusion
Hopefully that's enough Python / ROS testing workflow details to make you dangerous!  If you have any questions, feel free to leave a line at _`ryan.louie@students.olin.edu`_ or reach out to my on Github at [@youralien](https://www.github.com/youralien).
