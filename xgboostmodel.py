from numpy import asarray
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from keras.utils import np_utils

class XYdata:
    def __init__(self):
        self.X = []
        self.y = []
        self.y_ann = []
        self.dataXCat = []
        self.dataY = []
    
    def getXY(self,resourcesTS,taskSet):

        
        for i in range(0,len(resourcesTS)):
             for j in range(0,len(resourcesTS[i].trainData)):
                 self.dataXCat.append(resourcesTS[i].trainData[j].features)
                 self.dataY.append(getTaskIndex(taskSet,resourcesTS[i].trainData[j].nextTask))
        
        self.X = asarray(self.dataXCat)
        self.y = asarray(self.dataY)
        self.y_ann = np_utils.to_categorical(self.dataY)
        
        return(self)

# fit xgboost model 
def fitModel(xydata):
    model = XGBClassifier()
    model.fit(xydata.X, xydata.y)
    
    return model


def getTaskIndex(taskSet,task):
    taskIndex = 0
    
    for i in range(0,len(taskSet)):
        if taskSet[i] == task:
            taskIndex = i
            break
    
    return taskIndex