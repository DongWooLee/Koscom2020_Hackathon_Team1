const express = require('express');
const morgan = require("morgan");
const path = require('path');
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const sessionParser = require('express-session');
const indexRouter = require('./routes/index');
const sequelize = require('./models').sequelize;

const app = express();

sequelize.sync();

const session = sessionParser({
    secret: "Hackathon",
    resave: true,
    saveUninitialized: true
});

/*
const session = sessionParser({
    secret: "Hackathon",
    resave: true,
    saveUninitialized: true
});
*/
app.set("views", path.join(__dirname, "views"));
app.set("view engine", "pug");
app.use(express.static(path.join(__dirname, 'public')));
app.use('/img', express.static(path.join(__dirname, 'uploads')));
app.use(cookieParser());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(morgan("dev"));
app.use(session);

app.use("", indexRouter);
app.use((req, res, next) => {
    const err = new Error("Not Found");
    err.status = 404;
    next(err);
});
app.use((err, req, res) => {
    res.locals.message = err.mesage;
    res.locals.error = req.app.get("env") || "development" ? err : {};
    res.status(err.status || 500);
    res.render("error");
});


const PORT = process.env.PORT || 8000;

const handleListening = () => 
    console.log(`Listening on: ${PORT}`);

const server = app.listen(PORT,handleListening);