const app = require('./app.js');

const BASE_URL = '127.0.0.1';
const PORT = 8080;

app.listen(PORT, BASE_URL, () => {
  console.log(`Listening on port ${PORT}`);
});
