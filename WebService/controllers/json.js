
const json = (req, res) => {
    const json= require('./stock_data_2.json');
    res.json(json);
    
}

const kospi = async (req, res, next ) => {

    var url = 'https://sandbox-apigw.koscom.co.kr/v2/market/multiquote/stocks/{marketcode}/price'.replace(/{marketcode}/g, encodeURIComponent('kospi'));
    const queryParams = url + '?' +  encodeURIComponent('apikey') + '=' + encodeURIComponent('l7xx16014a467a924424b74e86bb2bdf86f2');
    
    var request=require('request');
    await request(queryParams, (err, response, obj) => {
        if(!err&&response.statusCode==200){
            const parsed = JSON.parse(obj);
            res.json(parsed.isuLists);
        }
    })
}

const kosdaq = async (req, res, next) => {

    let url = 'https://sandbox-apigw.koscom.co.kr/v2/market/multiquote/stocks/{marketcode}/lists'.replace(/{marketcode}/g, encodeURIComponent('kosdaq'));
    const queryParams = url + '?' +  encodeURIComponent('apikey') + '=' + encodeURIComponent('l7xx16014a467a924424b74e86bb2bdf86f2');
    
    var request=require('request');
    await request(queryParams, (err, response, obj) => {
        if(!err&&response.statusCode==200){
            const parsed = JSON.parse(obj);
            res.json(parsed.isuLists);
        }
    })
}

const purchase = (req, res, next) => {
    Stock.findAll({
        where: {
            userId: req.session.user.id
        }
    }).then(stock => {
        res.json(stock);
    });
}

module.exports = {
    json,
    kospi,
    kosdaq,
    purchase
}