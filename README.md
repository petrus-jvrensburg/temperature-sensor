# TEMPERATURE-SENSOR

Code for running prototype temperature sensor box. Originally written by Cobus van der Merwe, from ETSE.

## Setup for reading comms over serial

    cd temperature_sensor
    virtualenv env -p python3
    source env/bin/activate
    pip install -r requirements.txt

Then do the wiring, and enable serial comms on the RaspberryPi, using the steps outlined in [this blog post](https://scribles.net/setting-up-uart-serial-communication-between-raspberry-pis/).

## Reading comms from "/dev/serial0"

    cd temperature_sensor
    source env/bin/activate
    python serial_read.py

This script will keep running, and print the incoming comms to the terminal.  

## list available serial ports on a device

    python -m serial.tools.list_ports

## reference

*UART on RPi docs:* https://www.raspberrypi.org/documentation/configuration/uart.md

*Python Serial docs:* https://pythonhosted.org/pyserial/shortintro.html#opening-serial-ports
