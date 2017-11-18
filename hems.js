const express = require('express')
fs = require('fs')

const app = express()

static_content = null;

fs.readFile('page.html', 'utf8', function (err,data) {
  if (err) {
    return console.log(err);
  }
  static_content = data;
});

app.get('/', (req, res) => {
	console.log("Got request");
	res.send(static_content);
});
app.listen(3000, () => console.log('Service started on port 3000!'))
