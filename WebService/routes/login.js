const express = require("express");
const router = express.Router();

const {start, login} = require('../controllers/login');

router.get('/', start);
router.post('/login', login);

module.exports = router;