import cv2
import mediapipe as mp
import numpy as np
from os import system

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0)
# Setup MP instance
x_min = 0
x_max = 0
y_min = 0
y_max = 0
count = 0
out_of_bounds_x = False
out_of_bounds_y = False
i = 0
with mp_pose.Pose(
  min_detection_confidence = 0.5,
  min_tracking_confidence = 0.5
  ) as pose:

  while cap.isOpened():
    ret, frame = cap.read()

    # Recolor to RGB for MP
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False

    # Detect pose
    results = pose.process(image)

    # Recolor back to BGR for CV
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    try:
      landmarks = results.pose_landmarks.landmark
      left_eye_x = landmarks[mp_pose.PoseLandmark.LEFT_EYE_OUTER].x
      left_eye_y = landmarks[mp_pose.PoseLandmark.LEFT_EYE_OUTER].y
      right_eye_x = landmarks[mp_pose.PoseLandmark.RIGHT_EYE_OUTER].x
      right_eye_y = landmarks[mp_pose.PoseLandmark.RIGHT_EYE_OUTER].y
      mouth_left_x = landmarks[mp_pose.PoseLandmark.MOUTH_LEFT].x
      mouth_left_y = landmarks[mp_pose.PoseLandmark.MOUTH_LEFT].y
      mouth_right_x = landmarks[mp_pose.PoseLandmark.MOUTH_RIGHT].x
      mouth_right_y = landmarks[mp_pose.PoseLandmark.MOUTH_RIGHT].y
      x_values = [left_eye_x, right_eye_x, mouth_left_x, mouth_right_x]
      y_values = [left_eye_y, right_eye_y, mouth_left_y, mouth_right_y]
  
      # Establish and update min and max values for the X and Y axes
      if i < 200 and i > 15:
        for value in x_values:
          if x_max < value or x_max == 0:
            x_max = value
          if x_min > value or x_min == 0:
            x_min = value
        
        for value in y_values:
          if y_max < value or y_max == 0:
            y_max = value
          if y_min > value or y_min == 0:
            y_min = value  
      
    except:
      pass

    # Build bountry box and text coordinates
    rectangle_top_left = [x_min, y_max]
    rectangle_bottom_right = [x_max, y_min]
    x_middle = (x_max - x_min)/2 - (x_max - x_min)*.1 + x_min
    calibrate_coords = [x_middle, y_max]

    # Extablish and update Calibration text during calibration
    if i < 200 and i > 15:
      if i % 3 == 0:
        calibrate_text = 'Calibrating...'
      elif i % 2 == 0:
        calibrate_text = 'Calibrating..'
      else:
        calibrate_text = 'Calibrating.'
    else:
      calibrate_text = 'Calibrated'

    # Check current values against established boundries
    if i >= 200:
      for value in x_values:
        if x_max < value or x_min > value:
          out_of_bounds_x = True
        else:
          out_of_bounds_x = False
      
      for value in y_values:
        if y_max < value or y_min > value:
          out_of_bounds_y = True
        else: 
          out_of_bounds_y = False
      
      if out_of_bounds_x == True or out_of_bounds_y == True:
        count += 1
      else:
        count = 0

      if count >= 30:
        count = 0
        print('Check Posture')
        system('say "Check posture"')
  
    # Draw boundry box and calibration text
    cv2.rectangle(image, tuple(np.multiply(rectangle_top_left, [1280, 720]).astype(int)), tuple(np.multiply(rectangle_bottom_right, [1280, 720]).astype(int)), (255,255,255), 1)
    cv2.putText(image, str(calibrate_text),
                  tuple(np.multiply(calibrate_coords, [1280, 720]).astype(int)),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA
                )
    
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS) # mp_pose.POSE_CONNECTIONS [mp_pose.PoseLandmark.RIGHT_EYE_OUTER, mp_pose.PoseLandmark.LEFT_EYE_OUTER]

    i += 1

    cv2.imshow('Webcam Feed', image)

    if cv2.waitKey(5) & 0xFF == 27:
      break
  
  cap.release()
  cv2.destroyAllWindows()