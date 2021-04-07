
from flask import Flask, request, url_for, redirect
from werkzeug import secure_filename
import pandas as pd
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt

import time
import datetime

class data_generation():
    
    def __init__(self, tot_info, base_time, remain_list, model_input_list, target):

        self.tot_info = tot_info
        self.base_time = base_time
        self.remain_list = remain_list
        self.model_input_list = model_input_list
        self.target = target


    def GW_dataset_gen(self, tot_info, base_time, remain_list):
        

        time = pd.to_datetime(tot_info['time'])
        tot_info['time'] = time
        data_list = []
        for i in remain_list:
            data_list.append(tot_info[tot_info['id']==i])


        data_list_columns = list(data_list[0].columns)

        temp_data_set = []
        for i in range(len(data_list)):
            temp_data_set.append(pd.DataFrame(np.array(data_list[i]), columns = data_list_columns))



        base_time = datetime.datetime.strptime(base_time, "%Y-%m-%d %H:%M")
        base_index = temp_data_set[0][temp_data_set[0]['time'] == base_time].index.tolist()[0]
        now_dataset = {}
        
        for i in range(len(temp_data_set)):
            now_dataset[remain_list[i]] = temp_data_set[i].iloc[: base_index+1]

        GW_now_data = []
        scaler = MinMaxScaler(feature_range=(0, 1))
        for i in remain_list:
            for j in model_input_list:
                GW_now_data.append(now_dataset[i][j])
        GW_now_data = np.array(GW_now_data)
        GW_now_nptf = gen_nptf(GW_now_data)
        return GW_now_data, GW_now_nptf



    def period_parameter_extraction(self, remain_list, model_input_list, target):
        remain_list = np.copy(remain_list)
        non_target_list = np.delete(remain_list, np.where(np.array(remain_list) == target)[0][0])
        target_index = {}
        for i, id in enumerate(remain_list):
            target_index[id] = i


        GW_target_index = 4*target_index[target]


        target_sen_index = {} 
        for i, sensor in enumerate(model_input_list):
            target_sen_index[sensor] = i
        return GW_target_index, remain_list, target_index, target_sen_index

