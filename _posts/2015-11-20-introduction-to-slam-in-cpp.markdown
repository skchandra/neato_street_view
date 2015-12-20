---
layout: post
title:  "A SLAMming Learning Experience In C++"
date:   2015-11-20 01:28:25
categories: blog
---

Hey there!  This is Ryan and Kiki and we want to talk to you about a piece of the “Neato (Google) Street View” project: understanding a SLAM algorithm implementation.  For this, we looked at an existing implementation of Hector SLAM, a particular method of SLAM.  This implementation, however, is written in C++, a programming language we were not familiar with at first.  To understand the implementation of Hector SLAM, we learned how to read existing C++ code in the process!

Stepping into a code base, with multiple depths of abstraction, written in a language we were not familiar with, was really challenging at the beginning.  Take our word for it: while the challenges were many, it was well worth it!  

**Kiki:** The most helpful thing we did while going through SLAM was drawing a system diagram, because SLAM initially seemed as though it would be fairly straightforward, but was really very complex. This was largely due to the fact that are only a few executable files, but dozens of headers containing class definitions and algorithms that we had to go through. When we actually went through and made a system diagram that linked together the significant components, I was able to understand how the different classes interacted and were integrated together, and the overall framework has begun to make sense. 

**Ryan:**  One of the immediate challenges was searching quickly through the tree of abstractions to map out the entire system.  Protip:  Use a text editor that has the power to search in multiple directories!  SublimeText3 was fine for my needs, enabling me to open different files in the folder quickly, searching across all directories for a certain class name, and going to specific lines.  In addition, you can always print out values of a particular parameter if you are not sure what the values represent.  We did this to understand what the values for a 3-dimensional pose vector, which ended up being the x, y, and theta angles in reference to the robot.

##An Intro to C++
For those of you who are new to C++, we’ve included some notes and syntax rules that we learned while going through SLAM documentation:

###File Organization
C++ has two types of files: *.h and *.cpp files, which stand for “header” and “C plus plus” respectively.

Honestly, the conventions for using these two types are flexible. In many cases, *.h files specify a class declaration, or what an outline of the class will look like, while *.cpp files will methods definitions filled out in greater detail.

The reasons why the distinction between these two exist is because of how the C++ compiler works.  Without going into too much detail, *.cpp files are “poor and lonesome;” that means the functions in *.cpp files can’t be shared between each other.  Since modularization of code into separate files is good, C++ provides header files.  Header files allow us to still see the declaration of functions (declarations tells the compiler what types the inputs and outputs of functions are). Think of the header files as glue files that allow the files in your project to talk to each other, while not needing to worry about the underlying definitions of their implementations.

