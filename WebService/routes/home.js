const express = require("express");
const router = express.Router();

const {home, setting, postSetting, top10, buyForm, buy, report} = require('../controllers/home');
const {Stock} = require('../models');

router.get('', home);
router.get('/setting', setting);
router.post('/setting', postSetting);
router.get('/top10', top10);
router.post('/buyForm', buyForm);
router.post('/buy', buy);



router.get('/report', report);



module.exports = router;