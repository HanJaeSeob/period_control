


import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style='darkgrid',color_codes=True)

class prediction_model():
    def __init__(self, tmax, phi):

        self.tmax=tmax
        self.phi=phi

    def calculate_residual(self, predicted_data, real_data, phi):
        Residual = (predicted_data - real_data)**phi
        return Residual
    
    def calculate_twait(self, tmax, Residual):
        twait=int(np.ceil(tmax/(1+abs(Residual))))
        return twait

    def visualize(self, data, sampData, sampIdxes, visualizeLength):
        appxData=np.zeros(np.size(data))*np.nan


        sampIdxes=np.where(sampIdxes[:visualizeLength]==1)[0]
        for prevt, postt in zip(sampIdxes, sampIdxes[1:]):
            if postt-prevt==1:
                appxData[prevt]=sampData[prevt]
            else:
                slope=(sampData[postt]-sampData[prevt])/(postt-prevt-1)
                appxData[prevt:postt]=((np.array(range(prevt,postt))-prevt)*slope)+sampData[prevt]
	


