from datetime import datetime

class Event:
    def __init__(self, case, task, resource, time, duration, data):
        self.case = case
        self.task = task
        self.resource = resource
        self.time = time
        self.duration = duration
        self.data = data


class Features:
    def __init__(self):
        self.featureTaskSeq = []
        self.featureTaskFreq = []
        self.featureTaskDur = []
        self.featureDataSet = [] #list of lists
        self.featureDataFreq = [] #list of lists
        self.featureDataAvg = [] #one value per data variable
    
    def getTaskFeatures(self,events,tasks):
        
        for i in range(0,len(tasks)):
            self.featureTaskSeq.append(0)
            self.featureTaskFreq.append(0)
            self.featureTaskDur.append(0.0)
        
        for i in range(0,len(tasks)):
            t = tasks[i]
            tcount = 0
            tdur = 0.0
            tseq = 0
            
            for j in range(0,len(events)):
                ev = events[j]
                if ev.task == t:
                    tcount = tcount + 1
                    tdur = tdur + ev.duration
            
            avgTdur = 0.0
            if tcount > 0:
                avgTdur = tdur/tcount
                tseq = 1
                
            self.featureTaskSeq[i] = tseq
            self.featureTaskFreq[i] = tcount
            self.featureTaskDur[i] = avgTdur
                    
        return self
    
    def getDataFeatures(self,events,data_values,use_data,use_data_avg):
        
        for i in range(0,len(data_values)):
            self.featureDataSet.append([])
            self.featureDataFreq.append([])
            
        for k in range(0,len(data_values)):
            data_attr = data_values[k]
        
            for i in range(0,len(data_attr)):
                data_val = data_attr[i]
                dseq = 0
                dcases = []
                
                for j in range(0,len(events)):
                    ev = events[j]
                    if ev.data[use_data[k]] == data_val:
                        dseq = 1
                        if not ev.case in dcases:
                            dcases.append(ev.case)

                self.featureDataSet[k].append(dseq)
                self.featureDataFreq[k].append(len(dcases))
                    
        # continuous data feature
        for i in range(0,len(use_data_avg)):
            caseIDs = []
            avgData = []
            for j in range(0,len(events)):
                ev = events[j]
                if not ev.case in caseIDs:
                    caseIDs.append(ev.case)
                    avgData.append(float(ev.data[use_data_avg[i]]))
            dataSum = 0.0
            for j in range(0,len(avgData)):
                dataSum = dataSum + avgData[j]
                
            avgDataVal = -1.0
            
            if len(avgData) > 0:
               avgDataVal = dataSum/len(avgData)
               
            self.featureDataAvg.append(avgDataVal)
        
        return self


class Resource:
    def __init__(self,resName,resEvents,resStart,resEnd,isGeneralist,isNew):
        self.resName = resName
        self.resEvents = resEvents
        self.resNewEvents = [] #events related to first activity executions
        self.resStart = resStart
        self.resEnd = resEnd
        self.isGeneralist = isGeneralist #1 true, 0 - false
        self.isNew = isNew #1 true, 0 - false
    
    def populateNewEvents(self):
        usedTasks = []
        for i in range(0,len(self.resEvents)):
            if self.resEvents[i].task not in usedTasks:
                self.resNewEvents.append(self.resEvents[i])
                usedTasks.append(self.resEvents[i].task)
        return self
    
    def setGeneralist(self,mintasks):
        if len(self.resNewEvents) >= mintasks:
            self.isGeneralist = 1
        else:
            self.isGeneralist = 0
        return self
    
    def setNew(self,logStart,mindays):
        daysFromStart = self.resStart - logStart
        
        if daysFromStart.days >= mindays:
            self.isNew = 1
        else:
            self.isNew = 0
        return self
    
    def printResNumTasks(self):
        print(self.resName)
        print(len(self.resNewEvents))
    
    def printResource(self):
        print("{}, {}, {}, {}".format(self.resName, len(self.resEvents), self.resStart, self.resEnd))
        print("Gen: {}, New: {}".format(self.isGeneralist,self.isNew))
        newTasks = []
        newTimes = []
        for i in range(0,len(self.resNewEvents)):
            newTasks.append(self.resNewEvents[i].task)
            newTimes.append(self.resNewEvents[i].time)
        print(newTasks)
        
        for i in range(0,len(newTimes)):
            print(newTimes[i].strftime("%Y-%m-%d %H:%M:%S"))

