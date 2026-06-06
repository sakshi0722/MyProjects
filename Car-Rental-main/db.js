const mongoose = require("mongoose");

const mongoURL = "mongodb://127.0.0.1:27017/car-rental";

mongoose.connect(mongoURL);

const connection = mongoose.connection;

connection.on("connected", () => {
    console.log("Mongo DB Connection Successful");
});

connection.on("error", () => {
    console.log("Mongo DB Connection Error");
});

module.exports = mongoose;