If you would like to learn more, this summarized answer comes from [here](http://stackoverflow.com/questions/333889/why-have-header-files-and-cpp-files-in-c#answer-333964 "stackoverflow post").

###Inside a Class
Classes consist of member functions, each of which define specific tasks that objects, or instances of the class, can perform. These functions begin with declarations that specify the function name, return type, and parameters. One example is: `void setMapGridSize(const Eigen::Vector2i& newMapDims)`, where ‘void’ declares that the function returns nothing, ‘setMapGridSize’ sets the name of the function, and the code inside the parentheses signifies that the function takes in a variable of name ‘newMapDims’ and type ‘Eigen::Vector2i’. The code that goes inside a function is known as the definition. 

In order to create an object, the first function in a class is typically a constructor. Constructors are similar to `__init__` methods in Python, and initialize variables for the class to use. 

Now that we know there are different types of functions, it’s also useful to know the different ways in which they are called:

1. In order to access object methods or reference a method, a period is used. An example is `private_nh_.param("pub_drawings", p_pub_drawings, false);`, where ‘private_nh_ is the object, and its particular parameters for drawings is being set
2. If you want to access a method of a class/namespace directly, use double colons. An example of this is `std::string mapTopicStr(mapTopic_);`, where ‘std’ is the namespace and its method ‘string’ is being referenced
3. To reference a pointer to an object, use an arrow (->). We will not go into pointers here, but [this](https://en.wikipedia.org/wiki/Pointer_(computer_programming) "Wiki page") Wikipedia page has a great overview. An example of a reference to a pointer is `drawInterface->setScale(0.05f);`, where ‘drawInterface’ is the pointer to an object, and its method being accessed is ‘setScale’

As mentioned earlier, constructors are used to create objects. A feature that C++ doesn’t entirely do on its own is garbage collection, so it is also necessary to remove the object once it is no longer used. This is where destructors come into play. Destructors are identified by a tilda before the name, and, when called, is used to clean up memory. 

Finally, something really awesome about C++ is that, similar to typedefs in C, you can define your own aliases for types. Typedefs can be used to create an alias for array types, function types, pointers, classes, etc. They are used in the following way: `typedef OccGridMapBase<LogOddsCell, GridMapLogOddsFunctions> GridMap;`, where the type ‘OccGridMapBase<LogOddsCell, GridMapLogOddsFunctions>’ can now be accessed simply through the word ‘GridMap’.

###Standard Datastructures
* `std::vector` is an array
* Example: `std::vector<MapProcContainer> mapContainer`


##SLAM!
SLAM stands for Simultaneous Localization and Mapping.  We used an algorithm called Hector SLAM, named after the lab which published the first research paper.

- [Research Paper](http://www.sim.informatik.tu-darmstadt.de/publ/download/2011_SSRR_KohlbrecherMeyerStrykKlingauf_Flexible_SLAM_System.pdf)
- [Original C++ Repo](https://github.com/tu-darmstadt-ros-pkg/hector_slam)

###Overarching framework and architecture - system diagram

Through looking at the files SLAM is comprised of, we discovered that its architecture was significantly more complicated than we had initially assumed. In general, SLAM creates maps and has different levels of resolution for each map, so that if one layer of resolution messes up, the rest of the layers are able to counteract and make up for it. The main .cpp file reads from the laser scan node, and scales the scan data for each map level. Then, the scan data goes through a process of matching the new data with the existing map. Once each layer is updated, the overall map is generated according to highest intensities of occupancy on each level. 

###Main Files

####HectorSlamProcessor

The `HectorSlamProcessor` has an `update` method which is called from the `HectorMappingRos` module.  The `update` method propogates the data and state for most of the algorithmic code to run.

Obtaining a new pose estimate

`newPoseEstimateWorld = (mapRep->matchData(poseHintWorld, dataContainer, lastScanMatchCov));`

`mapRep`: Hector SLAM works by aligning beam endpoints with the mapped learned so far.  The map representation stores the map and the processing functions for a particular map. 

The `matchData` method performs scan matching using the stored map representation.  It takes in an intialization, scan measurements, and covariance information from the previous time step to estimate a new pose.

If the new estimated pose is different enough than the old pose, update the map representation

{% highlight C++ %}
if(util::poseDifferenceLargerThan(newPoseEstimateWorld, lastMapUpdatePose, paramMinDistanceDiffForMapUpdate, paramMinAngleDiffForMapUpdate) || map_without_matching) {

  mapRep->updateByScan(dataContainer, newPoseEstimateWorld);

  mapRep->onMapUpdated();
  lastMapUpdatePose = newPoseEstimateWorld;
}
{% endhighlight %}

####MapRepMultiMap
“Any hill climbing/gradient based approach has the inherent risk of getting stuck in local minima.  As the presented apporach is based on gradient ascent, it also is potentially prone to get stuck in local minima.  The problem is mitigated by using a multi-resolution map representation… we use multiple occupancy grid maps with each coarser map having half the resolution of the preceding one.”

`MapRepMultiMap` has a mapContainer and dataContainer which stores the map processing containers and laser scan data containesr respectively for the different resolution occupancy grids.  

For each map processing container, `matchData` and `updateByScan` methods are available.

For `matchData`, the “scan alignment process is started at the coareset map level, with the resulting estimated pose getiting used as the start estimate for the next level.”

####MapProcContainer
The map processing container contains the states of the map (via class attributes) and their algorithmic functions (via class methods).

The occupancy grid map is stored in the `gridMap` attribute

An occupancy map, in the theoretical case, is an underlying probably distribution of the likelihood that places in a map are occupied by objects.  We represent occupancy maps using a discrete grid of values. “Intuitively, the grid map cell values can be viewed as samples of an underlying continous probably distribution.”  In order to calculate the occupancy values of places in the map finer than the grid resolution and to compute derivatives of the map to help for gradient-based approaches, we can use interpolation and derivative approximation from discrete values.   

* `gridMapUtil` provides the mathematical definitions for interpolating and calculating gradients.
* `scanMatcher` is an instance of the `ScanMatcher` class, which we will talk about shortly.  This is where optimization of the alignment of beam endpoints with the map learnt so far.
* `updateByScan` method updates the occupany grid based on the new scan beam endpoints.

####GridMap
This file is where the representation and update methods are located for the Occupancy Grid Map.  `GridMap` is composed of one key function and another helper function:

* `updateByScan`: Updates the occupancy grid using the laser scan distances from the robot position
* `updateLineBresenhami`: Updates the map using a bresenhami variant for drawing a line from beam start to beam endpoint in map coordinates.  The bresenhami method is a ray tracing method.

####ScanMatcher
As the name implies, this file is where the classes and algorithms relating to scan matching are defined. `ScanMatcher` is composed of three notable functions:

* `matchData`: This takes in the data container with new scans and performs transformations upon it to match the scans as closely as possible with the existing map. Within the function, there is a limit set to the maximum angle change that the Neato can make in between scans and still return an accurate map - this is currently a 0.2 turn for the Neato.
* `updateEstimatePose`: The new changes are added to the map.
* `drawScan`: Once the transformations are completed and the map contains updated data, the map is redrawn to reflect the new changes. 

####HectorMappingRos
This is a .cpp file where the different files and headers we have just talked about are actually called and implemented. This file has a few main areas: 

* `scanCallback`: Function to continuously call and read the laser scan data.
* `publishMap`: Function that accesses the current map and levels. This uses a mutex to check if the map is currently locked or unlocked, so it is not being simultaneously read and written to.
* `rosLaserScanToDataContainer`: This takes the map information from the previous function and scales the laser scan data appropriately for each level of resolution.
* `rosPointCloudToDataContainer`: Sends the point cloud generated from the laser scan to a data container.
* `setServiceGetMapData`: Sets the size of each map and corresponding data container through scaling by resolution.
* callbacks: Multiple callback functions to continue the entire process while ROS is running and receiving scan data. 

###Our Implementation Plans
We hope to touch these files, rewriting the code in Python:

- `ScanMatcher.h`
- `MapRepMultiMap.h`
- `OccGridMapBase.h`
- `HectorMappingRos.cpp`
- `HectorSlamProcessor.h`
