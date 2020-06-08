from time import sleep
from random import random
import serial

port = "/dev/ttyAMA0"

try:
	ser = serial.Serial(port, 57600, timeout=1)
	ser.flush()
except:
	print(f"Cannot connect to Serial {port}")
else:
	while True:
		seed = int(random() * 10)  # random value from 0 to 9
		if seed == 0:
			print('Retake measurement')
			ser.write(b"Re\n")
		elif seed == 1:
			print('Temp too low')
			ser.write(b"Lo\n")
		elif seed == 2:
			print('Digit unknown')
			ser.write(b"Err\n")
		else:
			# fever > 37.5
			low = 33.5
			high = 38.3 

			# generate random feasible temperature
			test_val = low + ((high - low) * random())
			string_val = f"{test_val:.1f}"

			# display the digits
			print(string_val)
			
			ser.write(string_val.encode('utf-8'))
		sleep(10)