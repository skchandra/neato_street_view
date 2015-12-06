// server.js

// Generate a new instance of express server.
var express = require('express'), 
	http = require('http'),
    sqlite3 = require('sqlite3').verbose(),
    db = new sqlite3.Database('data.db');

var app = express();

app.use(express.static(__dirname + '/images'));

var port = process.env.PORT || 5000;
var host = process.env.HOST || "127.0.0.1";

// Starts the server itself
var server = http.createServer(app).listen(port, host, function() {
  console.log("Server listening to %s:%d within %s environment",
              host, port, app.get('env'));
});

// At the root of your website, we show the index.html page
app.get('/', function(req, res) {
  res.sendfile('./public/index.html')
});
