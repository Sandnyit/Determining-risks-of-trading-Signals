#Basic Mathematics and data manipulation libraries
import numpy as np
import pandas as pd

#Librarires for plotting
import matplotlib.pyplot as plt
import seaborn as sns

#CNN libraries
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

#Evaluation libraries
from sklearn.metrics import classification_report,confusion_matrix,precision_score,accuracy_score,recall_score,f1_score

from warnings import filterwarnings

#Mentioning labels
labels = ['glioma_tumor','meningioma_tumor','pituitary_tumor','no_tumor'] 

#Callbacks
def callbacks(save_name):
    early = EarlyStopping(monitor='val_accuracy', patience=3, verbose=1)
    checkpoint = ModelCheckpoint(save_name,monitor="val_accuracy",save_best_only=True,mode="auto",verbose=1)
    lr = ReduceLROnPlateau(monitor = 'val_accuracy', factor = 0.3, patience = 2, min_delta = 0.001,
                                  mode='auto',verbose=1)
    return early,checkpoint,lr

#Training Top Layer
def model(model_name,epoch,early,checkpoint,lr,X_train,y_train):
    his = model_name.fit(X_train,y_train,validation_split=0.1, epochs =epoch, verbose=1, batch_size=32,callbacks=[early,checkpoint,lr])
    return his


#Plotting Accuracy
def accuracy (his,epoch, name):
    
    fig, ax = plt.subplots(1,2,figsize=(14,7))
    fig.text(s='Training and Validation Accuracy and Loss of '+name+'.',size=18,fontweight='bold',color='#00008B',y=1,x=0.28,alpha=0.8)

    #sns.despine()
    ax[0].plot(his.history['accuracy'], color='#FF4040',label = 'Training')
    ax[0].plot(his.history['val_accuracy'], color='#0000FF',label = 'Validation')
    ax[0].legend(frameon=False)
    ax[0].set_xlabel('Epochs')
    ax[0].set_ylabel('Accuracy')

    #sns.despine()
    ax[1].plot(his.history['loss'], color='#FF4040',label ='Training')
    ax[1].plot(his.history['val_loss'],color='#0000FF',label = 'Validation')
    ax[1].legend(frameon=False)
    ax[1].set_xlabel('Epochs')
    ax[1].set_ylabel('Loss')

    fig.show()


#Prediction
def prediction(model_name,X_test,y_test):
    pred = model_name.predict(X_test)
    pred = np.argmax(pred,axis=1)
    y_test_new = np.argmax(y_test,axis=1)
    print(classification_report(y_test_new,pred,target_names=labels))
    return y_test_new, pred


#Confusion Matrix
def confusion(y_test_new, pred, name):
    cm = confusion_matrix(y_test_new, pred)

    fig = plt.figure(figsize=(12, 8))
    fig.text(s='Confusion Matrix of '+name+'.',size=18,fontweight='bold',color='#00008B',y=1,x=0.28,alpha=0.8)
    
    ax= plt.subplot()
    sns.heatmap(cm, annot=True, ax = ax, fmt = 'g',cmap='YlGnBu',linecolor='grey',linewidths=2, cbar=False); 

    ax.xaxis.set_label_position('bottom')
    plt.xticks()
    ax.xaxis.set_ticklabels(labels, fontsize = 10)
    ax.xaxis.tick_bottom()

    ax.yaxis.set_ticklabels(labels, fontsize = 10)
    plt.yticks(rotation=0)

    plt.show()


#Training model

def train(model_name,save_name,epoch,name,X_train,y_train,X_test,y_test,labels=labels):
    early,checkpoint,lr=callbacks(save_name)
    history=model(model_name,epoch,early,checkpoint,lr,X_train,y_train)
    accuracy(history,epoch,name)
    pred,y_test_new=prediction(model_name,X_test,y_test)
    confusion(y_test_new,pred,name)

#Adding Layers 
def layers(pretrained_model):
    model_name = pretrained_model.output
    model_name = tf.keras.layers.GlobalAveragePooling2D()(model_name)
    model_name = tf.keras.layers.Dropout(rate=0.5)(model_name)
    model_name = tf.keras.layers.Dense(4,activation='softmax')(model_name)
    model_name = tf.keras.models.Model(inputs=pretrained_model.input, outputs = model_name)
    
    model_name.compile(loss='categorical_crossentropy',optimizer = 'Adam', metrics= ['accuracy'])
    
    return model_name




