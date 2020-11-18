import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pykrx
from pykrx import stock as st
from datetime import datetime
import datetime as dt
import os
from scipy.cluster.vq import vq, kmeans, whiten
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
import random
import json
from collections import OrderedDict
import pickle
from catboost import CatBoostClassifier
import zerorpc


class StockAI(object):
    def __init__(self):
        self.date_list = []
        self.df_list = []
        self.get_stock_list()
        self.get_kospi_stock_list()
        self.get_kosdaq_stock_list()
        #self.get_weekly_list()
        self.rf_list = []
        self.cb_list = []
        self.goal_list = []
        self.train_with_random_forest()

    def generate_train_data(self, n, left_date, right_date, train_len, result_len, code_list):
        x_list = []
        y_closing_list = []
        y_highest_list = []

        while True:
            if len(x_list) == n:
                break

            duration = (datetime.strptime(right_date, '%Y%m%d') - datetime.strptime(left_date, '%Y%m%d')).days
            rand_offset = random.randrange(0, duration)

            start_date = datetime.strptime(left_date, '%Y%m%d') + dt.timedelta(days=rand_offset)
            end_date = (start_date + dt.timedelta(days=(train_len + result_len) * 2)).strftime("%Y%m%d")
            start_date = start_date.strftime("%Y%m%d")
            rand_code = code_list[random.randrange(0, len(code_list))]
            price_data = st.get_market_ohlcv_by_date(start_date, end_date, rand_code)

            if len(price_data['종가']) < train_len + result_len:
                continue

            closing_price_norm = price_data['종가'] / np.max(price_data['종가'][:train_len])
            highest_price_norm = price_data['고가'] / np.max(price_data['종가'][:train_len])

            train_data = closing_price_norm[:train_len]
            raw_closing_data = closing_price_norm[train_len:train_len + result_len]
            raw_highest_data = highest_price_norm[train_len:train_len + result_len]

            x_list.append(train_data)
            y_closing_list.append(raw_closing_data)
            y_highest_list.append(raw_highest_data)

        x_list = np.array(x_list)
        y_closing_list = np.array(y_closing_list)
        y_highest_list = np.array(y_highest_list)

        return x_list, y_closing_list, y_highest_list

    # Crawling이 되지 않아, 파일로 대체함
    def get_stock_list(self):
        self.stock_list = pd.read_csv("data/market.csv")


    def get_kospi_stock_list(self):
        self.kospi_stock_list = pd.read_csv("data/kospi_market.csv")


    def get_kosdaq_stock_list(self):
        self.kosdaq_stock_list = pd.read_csv("data/kosdaq_market.csv")


    ##  전체 데이터를 얻어오는데 시간이 오래걸리므로, 파일로 받아온 다음 Load하기 위한 코드
    def get_weekly_data(self):
        path = "WeeklyData/"
        for f in os.listdir(path):
            print (f)
            final_path = path + f
            if not f.__contains__('.csv'):
                continue
            df = pd.read_csv(final_path)
            if len(df) > 20:
                for i in range(len(df)):
                    c_origin = df['차트(원본)'][i][1:-1].split()
                    c_origin = [float(j) for j in c_origin]
                    df['차트(원본)'][i] = c_origin
                    t_origin = df['종가(원본)'][i][1:-1].split()
                    t_origin = [float(j) for j in t_origin]
                    df['종가(원본)'][i] = t_origin
                    h_origin = df['고가(원본)'][i][1:-1].split()
                    h_origin = [float(j) for j in h_origin]
                    df['고가(원본)'][i] = h_origin
                    c = df['차트'][i][1:-1].split()
                    c = [float(j) for j in c]
                    df['차트'][i] = c
                    t = df['종가'][i][1:-1].split()
                    t = [float(j) for j in t]
                    df['종가'][i] = t
                    h = df['고가'][i][1:-1].split()
                    h = [float(j) for j in h]
                    df['고가'][i] = h
                self.date_list.append(f.split('.csv')[0])
                print (f)
                self.df_list.append(df)

    ## RandomForest를 통한 학습 진행
    def train_with_random_forest(self):
        y_highest_list = np.load("data/y_highest_list.npy")
        x_list = np.load("data/x_list.npy")

        ## 수익률 0.5%에서 15.5%까지 0.5%단위로 모델을 따로 학습시킨다.
        for i in range(0, 31):
            goal = 0.005 + (0.005 * i)
            y_list = []
            print(goal)
            for k, item in enumerate(y_highest_list):
                ## 다음 5일의 고가 기준으로 수익률 이상인 순간이 있다면 이는 수익을 달성한 것이다.
                y_list.append(int(np.max(item) >= (1 + goal) * x_list[k][-1]))

            y_list = np.array(y_list)
            rf = RandomForestClassifier(n_estimators=100, oob_score=True, random_state=123456)
            rf.fit(x_list, y_list)
            self.goal_list.append(goal)
            self.rf_list.append(rf)

        print ("Random Forest Train Completed")


    ## Catboost를 통한 학습 진행
    def train_with_catboost(self):
        y_highest_list = np.load("data/y_highest_list.npy")
        x_list = np.load("data/x_list.npy")

        for i in range(0, 31):
            goal = 0.005 + (0.005 * i)
            y_list = []
            print(goal)
            for k, item in enumerate(y_highest_list):
                y_list.append(int(np.max(item) >= (1 + goal) * x_list[k][-1]))

            y_list = np.array(y_list)
            cb = CatBoostClassifier(iterations=10000, learning_rate=1, depth=2)
            cb.fit(x_list, y_list)
            self.cb_list.append(cb)

        print("Catboost Train Completed")

    ## 위에서 학습한 모델을 기준으로(현재는 RandomForest) 1117자 기준 추천 종목을 뽑는다.
   def get_recommend_list(self):
        #today_df = get_price_data_with_day(today, 20)
        today = "20201117"
        today_df = pd.read_csv('today.csv')

        ##12.5%의 수익률로 학습된 모델
        rf = self.rf_list[24]
        test_x = np.array(today_df['차트'].tolist())
        test_y = rf.predict(test_x)

        t_idx = np.reshape(np.argwhere(test_y == 1), -1)

        for idx in t_idx:
            stock_name = today_df['종목명'][idx]
            market_type = self.get_market_name(stock_name)
            print (market_type)
            prob = rf.predict_proba(test_x)[idx][1]
            if prob < 0.55:
                continue

            buy_price = int(today_df['차트(원본)'][idx][-1])
            print('{' + today_df['종목명'][idx] + "}를 " + str(today) + "20201117에 " + str(buy_price) + "원에 매수")

            stock_code = self.stock_list[self.stock_list['Name'] == stock_name]['Code']

            for idx, v in stock_code.items():
                stock_code = stock_code[idx]

    ## 특정종목이 어떤 시장에 속했는지 정보 반영
    def get_market_name(self,stock_name):
        if len(self.kospi_stock_list[self.kospi_stock_list["Name"] == stock_name]):
            return "kospi"
        elif len(self.kosdaq_stock_list[self.kosdaq_stock_list["Name"] == stock_name]):
            return "kosdaq"
        else:
            return "konex"


if __name__ == "__main__":
    stock = StockAI()

    ##  해당 코드를 Server로 돌리기 위한 코드 (현재는 비활성화함)
    #s = zerorpc.Server(StockAI())
    #s.bind("tcp://0.0.0.0:4243")
    #s.run()

    print (stock.get_recommend_list())


