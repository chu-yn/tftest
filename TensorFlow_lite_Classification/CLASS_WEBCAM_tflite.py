from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import io
import time
import numpy as np
import cv2

# import tensorflow as tf
from tflite_runtime.interpreter import Interpreter


from PIL import Image

def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}


def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image

def classify_image(interpreter, image, top_k=1):
  """Returns a sorted array of classification results."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  # If the model is quantized (uint8 data), then dequantize the results
  if output_details['dtype'] == np.uint8:
    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

  ordered = np.argpartition(-output, top_k)
  return [(i, output[i]) for i in ordered[:top_k]]


def main():
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
     '--model', help='Model path of model.tflite and labels.txt.', required=True)
  parser.add_argument(
      '--video', help='Webcam index number.', required=False, type=int, default=0)
  args = parser.parse_args()

  model_file = args.model + '/model.tflite'
  labels_file = args.model + '/labels.txt'

  labels = load_labels(labels_file)

  # interpreter = tf.lite.Interpreter(model_file)
  interpreter = Interpreter(model_file)

  interpreter.allocate_tensors()
  _, height, width, _ = interpreter.get_input_details()[0]['shape']
  print('model size (w / h) =',width,height)

  cap = cv2.VideoCapture(args.video)
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

  key_detect = 0
  times=1
  while (key_detect==0):
    ret,image_src =cap.read()

    frame_width=image_src.shape[1]
    frame_height=image_src.shape[0]

    cut_d=int((frame_width-frame_height)/2)
    crop_img=image_src[0:frame_height,cut_d:(cut_d+frame_height)]

    image=cv2.resize(crop_img,(width,height),interpolation=cv2.INTER_AREA)

    if (times==1):
      results = classify_image(interpreter, image)
      label_id, prob = results[0]

    print(labels[label_id],prob)
    cv2.putText(crop_img,
      labels[label_id] + " " + str(round(prob,2)),
      (5,30), cv2.FONT_HERSHEY_SIMPLEX, 1,
      (0,255,0), 6, cv2.LINE_AA)
    cv2.putText(crop_img,
      labels[label_id] + " " + str(round(prob,2)),
      (5,30), cv2.FONT_HERSHEY_SIMPLEX, 1,
      (0,0,0), 2, cv2.LINE_AA)

    times=times+1
    if (times>2):
      times=1

    cv2.imshow('Detecting....',crop_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      key_detect = 1

  cap.release()
  cv2.destroyAllWindows()

if __name__ == '__main__':
  main()
