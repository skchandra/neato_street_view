---
layout: post
title:  Less than 2 weeks before our final presentations!
date:   2015-12-8 22:54:25
categories: blog
---

# Project Update

## Collecting Panoramas + Waypoints

### Collecting 360 degree views with a ROS Node

* Collect a total of 36 Photos
* Take a snapshot every 10 degrees of rotation
* In order to get the widest range, we merge 5 pictures, which are 20 degrees (2 diff * 10 degrees) apart from each other.

### Improved stitching methods

![Image]({{ site.url }}/images/dr2/two-side-merge-method.png)
[Figure 1: Illustration of the two side merge method]

![Image]({{ site.url }}/images/dr2/two-side-merge-result.png)
[Figure 2: Result of the two side merge method]

![Image]({{ site.url }}/images/dr2/two-side-merge-result1.jpg)
[Figure 3: Applying the two side merge method to photos captured from the Neato]

![Image]({{ site.url }}/images/dr2/old-method.png)
[Figure 4: Old Methods of Stitching]

![Image]({{ site.url }}/images/dr2/old-result.png)
[Figure 5: Panoroma generated using the old method ]

### Select and Merge Script
* 36 photos representing the 360 degree view for a particular waypoint is saved in a unique folder
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
* starting with an incremented phase offset, the algorithm picks a photo every `20` degree (the difference) and merge `5` photos for one panorama.
* the incremented starting phase and fixed difference allow us to merge photos in many different combinations of 5 photos

* Example of selecting photos for merging. In this example, the `starting phase` is `3` and the `difference` between photos in every combination is `2`.

    `[3,5,7,9,11]`

    `[6,8,10,12,14]`

### SQL Database

We updated the schema of our database to reflect the current method of generating a panorama for each waypoint `(pose x, pose y, theta)`

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
[Figure 6: Final Panoromas are associated with their waypoints in the SQL database schema]