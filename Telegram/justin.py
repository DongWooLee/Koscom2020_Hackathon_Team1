import telegram
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import ChatAction
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests 
import json
import pandas as pd
from bs4 import BeautifulSoup
import logging
import emoji
import schedule
import time
import threading
import pymysql

# JSON data read
with open ('./stock_data.json',encoding = 'UTF-8') as json_file:
    json_data = json.load(json_file)
    json_data_2 = json_data['stock']['dataValues']

# make table using stock_data.json file
info_table = []
for idx,info in enumerate(json_data_2):
    code = info['stock_number']
    code_name = info['stock_name']
    price = info['stock_price']
    info_table.append([])
    info_table[idx].append(idx)
    info_table[idx].append(code)
    info_table[idx].append(price)
    info_table[idx].append(code_name)
# print(info_table)
    
# Active Bot with the token
token = "1461066934:AAHQLhV3b7PJ-EJX-JNJdYv0tz2fZBnWmhs"
bot = telegram.Bot(token)

# updater 
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

## for SQL
# justin_db = pymysql.connect(      ## for justin local
#     user='root', 
#     passwd = 'dhsh8955', 
#     host='127.0.0.1', 
#     db='1jo', 
#     charset='utf8'
# )
justin_db = pymysql.connect(        ## for seohee server
    user='root', 
    passwd = None, 
    host='127.0.0.1', 
    db='Hackathon_dev', 
    charset='utf8'
)
cursor = justin_db.cursor(pymysql.cursors.DictCursor)

# Pre-requirement Data for send_stock_recommendation
url = "https://finance.naver.com/item/main.nhn?code=" 
ment1 = "<<  끝투's 오늘의 추천 종목  >>\n\n"
ment = ment1
image = 'test_image_256.jpg'

# help page
# help_text1 = "<<  끝투 사용방법 안내 >>\n\n1.  /help : 도움말 페이지 \n\n"
# help_text2 = "2.  /recommend : 오늘의 추천 주식 \n\n3.  /buy : 주식구매 명령어"
# help_text3 = "\n                 ex) 3번 주식을 20개 매수하려면\
#     \n                 /buy 3 20 을 입력하세요\
#     \n\n4.  /sell : 보유주식 전량 매도\n"
# help_text4 = "\n5.  /status : 나의 주식 보유내역 조회\n"    ## U+1F604
help_text1 = "<<             끝투 사용방법 안내             >>\n\n1.  /help                :  도움말 페이지 \n\n"
help_text2 = "2.  /recommend :  오늘의 추천 주식 \n\n3.  /buy                 :  주식구매 명령어"
help_text3 = "\n                                  ex) 3번 주식을 20개 매수하려면\
    \n                                  /buy 3 20 을 입력하세요\
    \n\n4.  /sell                  :  보유주식 전량 매도\n"
help_text4 = "\n5.  /status             :   나의 보유 주식 내역조회\n"
# help_text5 = U+1F604
help_text = help_text1 + help_text2 + help_text3 + help_text4
greeting_text = "\n      끝투에 오신 것을 환영합니다!!\n\n                 powered by > koscom\n\n"

user_list = ["1437875774","1452320827","1403179813","1376368920","1465787776"] #이준형, 연서희, 이동우, 정예원, 코스콤
# user_list = ["1437875774"]
user_list2 = {"1376368920":1,"1465787776":2, "1437875774":3,"1452320827":4,"1403179813":5}

def get_user_id(num):
    return user_list2[num]
    
# Getting Stock Information from naver
def get_stock_price(code):
    result = requests.get(url+code)
    bs_obj = BeautifulSoup(result.content,"html.parser")
    no_today = bs_obj.find("p", {"class": "no_today"})
    blind = no_today.find("span", {"class": "blind"}) # 태그 span, 속성값 blind 찾기
    now_price = blind.text
    return now_price

