# Commented out IPython magic to ensure Python compatibility.
import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import matplotlib.pyplot as plt
from IPython.display import clear_output, display
import cv2
import numpy as np
import pickle
try:
    import mtcnn
except:
#     %pip install mtcnn    
    import mtcnn
# print version to confirm that mtcnn was successfully installed
print(mtcnn.__version__)

# create the mtcnn face detector
detector = mtcnn.MTCNN()

import cv2
import numpy as np

cap    = cv2.VideoCapture(0)
print('height:{} width:{}'.format(int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))))

while True:
    ret, image = cap.read() 
    if ret==False:
        break
        
    results = detector.detect_faces(image[...,[2,1,0]])    

    for b in results:
        x1, y1, width, height = b['box']
        cv2.rectangle(image,(x1,y1),(x1+width,y1+height),(0,0,255),2)
    
    cv2.imshow('camera',image)
    key = cv2.waitKey(20) & 0xFF
    if key == 27:
        break
    
cap.release()
cv2.destroyAllWindows()