class TrainDataTS:
    def __init__(self,curTS,nextTask):
        self.curTS = curTS
        self.nextTask = nextTask #one task, for each task with same ts separate object
        self.featureTaskSeq = [] 
        self.featureTaskFreq = [] 
        self.featureTaskDur = [] 
        self.featureDataSet = [] #list of lists - per data attr.
        self.featureDataFreq = [] #list of lists - per data attr.
        self.featureDataAvg = []
        self.features = [] #concatenated selected features

    def printTrainDataTS(self):
        print(self.curTS)
        print(self.nextTask)
        print(self.featureTaskSeq)
        print(self.featureTaskFreq)
        print(self.featureTaskDur)
        print(self.featureDataSet)
        print(self.featureDataFreq) 
        print(self.featureDataAvg)
        print(self.features)
        
    def concatSelectedfeatures(self,use_features):
        
        if use_features[0] == 1:
           self.features = self.features + self.featureTaskSeq
        
        if use_features[1] == 1:
           self.features = self.features + self.featureTaskFreq
           
        if use_features[2] == 1:
           self.features = self.features + self.featureTaskDur
        
        if use_features[3] == 1:
            for i in range(0,len(self.featureDataSet)):
               self.features = self.features + self.featureDataSet[i] 
        
        if use_features[4] == 1:
            for i in range(0,len(self.featureDataFreq)):
               self.features = self.features + self.featureDataFreq[i] 

        if use_features[5] == 1:
           self.features = self.features + self.featureDataAvg
           
        return self
        
        
class ResourceTS:
    def __init__(self,resource,ts):
        self.resource = resource
        self.ts = ts
        self.resName = resource.resName
        self.hasPrev = 0
        self.hasNext = 0
        self.nextTask = [] #>1 if same time
        self.prevResEvents = []
        self.prevNewResEvents = []
        
        #features - test
        self.featureTaskSeqTest = []
        self.featureTaskFreqTest = []
        self.featureTaskDurTest = []
        self.featureDataSetTest = [] #list of lists
        self.featureDataFreqTest = [] #list of lists
        self.featureDataAvgTest = []
        self.features = [] #list of selected features concatenated
        
        #features - train
        self.trainData = [] 
    
    def getNumFeatures(self):
        return len(self.features)
    
    def printResourceTS(self):
        print("{}, {}, {}, {}, {}, {}".format(self.resName, self.ts, len(self.prevResEvents), self.hasPrev, self.hasNext, self.nextTask))
        print(self.featureTaskSeqTest)
        print(self.featureTaskFreqTest)
        print(self.featureTaskDurTest)
        print(self.featureDataSetTest)
        print(self.featureDataFreqTest)
        for i in range(0,len(self.prevNewResEvents)):
            print(self.prevNewResEvents[i].task)

    def populateResourseTS(self):
        for i in range(0,len(self.resource.resEvents)):
            if self.resource.resEvents[i].time < self.ts:
                self.prevResEvents.append(self.resource.resEvents[i])
        
        for i in range(0,len(self.resource.resNewEvents)):
            if self.resource.resNewEvents[i].time < self.ts:
                self.prevNewResEvents.append(self.resource.resNewEvents[i])
        
        prevEvSize = len(self.prevResEvents)
        
        nextTime = self.ts
        rHasNew = 0
        
        for i in range(0,len(self.resource.resNewEvents)):
            if self.resource.resNewEvents[i].time >= self.ts:
                nextTime = self.resource.resNewEvents[i].time
                rHasNew = 1
                break
        
        if rHasNew > 0:
            for i in range(0,len(self.resource.resNewEvents)):
                if self.resource.resNewEvents[i].time == nextTime:
                    self.nextTask.append(self.resource.resNewEvents[i].task)
                    #print(self.resource.resEvents[i].time)
        
        if prevEvSize > 0:
            self.hasPrev = 1
            
        if len(self.nextTask) > 0:
            self.hasNext = 1
        
        return self
    
    def populateResFeaturesTest(self,tasks,data,use_data,use_data_avg):
        
        features = Features()
        features = features.getTaskFeatures(self.prevResEvents,tasks)
        features = features.getDataFeatures(self.prevResEvents,data,use_data,use_data_avg)
        
        self.featureTaskSeqTest = features.featureTaskSeq
        self.featureTaskFreqTest = features.featureTaskFreq
        self.featureTaskDurTest = features.featureTaskDur
        self.featureDataAvgTest = features.featureDataAvg
        
        for i in range(0,len(data)):
            self.featureDataSetTest.append(features.featureDataSet[i])
            self.featureDataFreqTest.append(features.featureDataFreq[i])
       
        return self
    
    def populateResFeaturesTrain(self,tasks,data,use_data,min_tasks,use_features,use_data_avg):
        
        if len(self.prevNewResEvents) > min_tasks:
            for j in range(min_tasks,len(self.prevNewResEvents)):
                curTS = self.prevNewResEvents[j].time
                nextTask = self.prevNewResEvents[j].task
                curTsPrevEvents = []
                for k in range(0,len(self.prevResEvents)):
                    if self.prevResEvents[k].time < curTS:
                       curTsPrevEvents.append(self.prevResEvents[k]) 
                
                if len(curTsPrevEvents) > 0:                
                    trainDataTS = TrainDataTS(curTS,nextTask) 
            
                    features = Features()
                    features = features.getTaskFeatures(curTsPrevEvents,tasks)
                    features = features.getDataFeatures(curTsPrevEvents,data,use_data,use_data_avg)
                    
                    trainDataTS.featureTaskSeq = features.featureTaskSeq
                    trainDataTS.featureTaskFreq = features.featureTaskFreq
                    trainDataTS.featureTaskDur = features.featureTaskDur
                    trainDataTS.featureDataAvg = features.featureDataAvg
                    
                    for i in range(0,len(data)):
                        trainDataTS.featureDataSet.append(features.featureDataSet[i])
                        trainDataTS.featureDataFreq.append(features.featureDataFreq[i])
           
                    trainDataTS = trainDataTS.concatSelectedfeatures(use_features)
                    
                    self.trainData.append(trainDataTS)
            
        return self
    
    def concatSelectedTestfeatures(self,use_features):
        
        if use_features[0] == 1:
           self.features = self.features + self.featureTaskSeqTest
        
        if use_features[1] == 1:
           self.features = self.features + self.featureTaskFreqTest
           
        if use_features[2] == 1:
           self.features = self.features + self.featureTaskDurTest
        
        if use_features[3] == 1:
            for i in range(0,len(self.featureDataSetTest)):
               self.features = self.features + self.featureDataSetTest[i] 
        
        if use_features[4] == 1:
            for i in range(0,len(self.featureDataFreqTest)):
               self.features = self.features + self.featureDataFreqTest[i] 

        if use_features[5] == 1:
           self.features = self.features + self.featureDataAvgTest
        
        return self

