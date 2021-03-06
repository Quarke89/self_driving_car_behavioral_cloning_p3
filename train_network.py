import csv
import cv2
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Dropout, Lambda, Cropping2D
from keras.layers.convolutional import Convolution2D
from keras.layers.pooling import MaxPooling2D
from sklearn.model_selection import train_test_split
import sklearn
from random import shuffle

samples = []
with open('./data/driving_log.csv') as csvfile:
	reader = csv.reader(csvfile)
	for line in reader:
		samples.append(line)

train_samples, validation_samples = train_test_split(samples, test_size=0.2)

def generator(samples, batch_size=32):
    num_samples = len(samples)
    while 1: 
        shuffle(samples)
        for offset in range(0, num_samples, batch_size):
            batch_samples = samples[offset:offset+batch_size]

            images = []
            angles = []
            for batch_sample in batch_samples:
            	for i in range(3):
            		source_path = batch_sample[i]
            		filename = source_path.split('/')[-1]
            		current_path = './data/IMG/' + filename
            		image = cv2.imread(current_path)
            		angle = float(line[3])
            		if i == 1:
            			angle += 0.2
            		elif i == 2:
            			angle -= 0.2
            		image_flipped = np.fliplr(image)
            		angle_flipped = -angle

            		images.append(image)
            		angles.append(angle)
            		images.append(image_flipped)
            		angles.append(angle_flipped)
            
            X_train = np.array(images)
            y_train = np.array(angles)
            yield sklearn.utils.shuffle(X_train, y_train)

train_generator = generator(train_samples, batch_size=32)
validation_generator = generator(validation_samples, batch_size=32)


# images = []
# measurements = []

# for line in lines:
# 	for i in range(3):
# 		source_path = line[0]	
# 		filename = source_path.split('/')[-1]
# 		current_path = './data/IMG/' + filename
# 		image = cv2.imread(current_path)	
# 		measurement = float(line[3])
# 		if i == 1:
# 			measurement += 0.2
# 		elif i == 2:
# 			measurement -= 0.2
		
# 		image_flipped = np.fliplr(image)
# 		measurement_flipped = -measurement

# 		images.append(image)	
# 		measurements.append(measurement)
# 		images.append(image_flipped)	
# 		measurements.append(measurement_flipped)

# X_train = np.array(images)
# y_train = np.array(measurements)


model = Sequential()
model.add(Lambda(lambda x: x/255.0 - 0.5, input_shape=(160,320,3)))
model.add(Cropping2D(cropping=((70,25), (0,0))))
model.add(Convolution2D(24, 5, 5, subsample=(2,2), activation="relu"))
model.add(Convolution2D(36, 5, 5, subsample=(2,2), activation="relu"))
model.add(Convolution2D(48, 5, 5, subsample=(2,2), activation="relu"))
model.add(Convolution2D(64, 3, 3, activation="relu"))
model.add(Convolution2D(64, 3, 3, activation="relu"))
model.add(Flatten())
model.add(Dense(100))
model.add(Dense(50))
model.add(Dense(10))
model.add(Dense(1))

model.compile(loss='mse', optimizer='adam')
# model.fit(X_train, y_train, validation_split=0.2, shuffle=True, nb_epoch=5)
model.fit_generator(train_generator, samples_per_epoch=len(train_samples), validation_data=validation_generator, nb_val_samples=len(validation_samples), nb_epoch=5)

model.save('model.h5')

