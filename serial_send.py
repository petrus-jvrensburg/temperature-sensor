import serial
import time

try:
	ser = serial.Serial('/dev/ttyS0', 57600, timeout=1)
	# Die een pi was ttyS0 die ander was ttyAMA0, kyk maar wat werk vir jou
	# ser = serial.Serial('/dev/ttyAMA0', 57600, timeout=1)
	ser.flush()
except ConnectionError:
	print("Cannot connect to Serial (/dev/ttyAMA0)")

read = 'xx'
while True:
	#ser.write(b"Hello from Raspberry Pi!\n")
	time.sleep(1)
	data_left = ser.inWaiting()             #check for remaining byte
	read = ser.read(data_left)
	print(read)
