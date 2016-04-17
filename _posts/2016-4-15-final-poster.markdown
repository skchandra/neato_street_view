---
layout: post
title:  "Final Product"
date:   2016-04-15 10:08:53
categories: blog
---

Final Product

Our final project is split into a few different components. We first generate a SLAM map using geomapping, and save it for future use. Then, we place our robot at a pre-determined waypoint corresponding to the map and initiate a program that spins the robot roughly 360 degrees. While the robot spins, it takes pictures at specific orientations, giving us multiple pictures for each waypoint. Then, these pictures are used in another program for panorama stiching - we stitch around three pictures together, giving us about 23-27 panoramas per waypoint. These filepaths are then stored in a database, which stores the x- and y-coordinates for the waypoint, and angle of the robot’s orientation. Finally, this database is used with the web application. The web application displays the SLAM map with each waypoint marked as a green dot. When a waypoint is clicked on, the corresponding panorama filepaths from the database are called to display a 360 degree view of that waypoint. The user can then interact with the panorama using arrow keys to load new panoramas, or return to the map to look at a new waypoint. A link to our final poster with extended descriptions of each component can be found [here](https://drive.google.com/file/d/0ByyJ5ZKB-imSUFd3NlQ0SDh6elk/view)!
