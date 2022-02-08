# -*- coding: utf-8 -*-
"""RESNET50.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eKw8T3iCNElqKamN-kwo-pye5vfh8z2m
"""

from google.colab import drive
drive.mount("/content/gdrive",force_remount=True)

import tensorflow as tf
import keras
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import datasets, layers, models, losses, Model

datagen = ImageDataGenerator(rotation_range=30, fill_mode='nearest')
test_generator = datagen.flow_from_directory("/content/gdrive/MyDrive/project",target_size=(224,224), batch_size=32,shuffle=True)

val_ds = tf.keras.utils.image_dataset_from_directory(
  "/content/gdrive/MyDrive/project",
  validation_split=0.2,
  subset="validation",seed=123,
  image_size=(224, 224))

train_ds = tf.keras.utils.image_dataset_from_directory(
  "/content/gdrive/MyDrive/project",
  validation_split=0.2,
  subset="training",seed=123,
  image_size=(224, 224))

val_batches = tf.data.experimental.cardinality(val_ds)
test_ds = val_ds.take(val_batches // 2)
val_ds = val_ds.skip(val_batches // 2)
print('Number of validation batches: %d' % tf.data.experimental.cardinality(val_ds))
print('Number of test batches: %d' % tf.data.experimental.cardinality(test_ds))

class_names = train_ds.class_names

plt.figure(figsize=(10, 10))
for images, labels in test_ds.take(1):
  for i in range(9):
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(images[i].numpy().astype("uint8"))
    plt.title(class_names[labels[i]])
    plt.axis("off")

base_model = tf.keras.applications.ResNet50(weights='imagenet',input_shape=(224, 224, 3),include_top=False)
for layer in base_model.layers:
  layer.trainable = False
#base_model.summary()
len(base_model.layers)

data_augmentation = keras.Sequential(
    [layers.RandomFlip("horizontal_and_vertical"), layers.RandomRotation(0.1),]
)
for image, _ in train_ds.take(1):
  plt.figure(figsize=(10, 10))
  first_image = image[0]
  for i in range(9):
    ax = plt.subplot(3, 3, i + 1)
    augmented_image = data_augmentation(tf.expand_dims(first_image, 0))
    plt.imshow(augmented_image[0] / 255)
    plt.axis('off')

inputs = tf.keras.Input(shape=(224, 224, 3))
data_augmentation = keras.Sequential([layers.RandomFlip("horizontal_and_vertical"), layers.RandomRotation(0.1),])
x = data_augmentation(inputs)
scale_layer=tf.keras.layers.Rescaling(scale=1./255)
x = scale_layer(x)
x = base_model(inputs, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = tf.keras.layers.Dense(4,activation=tf.keras.activations.softmax,kernel_regularizer=tf.keras.regularizers.L2(0.0001),bias_regularizer=tf.keras.regularizers.L2(0.0001))(x)
model = tf.keras.Model(inputs, outputs)
model.summary()

model.compile(tf.keras.optimizers.Adam(learning_rate=1e-4), loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False), metrics=['accuracy'])

history = model.fit(train_ds, batch_size=32, epochs=50, validation_data=val_ds,class_weight={0: 1.755294,
                                                                                             1: 8.227941,
                                                                                             2: 5.680203,
                                                                                             3: 7.535354})

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(8, 8))
plt.subplot(2, 1, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.ylabel('Accuracy')
#plt.ylim([0.24,0.36])
plt.title('Training and Validation Accuracy')

plt.subplot(2, 1, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.ylabel('Cross Entropy')
#plt.ylim([5.5,7.5])
plt.title('Training and Validation Loss')
plt.xlabel('epoch')
plt.show()

"""FINETUNING"""

base_model.trainable=True
# Let's take a look to see how many layers are in the base model
print("Number of layers in the base model: ", len(base_model.layers))

# Fine-tune from this layer onwards
# Freeze all the layers before the `fine_tune_at` layer
for layer in base_model.layers[:90]:
  layer.trainable =  False

model.compile(tf.keras.optimizers.Adam(learning_rate=1e-5), loss=losses.SparseCategoricalCrossentropy(from_logits=False), metrics=['accuracy'])

model.summary()

ep=20
#history_fine = model.fit(train_ds,epochs=20,initial_epoch=history.epoch[-1],validation_data=val_ds)
#model.fit(train_ds,batch_size=32,validation_data=val_ds,epochs=32)
history = model.fit(train_ds, batch_size=32, epochs=50, validation_data=val_ds,class_weight={0: 1.755294,
                                                                                             1: 8.227941,
                                                                                             2: 5.680203,
                                                                                             3: 7.535354})

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(8, 8))
plt.subplot(2, 1, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
#plt.ylim([0.8, 1])
#plt.plot([initial_epochs-1,initial_epochs-1],
          #plt.ylim(), label='Start Fine Tuning')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

#plt.subplot(2, 1, 2)
#plt.plot(loss, label='Training Loss')
#plt.plot(val_loss, label='Validation Loss')
#plt.ylim([0, 1.0])
#plt.plot([initial_epochs-1,initial_epochs-1],
         #plt.ylim(), label='Start Fine Tuning')
#plt.legend(loc='upper right')
#plt.title('Training and Validation Loss')
#plt.xlabel('epoch')
#plt.show()

loss, accuracy = model.evaluate(test_ds)
print('Test accuracy :', accuracy*100)