# Getting Stock Information from koscom
def koscomPrice(code):
    headers = {'apiKey':'l7xx16014a467a924424b74e86bb2bdf86f2'}
    url = "https://sandbox-apigw.koscom.co.kr/v2/market/stocks/kospi/"+ code+ "/price"
    res = requests.get(url, headers=headers)
    res2 = res.text
    index = res2.find('error')
    if index == -1 : 
        # print("kospi stock")
        json_data = res.json()
        json_data2 = json_data["result"]
        json_data3 = json_data2["trdPrc"]
    else : 
        # print("kosdaq stock")
        headers = {'apiKey':'l7xx16014a467a924424b74e86bb2bdf86f2'}
        url = "https://sandbox-apigw.koscom.co.kr/v2/market/stocks/kosdaq/"+ code+ "/price"
        res = requests.get(url, headers=headers)
        json_data = res.json()
        json_data2 = json_data["result"]
        json_data3 = json_data2["trdPrc"]
    return json_data3     

# # to update info_table which stores recommended stock infos
def update_info_table():
    for info in info_table:
        code = info[1]
        info[2] = koscomPrice(code)

# # to update json_data_2 which stores recommended stock infos
def update_json_data_2_table():
    for info in json_data_2:
        code = info['stock_number']
        info['stock_price'] =  koscomPrice(code)

# make stock name as same length with each other
def equalizer(a):
    gong = ""
    for i in range (9-a):
        gong = gong + "  "
    return gong    

# update 'recommends table' in db to current stock price
def update_db_current_price(price,code):
    sql = " update recommends set currentPrice = {} where stockNumber = {} ; ".format(price, code)
    cursor.execute(sql)
    justin_db.commit() 

# make 'ment' for sending telegram
def send_stock_recommendation(json_data_2,user_id):
    now = time.localtime()
    url = "https://finance.naver.com/item/main.nhn?code=" 
    ment1 = "<<            끝투's 오늘의 추천 종목             >>\n\n"
    ment2 =  "                         -- 현재시각 : %04d/%02d/%02d %02d:%02d:%02d\n\n" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    ment = ment1 + ment2
    for idx,info in enumerate(json_data_2):
        code = info['stock_number']
        code_name = info['stock_name']
        name_len_a = len(code_name)   #### + equalizer(name_len_a)
        #getting koscom price
        price = koscomPrice(code)
        update_db_current_price(price,code) ##### for yewon
        price = str(price)
        price = price.rjust(8)
        url_with_code = url + code
        updated_url = "[" + code_name + "]" + "(" + url_with_code + ")"
        buy_page = "> [매수클릭](http://3.34.3.203:8000/home/top10)"
        temp = str(idx+1) + '.  '  + updated_url +  '    가격 '+ ':' + price + '원    ' + buy_page +'\n\n'   ####you can use get_stock_price(code) for the price
        ment = ment + temp
    # send message to users     
    bot.sendMessage(chat_id = user_id,text = ment, parse_mode = 'Markdown',disable_web_page_preview=True)

# Defalult Greeting to all members
for user_id in user_list:   
    bot.send_photo(chat_id  = user_id, photo = open(image, 'rb'))
    bot.sendMessage(chat_id = user_id, text  = greeting_text)
    bot.sendMessage(chat_id = user_id, text  = help_text)    

# help page    
def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text= help_text)
    print(update.effective_chat.id)

start_handler = CommandHandler('help', help)
dispatcher.add_handler(start_handler)

# send stock_recommendation
def recommend(update, context):
    send_stock_recommendation(json_data_2,update.effective_chat.id)

start_handler = CommandHandler('recommend', recommend)
dispatcher.add_handler(start_handler)

#for priodical report
def report():
    for user_id in user_list:
        send_stock_recommendation(json_data_2,user_id)

# start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# sub-function for 'buy' function. 
def find_matching_stock_number(user_choice):
    return info_table[int(user_choice)-1][1]

# sub-function for 'buy' function. 
def find_matching_stock_price(user_choice):
    return info_table[int(user_choice)-1][2]

# sub-function for 'buy' function. 
def find_matching_stock_name(user_choice):
    return info_table[int(user_choice)-1][3]

