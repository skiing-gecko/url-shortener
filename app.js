const express = require('express');

const bodyParser = require('body-parser');

const path = require('path');
const app = express();

app.use(express.static(path.join(__dirname, '/static')));
app.use(bodyParser.urlencoded({ extended: false }));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '/static/index.html'));
});

app.post('/', (req, res) => {
  console.log(req.body.urlInput);
  res.send('OK');
});

module.exports = app;
