const express = require("express");
const router = express.Router();

const {postSignup, getSignup} = require('../controllers/signup');


router.get('', getSignup);
router.post('', postSignup);



module.exports = router;