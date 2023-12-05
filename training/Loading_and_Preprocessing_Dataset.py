# Import libraries
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings
import tensorflow as tf
warnings.filterwarnings('ignore')
import pandas as pd
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
#from sklearn.cross_validation import train_test_split
#import tensorflow as the backend for Keras
from keras import backend as K
K.image_data_format() # sostituito a --> K.set_image_dim_ordering()
from keras.utils import to_categorical # sostituito a --> from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten #sostituito a --> from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D as Convolution2D, MaxPooling2D #sostituito a --> from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD, RMSprop, Adam as adam #sostituto a --> from keras.optimizers import SGD,RMSprop,adam
from keras.callbacks import TensorBoard
# Import required libraries for cnfusion matrix
from sklearn.metrics import classification_report,confusion_matrix
import itertools

from keras.models import load_model

import pickle


#--------------------------------------------------------------


PATH = os.getcwd()
# Define data path
data_path = './dataset'
data_dir_list = os.listdir(data_path)
print(data_dir_list)


#--------------------------------------------------------------


img_rows=128
img_cols=128
num_channel=1
num_epoch=20
num_classes = 2
img_data_list=[]
for categories in data_dir_list:
	img_list=os.listdir(data_path+'/'+ categories)
	num_img = len([f for f in os.listdir(data_path+'/'+ categories) if os.path.isfile(os.path.join(data_path+'/'+ categories, f))])
	print ('Caricate',num_img,'immagini della categoria '+'{}\n'.format(categories))
	for img in img_list:
		input_img=cv2.imread(data_path + '/'+ categories + '/'+ img )
		input_img=cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
		input_img_resize=cv2.resize(input_img,(128,128))
		img_data_list.append(input_img_resize)

img_data = np.array(img_data_list)
img_data = img_data.astype('float32')
img_data /= 255.0
print (img_data.shape)


#--------------------------------------------------------------


if num_channel==1:
	if K.image_data_format()=='th': #K.image_dim_ordering()=='th':
		img_data= np.expand_dims(img_data, axis=1) 
		print (img_data.shape)
	else:
		img_data= np.expand_dims(img_data, axis=3) 
		print (img_data.shape)
		
else:
	if K.image_dim_ordering()=='th':
		img_data=np.rollaxis(img_data,3,1)
		print (img_data.shape)


#--------------------------------------------------------------


#Assegna nomi e numero di classi
num_classes = 2
num_of_samples = img_data.shape[0]
labels = np.ones((num_of_samples,),dtype='int64')
labels[0:99]=0
labels[100:199]=1
names = ['automobile', 'gatto']


#--------------------------------------------------------------


# convert class labels to on-hot encoding
Y = to_categorical(labels, num_classes) #np_utils.to_categorical(labels, num_classes)


#--------------------------------------------------------------


#Shuffle and Split the dataset
x,y = shuffle(img_data,Y, random_state=2)
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=2)


#--------------------------------------------------------------


print("X_train shape = {}".format(X_train.shape))
print("X_test shape = {}".format(X_test.shape))


#--------------------------------------------------------------


image = X_train[159,:].reshape((img_rows,img_cols))
#plt.imshow(image)
#plt.show()


#-------------------------------------------------------------- #2. Designing and training a CNN model in Keras


#Initialising the input shape
input_shape = img_data[0].shape
# Design the CNN Sequential model
cnn_model = Sequential()
cnn_model.add(Convolution2D(32, (3, 3), padding='same', activation='relu', input_shape=input_shape))
cnn_model.add(Convolution2D(32, (3, 3), activation='relu'))
cnn_model.add(MaxPooling2D(pool_size=(2, 2)))
cnn_model.add(Dropout(0.5))
cnn_model.add(Flatten())
cnn_model.add(Dense(128, activation='relu'))
cnn_model.add(Dropout(0.5))
cnn_model.add(Dense(num_classes, activation='softmax'))


#--------------------------------------------------------------


cnn_model.compile(loss='categorical_crossentropy', optimizer='adadelta', metrics=["accuracy"])

cnn_model.summary()

# Fit the model to the training data
hist = cnn_model.fit(X_train, y_train, batch_size=16, epochs=num_epoch, verbose=1, validation_data=(X_test, y_test))

# Retrieve the training and validation loss
train_loss = hist.history['loss']
val_loss = hist.history['val_loss']
train_acc = hist.history['accuracy']
val_acc = hist.history['val_accuracy']
xc = range(num_epoch)

#devo salvare il modello in un file da poter poi caricare per fare le predizioni
cnn_model.save('./model/SeeBeyond.h5')

with open('./model/variabili.pkl', 'wb') as file:
    pickle.dump((X_test, y_test), file)