# status page    
def status(update, context):
    justin_db.commit()
    user_id = get_user_id(str(update.effective_chat.id))
    ##======== stuats sql start =========## 
    sql = " select balance from accounts where userId = {} and bankName = 'project'; ".format(user_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    if result == None :
        stored_money = 0
    else : 
        stored_money = result['balance']
    status_text = "<<    1. 나의 끝투 계좌 잔액내역    >>\n\n"
    status_text = status_text + "  - 계좌 잔액 : [" + str(stored_money) + "]\n\n<<    2. 나의 주식 보유내역    >>\n\n"   
    ##======== stuats sql start =========## 
    sql = " select stockNumber,stockName,stockPrice,stockAmount from stocks where userId = {}; ".format(user_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    
    if result == None :
        context.bot.send_message(chat_id=update.effective_chat.id, text= "고객님이 보유한 주식이 없습니다.")
    else: 
        cursor.execute(sql)
        result = cursor.fetchall()
        profit_mother = 0
        profit_child = 0
        gross_profit_mother = 0
        gross_profit_child = 0
        for idx, info in enumerate(result):
            number = info['stockNumber']
            name = info['stockName']
            old_price = info['stockPrice']
            price = koscomPrice(number)
            amount = info['stockAmount']
            profit_child = price*amount
            profit_mother = old_price*amount
            gross_profit_child = gross_profit_child + profit_child
            gross_profit_mother = gross_profit_mother + profit_mother
            profit = (float) ((profit_child/profit_mother)*100-100)
            status_text = status_text +'  - 종목명 : ['+name+'],  수량 : ['+str(amount)+']개, 현재가격 : ['+str(price)+']원\n                          총['+str(amount*price)+']원,  수익률 : [' + str(round(profit,2))+']% \n\n' 
    ##======== stauts sql  end  =========## 
        #status_text = "<< 나의 주식 보유내역 >>\n\n" + status_text 
        gross_profit = (float) ((gross_profit_child/gross_profit_mother)*100-100)
        status_text2= "==========================================\n\n"+ "                          총 수익률 : [" + str(round(gross_profit,2)) + "]% 입니다. \n"
        context.bot.send_message(chat_id=update.effective_chat.id, text= status_text+status_text2)
        


start_handler = CommandHandler('status', status)
dispatcher.add_handler(start_handler)

# buy operation
def buy(update, context):
    user_want = update.message.text
    buy_commend,user_choice,user_quantity = user_want.split()
    user_stock_name = find_matching_stock_name(user_choice)
    user_stock_number = find_matching_stock_number(user_choice)
    user_stock_price = koscomPrice(user_stock_number)
    # user_stock_price = find_matching_stock_price(user_choice)
    # print(str(update.effective_chat.id))
    user_id = get_user_id(str(update.effective_chat.id))
    # print(user_id)
    buy_text1 = "["
    buy_text2 = "] 주식을 ["
    buy_text3 = "원]에 ["
    buy_text4 = "]개 매수 하였습니다."
    buy_text5 = "\n계좌 잔액 : ["
    ##========= [start] change Account Balance and Stock Amount with sql ===========## 
    sql = " select balance from accounts where userId = {} and bankName = 'project'; ".format(user_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    if result == None :
        sql = " "
    else : 
        stored_money = result['balance']
        required_money = int(user_stock_price)*int(user_quantity)
    #start
    if result == None :
        context.bot.send_message(chat_id=update.effective_chat.id, text="끝투 계좌가 없습니다.")
    elif stored_money < required_money : 
        fail_text1 = "끝투 계좌 잔고가 부족합니다.\n계좌 잔고 : ["
        fail_text2 = "필요 금액 : ["
        context.bot.send_message(chat_id=update.effective_chat.id, text= fail_text1 + str(stored_money) +"]\n"+fail_text2+str(required_money)+"]\n")
    else :
        stored_money = result['balance']
        required_money = int(user_stock_price)*int(user_quantity)
        ## seconed : make account balance decreased
        sql = " update accounts set balance = balance - {} where userId = {} and bankName = 'project'; ".format(required_money,user_id)
        cursor.execute(sql)
        justin_db.commit() 
        sql = "insert into stocks(stockNumber, stockName, stockPrice, stockAmount,userId,marketCode) values ('{}','{}',{},{},{},'kospi' );".format(user_stock_number,user_stock_name,user_stock_price,user_quantity,user_id)
        cursor.execute(sql)
        justin_db.commit() 
    ##========= [ end ] change Account Balance and Stock Amount with sql ===========##
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                text=buy_text1+user_stock_name+buy_text2+str(user_stock_price)+buy_text3+user_quantity+buy_text4+buy_text5+str(stored_money-required_money)+"원]\n")
        user_response_data = {
        "response": {
            "dataValues": [
                {
                "stock_number": user_stock_number,
                "stock_quantity" : user_quantity
                }
            ]
        }
        }
        with open("user_response.json", "w", encoding = "UTF-8") as json_file:
            json.dump(user_response_data, json_file, indent=4, sort_keys=True)

start_handler = CommandHandler('buy', buy)
dispatcher.add_handler(start_handler)

# sell operation
def sell(update, context):
    user_id = get_user_id(str(update.effective_chat.id))
    ##======== sell sql start =========## 
    sql = " select stockNumber,stockName,stockPrice,stockAmount from stocks where userId = {}; ".format(user_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    sell_text = ""
    if result == None :
        context.bot.send_message(chat_id=update.effective_chat.id, text= "매도할 주식이 없습니다.")
    else: 
        cursor.execute(sql)
        result = cursor.fetchall()
        profit_mother = 0
        profit_child = 0
        gross_profit_mother = 0
        gross_profit_child = 0
        for idx, info in enumerate(result):
            number = info['stockNumber']
            name = info['stockName']
            old_price = info['stockPrice']
            price = koscomPrice(number)
            amount = info['stockAmount']
            profit_child = price*amount
            profit_mother = old_price*amount
            gross_profit_child = gross_profit_child + profit_child
            gross_profit_mother = gross_profit_mother + profit_mother
            profit = (float) ((profit_child/profit_mother)*100-100)
            sell_text = sell_text +'['+name+'] 주식 ['+str(amount)+']개를 ['+str(price)+']원에 매도하였습니다.\n' 
            sell_text = sell_text + '                          총['+str(amount*price)+']원,  수익률 : [' + str(round(profit,2))+']% \n\n' 
            ## make account balance increased
            sql = "update accounts set balance = balance + {} where userId = {} and bankName = 'project';".format(price*amount, user_id)
            cursor.execute(sql)
            justin_db.commit()
            ## make Stock Amount decreased
            sql = "delete from stocks where userId = {} and stockNumber = {} ;".format(user_id,number)
            cursor.execute(sql)
            justin_db.commit()
    ##======== sell sql  end  =========## 
        sell_text = "보유하고 있는 주식을 모두 매도하였습니다.\n\n<< 매도 내역 >>\n\n" + sell_text 
        gross_profit = (float) ((gross_profit_child/gross_profit_mother)*100-100)
        sell_text2= "==========================================\n\n"+ "                          총 수익률 : [" + str(round(gross_profit,2)) + "]% 입니다. \n"
        context.bot.send_message(chat_id=update.effective_chat.id, text= sell_text+sell_text2) 


start_handler = CommandHandler('sell', sell)
dispatcher.add_handler(start_handler)


#for scheduler
schedule.every(1000).seconds.do(report)
def priodical_stock_data_report(interval):
    while True:
        schedule.run_pending()
        time.sleep(10) 

#for multi-threading (periodic_sending, and continous watchdog for query)
t = threading.Thread(target = priodical_stock_data_report, args=(30,))
t.start()

#for query watchdog 
while True:
    updater.start_polling(timeout=3, clean=False)
    updater.idle()
    time.sleep(1)
    