const { User, Account, Stock, Recommend } = require("../models");

const Sequelize = require('sequelize');
const { render } = require("pug");
const { renameSync } = require("fs");
const env = process.env.NODE_ENV || 'development';
const config = require('../config/config')[env];
const sequelize = new Sequelize(
    config.database, config.username, config.password, config,
);

const home = async (req, res, next) => {
    // console.log(req.session.user);
    await Account.findAll({
        where: {
            userId : 3//1//req.session.user.id
        }
    }).then(accounts => {
        console.log(accounts);
        res.render('home', {
            userName: '코스콤',//req.session.user.name,
            accounts: accounts
        });
    }).catch(error => {
        console.error(error);
        next(error);
    });
};

const setting = async (req, res, next) => {
    await User.findOne({
        where: {
            id : 3//,req.session.user.id
        }
    }).then(user => {
        // console.log(user);
        res.render('setting', {
            user : user
        });
    }).catch(error => {
        console.log(error);
        next(error);
    });
    
}

const postSetting = async (req, res, next) => {
    const {amount, date, period, profits} = req.body;

    console.log("profits: \n" + profits);
    await User.update({
        transferAmount : parseInt(amount),
        transferPeriod: parseInt(period),
        transferDate: date,
        expectedProfits: parseInt(profits)
    },{
        where: {
            id: 3//req.session.user.id
        }
    }).then(user =>{
        res.redirect('/home/setting');
    }).catch(error => {
        console.log(error);
        next(error);
    });
}

const top10 = async (req, res) => {
    Recommend.findAll().then(rec => {
        console.log(rec);
        res.render('top10', {
            data: rec
        });
    })
    
}
const buyForm = (req, res) => {
    const {stock_name, stock_number, stock_price, stock_percent, market_code} = req.body;
    console.log("market_code: " + market_code);
    res.render('buy', {
        stock_name: stock_name, 
        stock_number: stock_number,
        stock_price: stock_price,
        stock_percent: stock_percent,
        market_code: market_code
    });
}

const report = async(req, res, next) => {
    let query = "" + "select stockName, sum(stockAmount) as 'stockAmount', avg(stockPrice) as 'stockPrice' from stocks  where userId=3 group by stockName";
    await sequelize.query(query, 
        { type: Sequelize.QueryTypes.SELECT}
    ).then((stocks)=>{
        res.render('report', {
            stocks: stocks
        })
    })
}

const buy = async(req, res, next) => {
    const {stock_name, stock_number, stock_price, amount,market_code} = req.body;
    await Stock.create({
        stockNumber: stock_number,
        stockName: stock_name,
        stockPrice: Number(stock_price),
        stockAmount: Number(amount),
        userId: 3,//eq.session.user.id,
        marketCode: market_code
    }).then(async() => {
        await Account.findOne({
            where: {
                userId: 3,//1,
                bankName: "project"
            }
        }).then((account) => {
                console.log(account);
                var balance = account.dataValues.balance-stock_price*amount;
                Account.update({
                    balance : balance
                }, {
                    where: {
                        userId: 3,//req.session.user.id,
                        bankName: "project"
                    }
                });
        });
    }).then(() => {
        res.redirect('/home/report');
    }).catch(error => {
        console.error(error);
        return next(error);
    });
}

module.exports = {
    home,
    setting,
    postSetting,
    top10,
    buyForm,
    buy,
    report
};