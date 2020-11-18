const express = require("express");
const router = express.Router();

const loginRouter = require('./login');
const homeRouter = require('./home');
const signupRouter = require('./signup');
const jsonRouter = require('./json');

router.use('/home', homeRouter);
router.use('/', loginRouter);
router.use('/signup', signupRouter);
router.use('/json', jsonRouter);

module.exports = router;