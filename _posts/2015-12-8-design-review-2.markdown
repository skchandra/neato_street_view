---
layout: post
title:  Design Review 2!
date:   2015-12-8 22:54:25
categories: blog
---


With less than 2 weeks before our final presentation, the Neato Street View team has come to a great stopping point, developing working MVPs for our major subsystems.  Please have a look at our progress!

##Web Application
* Basic Interface:
    1. Ability to click on waypoints in a SLAM map
    2. Pan the camera angle to view a 360 degree panorama

![Image]({{ site.url }}/images/dr2/website1.png)
![Image]({{ site.url }}/images/dr2/website2.png)
_Figure 1: Web Application where 1) green dots represent clickable waypoints on the map and 2) arrow buttons control the camera angle of the 360 degree view point_

* Need to do:
    1. user interface, include depth perception
    2. take pics higher from ground in a better place (dining hall, outside of robo lab AC 2nd floor)
    3. capture photos using fisheye lense with camera calibration for undistorted, wide angle view

## Collecting Panoramas + Waypoints

### Collecting 360 degree views with a ROS Node

* Collect a total of `36` photos
* Take a snapshot every `10` degrees of rotation
* In order to get the widest range, we merge `5` pictures, which are `20` degrees (`2` index difference * `10` degrees) apart from each other.

### Improved Stitching Methods

We landed on an improved stitching method for generating panoramas which we call the __Two Side Merge__ method.  The effectiveness of this approach was generating panoramas that were balanced on the left and right side.

![Image]({{ site.url }}/images/dr2/two-side-merge-method.png)
_Figure 2: Illustration of the two side merge method_

![Image]({{ site.url }}/images/dr2/two-side-merge-result.png)
_Figure 3: Result of the two side merge method_

![Image]({{ site.url }}/images/dr2/two-side-merge-result1.jpg)
_Figure 4: Applying the two side merge method to photos captured from the Neato_

### Comparison to Old Stitching Methods

Compare these results to our previous stitching methods. The panorama produced is subpar, as one side of the image is heavily warped.

![Image]({{ site.url }}/images/dr2/old-method.png)
_Figure 5: Old Methods of Stitching_

![Image]({{ site.url }}/images/dr2/old-result.png)
_Figure 6: Panoroma generated using the old method_

### Select from 36 Photos and Merge into Panorama
* __`36` photos__ representing the 360 degree view for a particular waypoint is saved in a unique folder
{% highlight json%}
"images" : {
    "raw" : {
        "0.0,0.0,0.0" : [
            "0.jpg",
            "10.jpg",
            (...),
            "-20.jpg",
            "-10.jpg"
        ],
        "1.0,1.0,0.0" : [
            "0.jpg",
            "10.jpg",
            (...),
            "-20.jpg",
            "-10.jpg"
        ]
    }
}
{% endhighlight %}
* starting with an incremented phase offset, the algorithm picks __a photo every `20` degrees__ (the difference) and __merge `5` photos__ for one panorama.
* the incremented starting phase and fixed difference allow us to merge photos in many different combinations of 5 photos

* Example of selecting photos for merging. In this example, the __starting phase__ is `3` and the __index difference__ between photos in every combination is `2`.

    `[3,5,7,9,11]`

    `[6,8,10,12,14]`

### SQL Database

We updated the schema of our database to reflect the current method of generating a panorama for each waypoint pose __x, y, and theta.__

The paths to the final panoramas are stored in the local file system.  The path is associated with a unique waypoint row in the database.

{% highlight json%}
"images" : {
    "final" : [
        "x,y,theta_panorama.jpg",
        ...
    ]
}
{% endhighlight %}

![Image]({{ site.url }}/images/dr2/sqlite.png)
_Figure 7: Final Panoromas are associated with their waypoints in the SQL database schema_

### Learning SLAM using an existing C++ implementation
The Python Implementation of the SLAM algorithm, while high on our learning goals, was not an integral part of the eventual Neato Street View web app that we would demo.  In fact, because we will not be implementing the entirity of SLAM in Python (only the important systems such as `ScanMatcher`), the SLAM algorithm that will be generating the maps will still be the original C++ Hector SLAM package. We are happily still pursuing the Python implementation for the sake of learning more about mobile robotics algorithms and C++.

The following summarizes our progress:

* [ __DONE__ ] __Serializing Input and Ouput Data__ of the C++ `ScanMatcher::matchData` into JSON format.  This data serves as a ground truth to what the function should be taking in and returning out.
* [ __DONE__ ] __Load JSON__ into Python successfully
* [ - - - - - ] __Write Unit Testing Modules__ which feeds the serialized inputs as arguments to the Python function implementation and compares the function output to the matching serialized outputs
* [ - - - - - ] __Implement SLAM components in Python__, such as the equivalent of `ScanMatcher::matchData` in the C++ `hector_slam` module.

Check out some of the JSON `_dataContainer.json` and `_io.json` (input/output) files that were produced as a result of serializing the data from the ground truth implementation.

__16bithash_dataContainer.json__
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

__16bithash_io.json__
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