from gpiozero import LED, Button
from signal import pause
from time import sleep
from picamera import PiCamera
import cv2
import imutils
from imutils import contours
import numpy as np
import serial

try:
	ser = serial.Serial('/dev/ttyS0', 57600, timeout=1)
	ser.flush()
except:
	print("Cannot connect to Serial (/dev/ttyAMA0)")
else:
	DIGITS_LOOKUP = {
	    (1, 1, 1, 0, 1, 1, 1): 0,
	    (0, 0, 1, 0, 0, 1, 0): 1,
	    (1, 0, 1, 1, 1, 0, 1): 2,
	    (1, 0, 1, 1, 0, 1, 1): 3,
	    (0, 1, 1, 1, 0, 1, 0): 4,
	    (1, 1, 0, 1, 0, 1, 1): 5,
	    (1, 1, 0, 1, 1, 1, 1): 6,
	    (1, 0, 1, 0, 0, 1, 0): 7,
	    (1, 1, 1, 1, 1, 1, 1): 8,
	    (1, 1, 1, 1, 0, 1, 1): 9,
	    (0, 0, 0, 1, 0, 0, 0): '-',
	    (0, 1, 0, 0, 1, 0, 1): 'L',
	    (0, 0, 0, 1, 1, 1, 1): 'o',
	    (0, 0, 0, 0, 0, 0, 0): '*'	
	}

	#erosion
	def erode(image):
	    kernel = np.ones((1,3),np.uint8)
	    return cv2.erode(image, kernel, iterations = 1)

	#opening - erosion followed by dilation
	def opening(image):
	    kernel = np.ones((6,1),np.uint8)
	    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

	#skew correction
	def deskew(image):
	    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	    gray = cv2.bitwise_not(gray)
	    thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	    coords = np.column_stack(np.where(thresh > 0))
	    angle = cv2.minAreaRect(coords)[-1]
	    if angle < 5:
	        angle = -(95+angle)
	    else:
	        angle = -angle
	    (h, w) = image.shape[:2]
	    center = (w // 2, h // 2)
	    M = cv2.getRotationMatrix2D(center, angle, 1.0)
	    rotated = cv2.warpAffine(image, M, (w, h),
	        flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)    
	    return rotated


	camera = PiCamera()
	distance = Button(5)
	LED_Green = LED(2)
	LED_Red = LED(3)
	Trigger_Sensor = LED(26)
	LED_Red.on()
	LED_Green.on()
	Trigger_Sensor.on()

	TakeReadingFlag = 0;
	TakePictureFlag = 0;

	while True:
		Trigger_Sensor.off()
		if TakePictureFlag == 0:
			if distance.value:

				LED_Green.on()
				LED_Red.off()

				if TakeReadingFlag == 0:

					Trigger_Sensor.on()
					sleep(0.1)
					Trigger_Sensor.off()
					sleep(0.1)
					TakePictureFlag = 1;
			else:
				LED_Green.off()
				LED_Red.on()
				TakeReadingFlag = 0;
		else:
			camera.start_preview()
			sleep(2)
			camera.capture('/home/pi/Desktop/image_now.jpg')
			camera.stop_preview()
			sleep(0.2)
			image_to_extract = cv2.imread('/home/pi/Desktop/image_now.jpg')
			image = image_to_extract

			image = imutils.resize(image, height=500)
			output = image.copy()
			eroded = erode(output)
			deskewIm = deskew(eroded)
			gray = cv2.cvtColor(deskewIm, cv2.COLOR_BGR2GRAY)
			thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
			openings = opening(thresh)
			rnoise = cv2.medianBlur(openings,5)
			eroded = erode(rnoise)
			edged_image = cv2.Canny(eroded, 100, 255)
			# ////////////////////////////////////////////////////////////////////
			output = deskewIm.copy()
			
			digits = [] 
			#fixed frame coordinates    
			ff = [[344,134,42,84],[391,133,41,84],[437,132,41,84]]
			loop = [0,1,2]
			# loop over each of the digits
			for c in loop:
				# extract the digit ROI
				box=ff[c]
				x = box[0]
				y = box[1]
				w = box[2]
				h = box[3]
				roi = thresh[y:y + h, x:x + w]
	    			# compute the width and height of each of the 7 segments
	    			# we are going to examine
				(roiH, roiW) = roi.shape
				(dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
				dHC = int(roiH * 0.05)
				# define the set of 7 segments
				segments = [
					((0, 0), (w, dH)),  # top
					((0, 0), (dW, h // 2)), # top-left
					((w - dW, 0), (w, h // 2)), # top-right
					((0, (h // 2) - dHC) , (w, (h // 2) + dHC)), # center
					((0, h // 2), (dW, h)), # bottom-left
					((w - dW, h // 2), (w, h)), # bottom-right
					((0, h - dH), (w, h))   # bottom
				]
				on = [0] * len(segments)
				# loop over the segments
				for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
					# extract the segment ROI, count the total number of
					# thresholded pixels in the segment, and then compute
					# the area of the segment
					segROI = roi[yA:yB, xA:xB]
					total = cv2.countNonZero(segROI)
					area = (xB - xA) * (yB - yA)
					# if the total number of non-zero pixels is greater than
					# 32.5% of the area, mark the segment as "on"
					if total / float(area) > 0.325:
						on[i]= 1
				# lookup the digit and draw it on the image
				try:
					digit = DIGITS_LOOKUP[tuple(on)]
					digits.append(digit)
				except ValueError:
					digits.append('E')
				# cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 1)
				# cv2.putText(output, str(digit), (x - 10, y - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
			if digits[0] == '-':
				print('Retake measurement')
				ser.write(b"Re\n")
				TakeReadingFlag = 0;
			elif digits[0] == 'L':
				print('Temp too low')
				ser.write(b"Lo\n")
			elif digits[0] == 'E'
				print('Digit unknown')
				ser.write(b"Err\n")
			else:
				# display the digits
				string_val = u"{}{}.{}".format(*digits)
				print(string_val)
				
				ser.write(string_val.encode('utf-8'))
				LED_Green.off()
				sleep(0.1)
				LED_Green.on()
				sleep(0.1)
				LED_Green.off()
				sleep(0.1)
				LED_Green.on()
				sleep(0.1)
				LED_Green.off()
				sleep(0.1)
				LED_Green.on()

			TakePictureFlag = 0;