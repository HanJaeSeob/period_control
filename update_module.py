
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

class update_module():
    def __init__(self, model, GW_now_data, GW_now_nptf, ID, h,pm2_5,pm10_0, t, remain_list, GW_target_index, 
        target_sen_index, temp_value, twait, target, target_index, tmax, phi):

        self.model = model
        self.GW_now_data = GW_now_data
        self.GW_now_nptf = GW_now_nptf
        self.ID = ID
        self.h = h
        self.pm2_5 = pm2_5 
        self.pm10_0 = pm10_0 
        self.t = t 
        self.remain_list = remain_list
        self.GW_target_index = GW_target_index
        self.target_sen_index = target_sen_index
        self.temp_value = temp_value
        self.twait = twait
        self.target = target
        self.target_index = target_index
        self.tmax = tmax
        self.phi = phi



    def GW_imputation(model, GW_now_data, GW_now_nptf, ID, h,pm2_5,pm10_0, t, 
                      remain_list, GW_target_index, target_sen_index, temp_value, twait,target, target_index):
        scaler = MinMaxScaler(feature_range=(0, 1))


        data_interval = 32
        prediction_val = model.predict(GW_now_nptf[:,-data_interval:].reshape(1,len(GW_now_nptf),data_interval))[0]
            

        impu_sen_list = [] 
        for i in model_input_list:
            impu_sen_list.append(GW_target_index+ target_sen_index[i])
        restored_prediction = []
        for i in impu_sen_list:
            temp_scaler = scaler.fit_transform(GW_now_data[i].reshape(-1,1))
            restored_prediction.append(scaler.inverse_transform(prediction_val[i].reshape(-1,1))[0][0])

        restored_prediction = np.array(restored_prediction).reshape(len(restored_prediction),1)
        temp_value[impu_sen_list[0]:impu_sen_list[-1]+1] = restored_prediction
        if target in remain_list:
            remain_list.remove(target)

        temp_value[4*target_index[ID]:4*target_index[ID]+4] = np.array([h,pm2_5,pm10_0,t]).reshape(4,1)
        if ID in remain_list:
            remain_list.remove(ID)
        if len(remain_list) == 0:
            GW_now_data = np.hstack((GW_now_data,temp_value))
            GW_now_nptf = gen_nptf(GW_now_data)
            twait = twait - 1

        return GW_now_data, GW_now_nptf, temp_value, twait    


    def GW_period_control(model, GW_now_data, GW_now_nptf, ID, h,pm2_5,pm10_0, t, remain_list,tmax,phi,temp_value,temp_twait, target, target_index, target_sen_index, target_sen, GW_target_index):
        
        import prediction_model
        
        prediction_model=prediction_model.prediction_model(tmax=tmax,phi=phi)

        scaler = MinMaxScaler(feature_range=(0, 1))
        tmax = 5
        phi = 2

        if ID == target:

            data_interval = 32
            prediction_val = model.predict(GW_now_nptf[:,-data_interval:].reshape(1,len(GW_now_nptf),data_interval))[0]
            

            impu_sen_list = [] 
            for i in model_input_list:
                impu_sen_list.append(GW_target_index+ target_sen_index[i])
                

            prediction_data_for_target_node = []
            for i in impu_sen_list:
                temp_scaler = scaler.fit_transform(GW_now_data[i].reshape(-1,1))
                prediction_data_for_target_node.append(scaler.inverse_transform(prediction_val[i].reshape(-1,1))[0][0])
            prediction_data_for_target_node = np.array(prediction_data_for_target_node).reshape(len(prediction_data_for_target_node),1)

            target_prediction = prediction_data_for_target_node[target_sen_index[target_sen]][0]
            

            temp_value[impu_sen_list[0]:impu_sen_list[-1]+1] = np.array([h,pm2_5,pm10_0,t]).reshape(4,1)
            

            real_val = temp_value[target_sen_index[target_sen]][0]
            


            
            Residual = prediction_model.calculate_residual(target_prediction, real_val, phi)
            temp_twait = prediction_model.calculate_twait(tmax,Residual)
            if ID in remain_list:
                remain_list.remove(ID)
            else:
                print('.......... retransmission..............')
                print('target node {} retransmission'.format(ID))

            twait = temp_twait
            
        else:

            temp_value[4*target_index[ID]:4*target_index[ID]+4] = np.array([h,pm2_5,pm10_0,t]).reshape(4,1)
            twait = 1
            if ID in remain_list:
                remain_list.remove(ID)
            else:
                print('.......... retransmission..............')
                print('node {} retransmission'.format(ID))


        if len(remain_list) == 0:
            GW_now_data = np.hstack((GW_now_data,temp_value))
            GW_now_nptf = gen_nptf(GW_now_data)

        return GW_now_data, GW_now_nptf, twait, temp_value, remain_list, temp_twait


        