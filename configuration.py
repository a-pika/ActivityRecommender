log = 'C:\\python\\ActivityRecommender\\data\\bpic12.csv'
#log = 'C:\\python\\ActivityRecommender\\data\\bpic17_6m.csv'

results_out = 'C:\\python\\ActivityRecommender\\output\\bpic12-xgb-AO.csv'

sort_log = 1 #0 - no, 1 - yes
use_ml_model = 0 #0 - xgboost, 1 - nn

# [AO,AF,AD,DO,DF,DA] 
use_features = [1,0,0,0,0,0]  
#indexes of data attributes to be used (in 'data' array)
use_data = [] #categorical vars
use_data_avg = [] #continuous vars

splits = [60,90,120,150]
confidence_thresholds = [0.0,0.25,0.5,0.75]

min_tasks = 1 # > 0  
min_tasks_test = 5 # > 0
use_generalists = 0 
use_new_resources = 0 

#NN
search_rounds = 50
batch_size = [10,20,40,60,100]
epochs = [50,100,150,200,300]
activation = ['relu','sigmoid','tanh']
neurons = [20,30,50,100,150,200,300,400,500]
dropout = [0.0,0.1,0.2,0.3]
cv_split = 3 