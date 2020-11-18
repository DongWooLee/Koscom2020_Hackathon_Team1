const { User } = require("../models");
const moment = require('moment');

const getSignup = (req, res) => {
    res.render('signup');
}

const postSignup = async (req, res) => {
    const {name, userId, password} = req.body;
    try{
        const date = moment().format('YYYY-MM-DD');

        await User.create({
            name: name,
            userId: userId,
            password: password,
            transferDate: date
        }).then(user => {
            req.session.user = {
                id: 3,//user.dataValues.id,
                name: '코스콤', //user.dataValues.name
            };
        });
        res.redirect('/home');
    }catch(error){
        console.error(error);
        return next(error);
    }
};



module.exports = {
    postSignup,
    getSignup
};