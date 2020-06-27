from utils import getMax,loadLog,getLogStart,saveResultsInCSV,getAvg
from features import Event,Resource,ResourceTS,getTrainResources,getTestResources
from features import getEvents,getResource,getSetOfResources,getSetOfTasks
from features import getSetOfDataValues
from evaluation import getTestResourcesTS
from datetime import datetime,timedelta
from sklearn.metrics import accuracy_score
import numpy
from xgboostmodel import XYdata,fitModel
from ann import fitANNModelWithHPO
from sklearn.preprocessing import MinMaxScaler
from configuration import *

#1.1 - read the log from csv (events sorted by time)
logdata = loadLog(log)

#1.2 - transform log data into a list of Event objects
#mandatory: case,task,resource,time,duration
#optional: list of data attributes
events = getEvents(logdata)

#1.3 - log start
logStart = getLogStart(events)

#2.1 - get a set of resources
resourceSet = getSetOfResources(events)

#2.2 - create a list of Resource objects
resources = []

for i in range(0,len(resourceSet)):
    resources.append(getResource(resourceSet[i],events))

for i in range(0,len(resources)):
    resources[i] = resources[i].populateNewEvents()
    if use_generalists > 0:
        resources[i] = resources[i].setGeneralist(use_generalists)
    if use_new_resources > 0:
        resources[i] = resources[i].setNew(logStart,use_new_resources)


#3.1 - get a list of resources for training (all/generalists)
trainResources = getTrainResources(resources,use_generalists)

#3.2 - get a set of all tasks
taskSet = getSetOfTasks(events)
    
#3.3 - get sets of values for each data attribute
data_values = []
for i in range(0,len(use_data)):
    data_values.append(getSetOfDataValues(events,use_data[i]))

#3.4 - create array for storing results
lines = []
title = ['min_tasks','min_tasks_test','use_generalists','use_new_resources',
         'taskSet','taskFreq','taskDur','dataSet','dataFreq','dataAvg',
         'dataAttrCat','dataAttrAvg','timeSplit','numTrainR','numTestR',
         'confidence_threshold','Recommendations','Accuracy']
lines.append(title)

for si in range(0,len(splits)):
    splitDays = splits[si]
    timeSplit = logStart + timedelta(days=splitDays)
    print(timeSplit)
    
    #4.0 - populate csv line
    line = []
    line.append(min_tasks)
    line.append(min_tasks_test)
    line.append(use_generalists)
    line.append(use_new_resources)
    line.append(use_features[0])
    line.append(use_features[1])
    line.append(use_features[2])
    line.append(use_features[3])
    line.append(use_features[4])
    line.append(use_features[5])
    
    used_dataAttr = 'usedCatData-'
    for ai in range(0,len(use_data)):
        used_dataAttr = used_dataAttr + str(use_data[ai])+'-'
    line.append(used_dataAttr)
    
    used_dataAttrAvg = 'usedNumData-'
    for ai in range(0,len(use_data_avg)):
        used_dataAttrAvg = used_dataAttrAvg + str(use_data_avg[ai])+'-'
    line.append(used_dataAttrAvg)

    line.append(splitDays)
    
    #4.1 - create a list of ResourceTS objects
    resourcesTS = []
    for i in range(0,len(trainResources)):
        newResTS = ResourceTS(trainResources[i],timeSplit)
        newResTS = newResTS.populateResourseTS()
        resourcesTS.append(newResTS)

    #4.2 - populate test & train features 
    for i in range(0,len(resourcesTS)):
        resourcesTS[i] = resourcesTS[i].populateResFeaturesTest(taskSet,data_values,use_data,use_data_avg)
        resourcesTS[i] = resourcesTS[i].populateResFeaturesTrain(taskSet,data_values,use_data,min_tasks,use_features,use_data_avg)

    #5.1 get xyData
    xyDataTS = XYdata()
    xyDataTS = xyDataTS.getXY(resourcesTS,taskSet)
    
    #5.2 data scaling 
    scaler = MinMaxScaler()
    scaler.fit(xyDataTS.X)
    
    #5.3 get model
    model = None
    
    if use_ml_model == 0:
       model = fitModel(xyDataTS)
    else:
       model = fitANNModelWithHPO(xyDataTS,scaler,batch_size,epochs,activation,neurons,dropout,search_rounds,cv_split)
 
    #6.1 get test resources
    testResourcesTS = getTestResourcesTS(resourcesTS,min_tasks_test)
    print("#numTrain: {}".format(len(resourcesTS)))
    print("#numTest: {}".format(len(testResourcesTS)))
    
    line.append(len(resourcesTS))
    line.append(len(testResourcesTS))
    
    #6.2 - transform test features into ml input
    for ri in range(0,len(testResourcesTS)):
        testResourcesTS[ri] = testResourcesTS[ri].concatSelectedTestfeatures(use_features)
    
    for cth in range(0,len(confidence_thresholds)):
        current_threshold = confidence_thresholds[cth]
        current_line = []
        for li in range(0,len(line)):
            current_line.append(line[li])
        recommendations = []
        accuracies = []
   
        for ri in range(0,len(testResourcesTS)):
            X0 = numpy.array(testResourcesTS[ri].features).reshape((1,-1))
            Xr = X0
            if use_ml_model == 1:        
                Xr = scaler.transform(X0)
            
            #6.3 - get prediction
            rPred = model.predict(Xr)
            predTask = taskSet[rPred[0]]
            rProb = model.predict_proba(Xr)
            maxProb = getMax(rProb[0])
        
            #6.4 - compare predicted and real value
            realTasks = testResourcesTS[ri].nextTask
            if maxProb >= current_threshold:
                recommendations.append(1) 
                if predTask in realTasks:
                    accuracies.append(1) 
                else:
                    accuracies.append(0)
            else:
                recommendations.append(0) 
        
      
        #6.5 - record avg results for test resources at ts
        avgRecommendations = getAvg(recommendations)
        avgAccuracy = getAvg(accuracies)
        print(avgRecommendations)
        print(avgAccuracy)
    
        current_line.append(current_threshold)
        current_line.append(avgRecommendations)
        current_line.append(avgAccuracy)
        lines.append(current_line)
 
#7. write configuration and results in csv
saveResultsInCSV(results_out,lines)







