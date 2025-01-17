import numpy as np
from imutils.video import VideoStream
from imutils.video import FPS
from imutils.object_detection import non_max_suppression
import face_recognition
import pytesseract
import argparse
import imutils
import pickle
import time
import cv2
import pyttsx3
import RPi.GPIO as GPIO
import time

engine = pyttsx3.init()

args = {
    "facial-encodings": "models/facial_recognition_encodings",
    "facial-recognition-model": "models/facial_recognition_model_haar.xml",
    "object-recognition-config": "models/object_recognition_config.pbtxt",
    "object-recognition-model": "models/object_recognition_model_mobilenetssd.pb",
    "text-recognition-model": "models/text_recognition_model_east.pb",
    "object-min-confidence": 0.5,
    "text-min-confidence": 0.5,
    "text-width": 320,
    "text-height": 320,
    "text-padding": 0.05,
}

t1 = time.time()
print("[INFO] loading facial recognition model...")
data = pickle.loads(open(args["facial-encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["facial-recognition-model"])

t2 = time.time()
print("Time to load facial recognition model: %.2f" % (t2 - t1))

CLASSES = [
    "none",
    "bag",
    "bed",
    "bike",
    "billboard",
    "bird",
    "book",
    "bottle",
    "bowl",
    "building",
    "car",
    "cat",
    "chair",
    "cup",
    "dog",
    "door",
    "fan",
    "keys",
    "laptop",
    "pen",
    "person",
    "phone",
    "plant",
    "rickshaw",
    "shoes",
    "switchboard",
    "table",
    "tree",
    "tv",
    "wallet",
    "watch",
]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading object recognition model...")
net = cv2.dnn.readNetFromTensorflow(
    args["object-recognition-model"], args["object-recognition-config"]
)

t3 = time.time()
print("Time to load object recognition model: %.2f" % (t3 - t2))

layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]

# load the pre-trained EAST text detector
print("[INFO] loading text recognition model...")
net1 = cv2.dnn.readNet(args["text-recognition-model"])

t4 = time.time()
print("Time to load text recognition model: %.2f" % (t4 - t3))

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(1.0)

t5 = time.time()
print("Time to turn on camera: %.2f" % (t5 - t4))

print("Welcome to Seer.")
engine.say("Welcome to Seer.")
print("Push button 1 for facial recognition.")
engine.say("Push button 1 for facial recognition.")
print("Push button 2 for object recognition.")
engine.say("Push button 2 for object recognition.")
print("Push button 3 for text recognition.")
engine.say("Push button 3 for text recognition.")

engine.runAndWait()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(3, GPIO.OUT)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(3, 1)
GPIO.output(11, 1)
GPIO.output(19, 1)

while True:

    if GPIO.input(7) == GPIO.HIGH:

        print("You pushed button 1. Starting facial recognition.")
        engine.say("You pushed button 1. Starting facial recognition.")
        engine.runAndWait()
        facial_recognition()

    if GPIO.input(15) == GPIO.HIGH:

        print("You pushed button 2. Starting object recognition.")
        engine.say("You pushed button 2. Starting object recognition.")
        engine.runAndWait()
        object_recognition()

    if GPIO.input(23) == GPIO.HIGH:

        print("You pushed button 3. Starting text recognition.")
        engine.say("You pushed button 3. Starting text recognition.")
        engine.runAndWait()
        text_recognition()

GPIO.cleanup()
print("Exiting application")


def facial_recognition():

    # grab the frame from the threaded video stream and resize it
    # to 500px (to speedup processing)
    frame = vs.read()
    frame = imutils.resize(frame, width=500)

    # convert the input frame from (1) BGR to grayscale (for face
    # detection) and (2) from BGR to RGB (for face recognition)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # detect faces in the grayscale frame
    rects = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    # OpenCV returns bounding box coordinates in (x, y, w, h) order
    # but we need them in (top, right, bottom, left) order, so we
    # need to do a bit of reordering
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

        # check to see if we have found a match
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)
            # update the list of names
            names.append(name)
        else:
            print("No face detected")
            engine.say("No face detected")

    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(
            frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2
        )
        if names:
            print(name)
            engine.say(name)
        else:
            print("No face Detected")

    # display the image to our screen
    engine.runAndWait()
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF


def object_recognition():

    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True, crop=False)

    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()

    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > args["object-min-confidence"]:
            # extract the index of the class label from the
            # `detections`, then compute the (x, y)-coordinates of
            # the bounding box for the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(
                frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2
            )

            if CLASSES[idx]:
                print(CLASSES[idx])
                engine.say(CLASSES[idx])
            else:
                print("Nothing")

    # show the output frame
    engine.runAndWait()
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF


