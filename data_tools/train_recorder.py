import os
import numpy as np
import pandas as pd
import re

from sklearn.model_selection import train_test_split
import tensorflow.keras as keras
import warnings
warnings.filterwarnings("ignore")

activity={'guohang':0,'dijin':1,'zhencha':2,'yanxi':3,'xunlian':4}

names = os.listdir('./train_data')
print(len(names))
X,y=[],[]
for dir in names:
    data=pd.read_csv('./train_data/'+dir)
    dir=dir.split('.csv')[0]
    label=re.split('\d+$',dir)[0]

    data=data.values[1:]
    temp_X=np.zeros((10,6))
    i=0
    while data[i][0]==0 and data[i][2]==0 and data[i][4]==0 and i<len(data)-1:
        i+=1
    # print(i)
    for j in range(min(len(temp_X),len(data)-i)):
        temp_X[j]=(data[i+j])
    X.append(temp_X)

    y.append(activity[label])
# y = np_utils.to_categorical(y,num_classes= 5)
X= np.array(X, dtype = float).reshape(len(names),10,6,1)
y= np.array(y,dtype=int)
# print(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)


print('x_train.shape:',X_train.shape)
print('y_train.shape:',y_train.shape)

model = keras.Sequential()
# 第一层卷积，卷积核数为128，卷积核3x3，激活函数使用relu，输入是每张原始图片64x64*1
model.add(keras.layers.Conv2D(128, kernel_size=3, activation='relu', input_shape=(10, 6, 1)))
# 第一池化层
model.add(keras.layers.MaxPool2D((2, 2), strides=2))

# # 第二层卷积，卷积核数为64，卷积核3x3，激活函数使用relu
# model.add(keras.layers.Conv2D(64, kernel_size=3, activation='relu'))
# # 第二池化层
# model.add(keras.layers.MaxPool2D((2, 2), strides=2))

#把多维数组压缩成一维，里面的操作可以简单理解为reshape，方便后面全连接层使用
model.add(keras.layers.Flatten())
#对应cnn的全连接层，40个人对应40种分类，激活函数使用softmax，进行分类
model.add(keras.layers.Dense(5, activation='softmax'))


model.compile(optimizer='adam',loss='sparse_categorical_crossentropy', metrics=['accuracy'])

model.fit(X_train, y_train, epochs=10)
y_predict = model.predict(X_test)
# 打印实际标签与预测结果
model.evaluate(X_test,y_test)
# print(y_test[0], np.argmax(y_predict[0]))
for i in range(len(y_test)):
    print(y_test[i],np.argmax(y_predict[i]))

model.save('ABM_model.h5')  
# model = models.load_model('my_model.h5')
