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

Check out what could be Olin's first [Python unit-test here](https://github.com/youralien/hector_slam/blob/python/python_slam/test_ScanMatcher.py)!