def text_recognition():

    frame = vs.read()

    orig = frame.copy()
    (origH, origW) = frame.shape[:2]

    # set the new width and height and then determine the ratio in change
    # for both the width and height
    (newW, newH) = (args["text-width"], args["text-height"])
    rW = origW / float(newW)
    rH = origH / float(newH)
    frame = cv2.resize(frame, (newW, newH))
    (H, W) = frame.shape[:2]

    # construct a blob from the image and then perform a forward pass of
    # the model to obtain the two output layer sets
    blob = cv2.dnn.blobFromImage(
        frame, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False
    )
    net1.setInput(blob)
    (scores, geometry) = net1.forward(layerNames)

    # decode the predictions, then  apply non-maxima suppression to
    # suppress weak, overlapping bounding boxes
    (rects, confidences) = decode_predictions(scores, geometry)
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    # initialize the list of results
    results = []

    # loop over the bounding boxes
    for (startX, startY, endX, endY) in boxes:
        # scale the bounding box coordinates based on the respective
        # ratios
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)

        # in order to obtain a better OCR of the text we can potentially
        # apply a bit of padding surrounding the bounding box -- here we
        # are computing the deltas in both the x and y directions
        dX = int((endX - startX) * args["text-padding"])
        dY = int((endY - startY) * args["text-padding"])

        # apply padding to each side of the bounding box, respectively
        startX = max(0, startX - dX)
        startY = max(0, startY - dY)
        endX = min(origW, endX + (dX * 2))
        endY = min(origH, endY + (dY * 2))

        # extract the actual padded ROI
        roi = orig[startY:endY, startX:endX]

        # in order to apply Tesseract v4 to OCR text we must supply
        # (1) a language, (2) an OEM flag of 4, indicating that the we
        # wish to use the LSTM neural net model for OCR, and finally
        # (3) an OEM value, in this case, 7 which implies that we are
        # treating the ROI as a single line of text
        config = "-l eng --oem 1 --psm 7"
        text = pytesseract.image_to_string(roi, config=config)

        # add the bounding box coordinates and OCR'd text to the list
        # of results
        results.append(((startX, startY, endX, endY), text))

    # sort the results bounding box coordinates from top to bottom
    results = sorted(results, key=lambda r: r[0][1])

    # loop over the results
    for ((startX, startY, endX, endY), text) in results:
        # display the text OCR'd by Tesseract
        print("{}".format(text))

        # strip out non-ASCII text so we can draw the text on the image
        # using OpenCV, then draw the text and a bounding box surrounding
        # the text region of the input image
        text = "".join([c if ord(c) < 128 else "" for c in text]).strip()

        if text:
            print(text)
            engine.say(text)

        output = orig.copy()
        cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv2.putText(
            orig,
            text,
            (startX, startY - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 255),
            3,
        )

    cv2.imshow("Frame", orig)
    key = cv2.waitKey(1) & 0xFF
    engine.runAndWait()


def decode_predictions(scores, geometry):

    # grab the number of rows and columns from the scores volume, then
    # initialize our set of bounding box rectangles and corresponding
    # confidence scores
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    # loop over the number of rows
    for y in range(0, numRows):
        # extract the scores (probabilities), followed by the
        # geometrical data used to derive potential bounding box
        # coordinates that surround text
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        # loop over the number of columns
        for x in range(0, numCols):
            # if our score does not have sufficient probability,
            # ignore it
            if scoresData[x] < args["text-min-confidence"]:
                continue

            # compute the offset factor as our resulting feature
            # maps will be 4x smaller than the input image
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            # extract the rotation angle for the prediction and
            # then compute the sin and cosine
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # use the geometry volume to derive the width and height
            # of the bounding box
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # compute both the starting and ending (x, y)-coordinates
            # for the text prediction bounding box
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            # add the bounding box coordinates and probability score
            # to our respective lists
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    # return a tuple of the bounding boxes and associated confidences
    return (rects, confidences)
