# Seer - A Computer Vision and Machine Learning based Device for Visually Impaired

Seer is a Computer Vision and Machine Learning based Device for Visually Impaired, built using Raspberry Pi and coded in Python.

<img src="https://github.com/abd612/seer/blob/master/documentation/seer-logo.png" width="200"  style="vertical-align:middle">

## Description

* Language: Python
* Libraries: Numpy, Pandas, Scikit-Learn, Matplotlib, Tensorflow, Keras, OpenCV, ImUtils
* Models: MobileNet-SSD, HAAR/HOG, EAST/Tesseract
* Microcontroller: Raspberry Pi 3
* Video: https://youtu.be/LcJY8Y7udfg

## Abstract

Vision is the most important and primitive tool for mankind to learn and interact with the environment. The significance of vision has skyrocketed in this current era of information technology. Sadly, there are millions of people in the world who have to live their lives in eternal darkness or with some sort of visual impairment. They rely on their family to fulfill their daily needs. We are trying to come up with a solution which can make the visually impaired people more independent in their daily chores. Visually challenged people use their sense of touch or someone else’s help to identify everyday objects. Our proposed device will help the people with visual disabilities to recognize common objects in their line of sight. We want to allow them to identify familiar faces, everyday objects and recognize text that they come across in their daily life. We are using models based on machine learning and computer vision to input image through a camera and get the information about various objects in the image. The obtained information about the object is conveyed to the user in the form of audio. For object detection, we are using a pretrained model which is trained on hundreds of thousands of images and we have fine-tuned it with our own collected dataset. The model being used is MobileNet-SSD which is based on Convolutional Neural Networks. The data collected by us spans around 30 categories with 40 to 50 images per category. With a train/test split of 80/20, we’ve achieved an accuracy of around 80% for object detection. For text recognition, the object containing text is first identified using a model called EAST Detector and then an OCR software called Tesseract is used to convert the image into machine recognizable text. The text detector is based on a deep neural network architecture and gives an accuracy of around 90%. In case of facial recognition, a combination of HAAR and HOG Classifier is being used to detect the faces while Nearest Means Classifier employing the vector embeddings created from our own custom dataset is being used to recognize them. The data collected by us spans around 10 persons with 50 images per person. With a train/test split of 80/20, we’ve achieved an accuracy of around 85% for face recognition. The major tools being deployed are Python, Numpy, Pandas, Scikit-Learn, Matplotlib, Tensorflow, Keras, OpenCV and ImUtils.

## Developer
 
[@abd612](https://github.com/abd612)