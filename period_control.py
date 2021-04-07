
from flask import Flask, request, url_for, redirect
from werkzeug import secure_filename
import pandas as pd
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt
import data_generation
import update_module



def updatePeriod(model, twait, remain_list, GW_now_data, GW_now_nptf, 
                 ID, h, pm2_5, pm10_0, t, GW_target_index, target_sen_index,temp_value, temp_twait,target, target_index, target_sen):

    update_module = update_module.update_module(model = model, GW_now_data = GW_now_data, GW_now_nptf = GW_now_nptf, ID = ID, h = h, pm2_5 = pm2_5, pm10_0 = pm10_0, t= t, remain_list = remain_list, GW_target_index = GW_target_index, 
    target_sen_index = target_sen_index, temp_value = temp_value, twait = twait, target = target, target_index = target_index, tmax = tmax, phi = phi)


    refer_period = 10000

    if twait != 1:
        GW_mode = 0
        if len(remain_list) == 3: 
            temp_value = np.zeros((12,1))
            
        GW_now_data, GW_now_nptf, temp_value, twait = update_module.GW_imputation(model, GW_now_data, GW_now_nptf, 
                                                                    ID, h,pm2_5,pm10_0, t, remain_list, 
                                                                    GW_target_index, target_sen_index, temp_value,twait,target, target_index)
        period = refer_period
        if len(remain_list) == 0:
            remain_list = [47,48,49]
        print("\n====================================================================================")
        
        print('GW_mode: Imputataion')
        print('ID:{} \n remain_list:{} \n twait:{}'.format(ID,remain_list,twait))
        
    else:
        GW_mode = 1
        tmax = 5
        phi = 2
        if len(remain_list) == 3: 
            temp_value = np.zeros((12,1))
            
        GW_now_data, GW_now_nptf, twait, temp_value, remain_list, temp_twait = update_module.GW_period_control(model, GW_now_data, GW_now_nptf, ID, 
                                                                             h,pm2_5,pm10_0, t, remain_list,tmax,phi,
                                                                             temp_value, temp_twait,target, target_index, target_sen_index, target_sen,GW_target_index)
        

        
        if ID == target:
            period = (twait+1)*refer_period
        else:
            period = refer_period

        if len(remain_list) == 0:
            remain_list = [47,48,49]
            twait = temp_twait
        else:
        	twait = 0

        print("\n====================================================================================")
        print('GW_mode:Period Control')
        print('ID:{} \nremain_list:{} \ntwait:{}'.format(ID,remain_list,twait))
        
       		
       		
    return period, twait, remain_list, GW_now_data, GW_now_nptf, temp_value, temp_twait



############################################################################################################
################################### Data & AI Model Loading ################################################

print (os.getcwd())
current_dir = os.path.dirname(os.path.abspath("__file__"))
try:
    TOT_EX_PATH = os.path.join(current_dir, 'dataset_for_DB_only_data.csv')

except:
    print('You should have to use file name with "modified department name". Check it')
print("TOT_EX_PATH:", TOT_EX_PATH)

model = keras.models.load_model('CNN.h5')


############################################################################################################
############################################ Initialization ################################################

dfs = pd.read_csv(TOT_EX_PATH, encoding ='utf-8')
app = Flask(__name__)
tot_info = dfs

app = Flask(__name__)
base_time = "2019-10-23 23:58"
model_input_list = ['h','pm025','pm100','t']
remain_list = [47,48,49]
temp_value = np.zeros((len(remain_list)*len(model_input_list),1))
twait = 1
temp_twait = 1
target_sen = 't'
target = 47

data_generation = data_generation.data_generation(tot_info = tot_info, base_time = base_time, remain_list = remain_list, model_input_list = model_input_list, target = target)

GW_now_data, GW_now_nptf = data_generation.GW_dataset_gen(tot_info, base_time, remain_list)


GW_target_index, remain_list, target_index, target_sen_index= data_generation.period_parameter_extraction(remain_list, model_input_list,target)



############################################################################################################
############################################ Web server ####################################################


@app.route('/')
def index():
    return 'Hello world'

@app.route('/fileUpload', methods=['GET'])
def upload_file():
    if request.method =='GET':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return 'Upload Done'

@app.route('/getdata', methods=['GET'])
def test():

    global model_input_list, twait, temp_twait, remain_list, GW_now_data, GW_now_nptf, temp_value, GW_target_index, cluster_id, target_index, target_sen_index, target_sen, target
    t = 0
    h = 0
    ID = 0
    pm2_5 = 0 
    pm10_0 = 0
    if request.method == 'GET':
        ID = request.args['id']
        t = request.args['temp']
        h = request.args['humi']
        pm2_5 = request.args['dust2_5_1']
        pm10_0 = request.args['dust10_0_1']
    
    ID = int(ID)
    t = float(t)
    h = float(h)
    pm2_5 = int(pm2_5)
    pm10_0 = int(pm10_0)




    period, twait, remain_list, GW_now_data, GW_now_nptf, temp_value, temp_twait =  updatePeriod(model, twait, remain_list, GW_now_data, GW_now_nptf, 
                 ID, h, pm2_5, pm10_0, t, GW_target_index, target_sen_index,temp_value, temp_twait,target, target_index, target_sen)
    print('period:{}ms'.format(period),'\n')
    return str(period)

if __name__ == '__main__':
    app.run(debug=False, port=8090, host='0.0.0.0')

