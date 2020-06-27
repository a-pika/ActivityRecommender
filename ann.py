from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import GridSearchCV,RandomizedSearchCV
from sklearn.preprocessing import MinMaxScaler

# Function to create model, required for KerasClassifier
def create_model(inputs,outputs,activation='relu',neurons=12,dropout=0.0):
    model = Sequential()
    model.add(Dense(neurons, input_dim=inputs, activation=activation))
    model.add(Dropout(dropout))
    model.add(Dense(outputs, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy']) 
    return model

# fit ann model with hyperparameter optimization
def fitANNModelWithHPO(xydata,scaler,batch_size,epochs,activation,neurons,dropout,search_rounds,cv_split):
    X0 = xydata.X
    X = scaler.transform(X0)
    
    y = xydata.y_ann
    inputs = len(X[0])
    outputs = len(y[0])
    
    model = KerasClassifier(build_fn=create_model,inputs=inputs,outputs=outputs,verbose=0)
    param_grid = dict(dropout=dropout,batch_size=batch_size,epochs=epochs,activation=activation,neurons=neurons)
    
    #grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1, cv=3)#n_jobs=-1 - use all cores, a bug
    grid = RandomizedSearchCV(estimator=model, param_distributions=param_grid, n_iter=search_rounds, n_jobs=1, cv=cv_split, refit='True')
    
    grid_result = grid.fit(X,y)
    
    print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
    
    return grid_result.best_estimator_


