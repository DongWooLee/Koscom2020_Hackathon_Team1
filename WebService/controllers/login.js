const { User } = require("../models");

const start = (req, res) => {
    res.render('login');
};

const login = async(req, res, next) => {
    const {userId, password} = req.body;

    User.findOne({
        where: {
            userId : userId,
            password: password
        }
    }).then(user => {
        console.log(user);
        console.log(user.dataValues);
        req.session.user = {
            id: 3,//user.dataValues.id,
            name:'코스콤', //user.dataValues.name
        };
        res.redirect('/home');
    }).catch((error) => {
        console.error(error);
        next(error);
    });
}


module.exports = {
    start,
    login
};