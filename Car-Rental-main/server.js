const express = require("express");
const app = express();
const db = require("./db");

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/api/users', require('./routes/usersRoute'));

const port = 5000;

app.listen(port, () => {
  console.log(`Node JS Server Started in Port ${port}`);
});