import serial
import time

port = "/dev/serial0"

try:
	ser = serial.Serial(port, 57600, timeout=1)
	ser.flush()
except ConnectionError:
	print(f"Cannot connect to Serial {port}")

while True:
	time.sleep(1)
	data_left = ser.inWaiting()  #check for remaining byte
	input = ser.read(data_left)
	if input:
		print(input)
