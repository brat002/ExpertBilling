from utilites import create_speed
import datetime

default = ['2048k', '2048k', '2100k', '2100k', '2000k', '2000k', 8, 8, '1500k', '1500k', 8, 25]
speeds = []
correction = [512,512,0,0,0,0,0,0,0,0,0, 'Kbps', 'abs']
addonservicespeed = []
speed = ''
date_ = datetime.datetime.now()
fMem = {}

print create_speed(default, speeds,  correction, addonservicespeed, speed, date_, fMem)
