#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
import json
import pathlib
import time

from tkinter import *

import serial
import serial.tools.list_ports


CONFIG_FILE = 'settings.json'
CONFIG_FPATH = pathlib.Path(__file__).parent / CONFIG_FILE

PORT_NAME = 'COM4'
BAUD_RATE = 115200
TIMEOUT = 0
PARITY = serial.PARITY_EVEN
HW_HANDSHAKE = 0


ser = serial.Serial(baudrate=BAUD_RATE, timeout=TIMEOUT, parity=PARITY, rtscts=HW_HANDSHAKE)
# set port name later in order to keep port closed, will be opened later
ser.port = PORT_NAME


def from_rgb(rgb):
    # https://stackoverflow.com/q/5661725/3991125
    val = ''.join(f'{i:02x}' for i in rgb)
    return f'#{val}'

@dataclass
class SliderContainer:
    color: str
    variable: IntVar


def get_values():
    return {key: slider_container.variable.get() for key, slider_container in sliders.items()}


def send_values(serial_port=ser):
    values = get_values()
    values['setAsDefault'] = False
    print('Sending values:', values)
    payload = json.dumps(values).encode()
    # TODO: Enable Serial Port Output
    serial_port.write(payload)


def save_as_default():
    # TODO: Do not use global variable (very ugly)
    global config
    settings = get_values()
    settings['setAsDefault'] = True
    config = settings.copy()
    with CONFIG_FPATH.open('w') as f:
        json.dump(settings, f)


def restore_default(config):
    # print(config)
    for color, slider_container in sliders.items():
        val = config.get(color, 0)
        slider_container.variable.set(val)
    send_values()


def load_config(fpath):
    try:
        config = json.loads(fpath.read_bytes())
    except FileNotFoundError as err:
        config = {}
    return config


def set_all_value(val):
    for slider_container in sliders.values():
        slider_container.variable.set(val)
    send_values()


# TODO: Refactor function since it returns several widgets
def make_slider(color, config=None):
    sliders[color] = SliderContainer(color, IntVar())
    # TODO: Why is command function executed (is already encapsulated in lambda function)?
    slider = Scale(root, label=None, from_=0, to=255, showvalue=False, orient=HORIZONTAL, variable=sliders[color].variable, command=lambda val: send_values())
    # slider = Scale(root, label=None, from_=0, to=255, showvalue=False, orient=HORIZONTAL, variable=sliders[color].variable)
    # print(config)
    if config:
        initial_val = config.get(color, 0)
        slider.set(initial_val)
    label = Label(root, text=f'{color.title()}:')
    entry = Entry(root, width=3, justify=RIGHT, textvariable=sliders[color].variable, validatecommand=None, validate=None)
    return label, slider, entry


def calculate_mixed_rgb(*args):
    red = sliders['red'].variable.get()
    green = sliders['green'].variable.get()
    blue = sliders['blue'].variable.get()
    color = from_rgb((red, green, blue))
    color_indicator.config(background=color)


def quit():
    # TODO: Implement function to quit
    # https://stackoverflow.com/q/111155/3991125
    pass


sliders = {}
config = load_config(CONFIG_FPATH)


print('Serial Port open:', ser.is_open)
ser.open()
print('Serial Port open:', ser.is_open)

# TODO: Get ACK from device?
print('Waiting for connection')
time.sleep(2)

# available_ports = [str(port).split(' ')[0] for port in serial.tools.list_ports.comports()]
# print(available_ports)

root = Tk()
root.title('Set Illumination')
# root.grid_columnconfigure(0, minsize=20)
# root.grid_columnconfigure(5, minsize=20)

row = 0
label = Label(root, text='Port:')
label.grid(row=row, column=0, sticky=W)

# TODO: Use drop-down to select serial port, m currently hard coded
label = Label(root, text=f'{PORT_NAME}')
label.grid(row=row, column=1, sticky=W)

# selected_port = StringVar()
# select = OptionMenu(root, selected_port, *available_ports)
# select.grid(row=row, column=2, sticky=W)

# TODO: Implement function to refresh serial ports
# btn = Button(root, text='Refresh Ports', command=None)
# btn.grid(row=row, column=3, sticky=W)


row = 1
root.grid_rowconfigure(row, minsize=10)


row = 2
label, slider, entry = make_slider('red', config)
label.grid(row=row, column=0, sticky=W)
slider.grid(row=row, column=1, sticky=W)
entry.grid(row=row, column=2, sticky=W)


row = 3
label, slider, entry = make_slider('green', config)
label.grid(row=row, column=0, sticky=W)
slider.grid(row=row, column=1, sticky=W)
entry.grid(row=row, column=2, sticky=W)


row = 4
label, slider, entry = make_slider('blue', config)
label.grid(row=row, column=0, sticky=W)
slider.grid(row=row, column=1, sticky=W)
entry.grid(row=row, column=2, sticky=W)


row = 5
label, slider, entry = make_slider('white', config)
label.grid(row=row, column=0, sticky=W)
slider.grid(row=row, column=1, sticky=W)
entry.grid(row=row, column=2, sticky=W)


# TODO: Think about brightness since this is not readily supported by MCU library
# row = 6
# label, slider, entry = make_slider('brightness', config)
# label.grid(row=row, column=0, sticky=W)
# slider.grid(row=row, column=1, sticky=W)
# entry.grid(row=row, column=2, sticky=W)


row = 7
root.grid_rowconfigure(row, minsize=10)


row = 8
btn = Button(root, text='Zero', command=lambda: set_all_value(0))
btn.grid(row=row, column=0, sticky=NSEW, padx=5, pady=5)

btn = Button(root, text='Maximum', command=lambda: set_all_value(255))
btn.grid(row=row, column=3, sticky=NSEW, padx=5, pady=5)


row = 9
btn = Button(root, text='Restore', command=lambda: restore_default(config))
btn.grid(row=row, column=0, sticky=NSEW, padx=5, pady=5)

btn = Button(root, text='Save', command=save_as_default)
btn.grid(row=row, column=3, sticky=NSEW, padx=5, pady=5)


# mixed rows/columns
color_indicator = Label(root, text=None, width=5)
calculate_mixed_rgb()
color_indicator.grid(row=2, column=3, columnspan=1, rowspan=3, sticky=NSEW, padx=5, pady=2)


# observe RGB color variables for mixed color indicator label
for color in ['red', 'green', 'blue']:
    sliders[color].variable.trace('w', calculate_mixed_rgb)


root.geometry()
root.resizable(0, 0)
root.mainloop()
