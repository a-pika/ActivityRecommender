import csv
from features import Event

def getMax(vals):
    maxVal = 0
    for i in range(0,len(vals)):
        if vals[i] > maxVal:
            maxVal = vals[i]
    return maxVal


def loadLog(logPath):
    with open(logPath, newline='') as f:
        reader = csv.reader(f)
        logData = list(reader)
    return logData

def getLogStart(events):
    return events[0].time

def saveResultsInCSV(results_out,lines):
    with open(results_out,'w', newline='') as result_file:
        wr = csv.writer(result_file, dialect='excel')
        wr.writerows(lines)
        
def getAvg(vals):
    avg = -1
    sum = 0
    for i in range(0,len(vals)):
        sum = sum + vals[i]

    if len(vals) > 0:
        avg = sum/len(vals)

    return avg