def getResource(res,events):
    rEvents = []
    
    for i in range(0,len(events)):
        if events[i].resource == res:
            rEvents.append(events[i])
          
    rStart = rEvents[0].time
    rEnd = rEvents[len(rEvents)-1].time
    
    resource = Resource(res,rEvents,rStart,rEnd,0,0)
    
    return resource


def getEvents(logdata):   
    
    events = []
    
    for i in range(0,len(logdata)):
        ev = logdata[i]
        case = ev[0]
        task = ev[1]
        resource = ev[2]
        time = datetime.strptime(ev[3],"%d/%m/%Y %H:%M:%S")
        duration = float(ev[4])
        data = []
        for j in range(5,len(ev)):
            data.append(ev[j])
        e = Event(case,task,resource,time,duration,data)
        events.append(e)
    
    return events

def getSetOfResources(events):
    resources = []
    for i in range(0,len(events)):
        ev = events[i]
        res = ev.resource
        if not res in resources:
            resources.append(res)
    
    return resources

def getSetOfTasks(events):
    tasks = []
    for i in range(0,len(events)):
        ev = events[i]
        task = ev.task
        if not task in tasks:
            tasks.append(task)
    
    return tasks

def getTrainResources(resources,useGeneralists):
    train_resources = []
    if useGeneralists == 0:
        for i in range(0,len(resources)):
            train_resources.append(resources[i])
    else:
        for i in range(0,len(resources)):
            if resources[i].isGeneralist == 1:
                train_resources.append(resources[i])
                
    return train_resources
            
def getTestResources(resources,useGeneralists,useNew):
    test_resources = []
    
    if useGeneralists == 0 and useNew == 0:
        for i in range(0,len(resources)):
            test_resources.append(resources[i])
    elif useGeneralists > 0 and useNew == 0:
        for i in range(0,len(resources)):
            if resources[i].isGeneralist == 1:
                test_resources.append(resources[i])
    elif useGeneralists == 0 and useNew > 0:
        for i in range(0,len(resources)):
            if resources[i].isNew == 1:
                test_resources.append(resources[i])
    else:
        for i in range(0,len(resources)):
            if resources[i].isNew == 1 and resources[i].isGeneralist == 1:
                test_resources.append(resources[i])
                
    return test_resources            
            
def getSetOfDataValues(events,data_index):
    data_values = []
    for i in range(0,len(events)):
        ev = events[i]
        data_val = ev.data[data_index]
        if not data_val in data_values:
            data_values.append(data_val)
    
    return data_values            
            
            
            
            
       
            
            
            
            
            
            
            
            
            
            
            
    
    
    
    