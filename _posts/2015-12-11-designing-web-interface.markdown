---
layout: post
title:  Developing a Web Interface!
date:   2015-12-11 17:30:25
categories: blog
---

##Developing a Web Interface

Hi everyone! This is Kiki and I’m here to talk about my work from the past week and a half, setting up a site for visitors to view our map and interact with the panoramas. I initially started out using Flask for Python with SQLite3, and developed a basic app that displayed the map. To host the application, we planned to use Heroku; however, from doing research online it we learned that if we ran the free version of Heroku with only one dyno, and used SQLite3 rather than its built-in Postgres, the database would clear itself once every 24 hours. We also found that many users experienced many bugs and complications when using these two technologies together; as a result, we decided to move to developing a Node.js application with SQLite3, and host it on Modulus. 
Through the Node.js backend, the application creates an instance of a server and connects to a database. The database contains the filepath to each panorama, accessible through each picture’s x-coordinate, y-coordinate, and theta (viewing angle). This third field is when the user is actually interacting with the panorama - when they move left or right, different images will be displayed. 
The actual visualization happens through the frontend HTML and JavaScript. We have a basic floorplan map of CC300 (it is a placeholder map, so it is very imprecise) which has multiple waypoints that a user can click on to see more about that area: 
![Image]({{ site.url }}/images/dr2/website1.png)
Once the user clicks on a waypoint, a panorama (shown below) fills the screen:
![Image]({{ site.url }}/images/dr2/website2.png)
The user can then move left or right to view a 360-degree of the room. 
As of now, I did not integrate the database with the visual display, so the image path is being changed through the JavaScript. Our next steps include making this shift so that our website file storage is cleaner, and so we can integrate the working SQL code to read from a database and display images. Another area we are planning to work further on is the user interface - we would like to give the panorama more of a 3D feeling by allowing users to also move up and down, as well and zoom in and out to create the appearance of moving forwards or backwards. If we have time, we would also like to move from using buttons to a more intuitive click and drag interface, and work on making the transition between photos smoother. 
That’s all we have for now on the web interface, but check back next week for a link to the website to test it out yourself!
