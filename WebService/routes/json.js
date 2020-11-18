const express = require("express");
const router = express.Router();
const {json, kospi, kosdaq, purchase} = require('../controllers/json');


router.get('', json);
router.get('/kospi', kospi);
router.get('/kosdaq', kosdaq);
router.get('/purchse', purchase);


module.exports = router;

