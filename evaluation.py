def getTestResourcesTS(resourcesTS,minTasks):
    testResTS = []
    
    for i in range(0,len(resourcesTS)):
        curRes = resourcesTS[i].resource
        minT = 0
        hasNext = 0
        
        if len(resourcesTS[i].prevNewResEvents) >= minTasks:
            minT = 1
    
        if resourcesTS[i].hasNext > 0:
            hasNext = 1
            
        if minT > 0 and hasNext > 0:
           testResTS.append(resourcesTS[i]) 
        
    return testResTS
    
