#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 14:10:23 2022

@author: jcloud
"""

#ADD AUDIO
#MODIFY COMMENTED PLACES BELOW
#FIGURE OUT HOW TO ADD FIXATION

import psychopy.visual
from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB', 'sounddevice', 'pyo', 'pygame']
from psychopy import core, event, parallel

from pygaze.libinput import  Keyboard
from pygaze.libscreen import Display, Screen
from pygaze.eyetracker import EyeTracker
import pygaze

import argparse
import pandas as pd
import os
import random
import numpy as np
import matplotlib.pyplot as plt

import stimlsltools as slt

parser = argparse.ArgumentParser(description='')
parser.add_argument('--filename', dest='filename', type=str, help='name of output data file (.csv)', required = True)
parser.add_argument('--withEEG', dest='withEEG', type=bool, help='True if running with EEG', default=False)
parser.add_argument('--portAddress', dest='portAddress', type=int, help='address of parallel port', default=0)

args = parser.parse_args()

withEEG = args.withEEG

visuals = {
'FlankerStart' : ['Next activity starting soon.', 'space', True, 0],
'Instructions1' : ['You will see arrows presented at the middle of the screen that point either to the left (<) or right (>).\n\nPress the left button (C) if the arrow is pointing to the left\n\n(<)\n\nor press the right button (M) if the arrow is pointing to the right\n\n(>).', 'space', False, 0],
'Instructions2' : ['These arrows will appear in the center of a line of other items.\n\nSometimes, these other items will be arrows pointing in the same direction\n\n(>>>>>),\n\nor in the opposite direction\n\n(<<><<).', 'space', False, 0],
'Instructions3' : ['Your job is to respond to the middle arrow, no matter what direction the other arrows are pointing. For example, you would press the left button for both\n\n(<<<<<)\n\nand\n\n(>><>>)\n\nbecause the middle arrows point to the left.\n\nTry pressing the left button now.', 'c', False, 0],
'Instructions3.5' : ['As another example, you would press the right button for both\n\n(>>>>>)\n\nand\n\n(<<><<)\n\nbecause the middle arrows point to the right.\n\nTry pressing the right button now.', 'm', False, 0],
'Instructions4' : ['Finally, in some trials dashes (-) will appear beside the middle arrow.\n\nAgain, respond only to the direction of the middle arrow.\n\nPlease respond as quickly and accurately as possible.', 'space', False, 0],
'Instructions5' : ['Now you will have a chance to practice the task before moving on to the test phase.\n\nRemember to respond only to the middle arrow.', 'space', False, 0],
'Practice1' : [],
'Feedback1' : ['', 'space', True, 0],
'Practice2' : [],
'Feedback2' : ['', 'space', True, 0],
'Practice3' : [],
'Feedback3' : ['', 'space', True, 0],
'Instructions6' : ['Good job on the practice trials. You can now move on to the test trials. You will do the same task as in the practice, responding to the direction of the middle arrow.\n\nYou will complete three blocks of trials, each about 3-5 minutes long. You will have a short break in between these trials.\n\nRemember to respond only to the middle arrow.', 'space', False, 0],
'Stim1' : [],
'Break1' : ['Take a break!', 'space', True, 0],
'Stim2' : [],
'Break2' : ['Take a break!', 'space', True, 0],
'Stim3' : [],
'FlankerEnd' : ['Thank you!', 'space', True, 0]
}

present_list = os.listdir('/home/nkirs/Desktop/MOBI/Stimuli/flanker_orders')
random.shuffle(present_list)
stimlist = []
practicelist = []

for x in range(6):
    f = open('/home/nkirs/Desktop/MOBI/Stimuli/flanker_orders/{}'.format(present_list[x]), 'r')
    temp = f.readlines()
    temp2 = []
    for i in temp:
        temp2.append(i.rstrip('\n'))
        if x % 2 != 0:
            temp2.append('feedback')
        temp2.append('fixation')
    if x % 2 == 0:
        stimlist.append(temp2)
    else:
        practicelist.append(temp2)

visuals['Stim1'] = [stimlist[0], 'c', True, len(stimlist[0])]
visuals['Stim2'] = [stimlist[1], 'c', True, len(stimlist[1])]
visuals['Stim3'] = [stimlist[2], 'c', True, len(stimlist[2])]
visuals['Practice1'] = [practicelist[0], 'c', True, 90]
visuals['Practice2'] = [practicelist[1], 'c', True, 90]
visuals['Practice3'] = [practicelist[2], 'c', True, 90]

disp = Display(disptype='psychopy', bgc ='black')
scr = Screen(disptype='psychopy', bgc='black')
event.Mouse(visible = False)

#pygaze.expdisplay.recordFrameIntervals = True

if withEEG:
    p_port = parallel.ParallelPort(address=args.portAddress)
    
crosshair = psychopy.visual.ShapeStim(
    win = pygaze.expdisplay,
    units = 'pix',
    vertices = ((-3,.5),(-.5,.5),
                (-.5,3),(.5,3),
                (.5,.5),(3,.5),
                (3,-.5),(.5,-.5),
                (.5,-3),(-.5,-3),
                (-.5,-.5),(-3,-.5)),
    size = 20,
    fillColor = 'Black',
    lineColor = 'White')
    
center_text = psychopy.visual.TextStim(
    win = pygaze.expdisplay,
    text = '',
    height = 50, 
    wrapWidth = 1080)
    
image = psychopy.visual.ImageStim(
    win = pygaze.expdisplay,
    image = None)
    
image_text = '/home/nkirs/Desktop/MOBI/Stimuli/flanker_stim/{}.png'
    
if withEEG:
    p_port.setData(0)
    
out_dict = {'sectionname' : ['starttime', 'endtime', 'duration', 'responsetime', 'delta', 'condition', 'response', 'accuracy']}

cont = True
visual_screens = list(visuals.keys())
visual_screen_idx = 0
visual_screen = None
new_screen = True
finish_screen = False
task_clock = core.Clock()
timeout = 2
fixationtime = .5

curtime = None
starttime = None
endtime = None
duration = None
responsetime = None
response = None
delta = None
condition = None
accuracy = None
rep = 0
cur_stim = None
accuracy_list = []

flip_rate = 60
duration = 10000
flips = duration * flip_rate
flip_rate = 1 / flip_rate
flip_timing = [flip_rate * t for t in range(flips)]
frame = 0

send_pulse = False

while cont:
    curtime = task_clock.getTime()
    if curtime >= flip_timing[frame]:
        disp.fill(screen=scr)
        disp.show()
        frame += 1
        
        scr.clear()
        visual_screen = visual_screens[visual_screen_idx]
        if type(visuals[visual_screen][0]) != list:
            if 'Feedback' in visual_screen:
                if type(accuracy_list) == list:
                    accuracy_list = np.array(accuracy_list)
                mean = accuracy_list.mean()
                accuracy = mean
                if accuracy >= .75 or visual_screen == 'Feedback3':
                    center_text.text = 'Good job!'
                else:
                    center_text.text = 'Good job! You will now do another practice round. Remember to respond only to the central arrow'
                accuracy_list = list(accuracy_list)
            else:
                center_text.text = visuals[visual_screen][0]
            scr.screen.append(center_text)
            cur_stim = None 
            condition = None
        else:
            cur_stim = visuals[visual_screen][0][rep]
            if cur_stim == 'feedback':
                if accuracy == 0 and responsetime != None:
                    center_text.text = 'Incorrect.'
                elif accuracy == 1:
                    center_text.text = 'Correct!'
                else:
                    center_text.text = 'Too Slow.'
                scr.screen.append(center_text)
                condition = None
            else:
                image.setImage(image_text.format(cur_stim))
                scr.screen.append(image)
                condition = cur_stim
                if 'fixation' in cur_stim:
                    condition = None
    
        if new_screen and visuals[visual_screen][2]:
            if withEEG:
                p_port.setData(255)
                send_pulse = True
            if cur_stim is not None and 'fixation' not in cur_stim and 'feedback' not in cur_stim:
                slt.pushToStreamLabel('Onset ' + visual_screen)
    
        if new_screen:
            new_screen = False
            starttime = task_clock.getTime()
            print('NOW RUNNING: FLANKER')
        else:
            if withEEG and not send_pulse:
                p_port.setData(0)
        
        keys = event.getKeys(['escape', 'space', 'c', 'm'])
        if 'escape' in keys:
            break
        elif len(keys) > 0 and visuals[visual_screen][2]:
            responsetime = curtime
            response = keys[-1]
            if response == 'c':
                response = 'left'
            elif response == 'm':
                response = 'right'
            if cur_stim is not None and response in cur_stim:
                accuracy = 1
            elif response == 'space':
                pass
            else:
                accuracy = 0
            if accuracy != None:
                accuracy_list.append(accuracy)
                slt.pushToStreamLabel('Response: ' + response + '_' + str(accuracy))
            
        if type(visuals[visual_screen][1]) == str:
            if visuals[visual_screen][1] == 'c' and 'Instructions' not in visual_screen and 'fixation' not in cur_stim and 'feedback' not in cur_stim:
                if ('c' in keys or 'm' in keys) or curtime - starttime >= timeout:
                    finish_screen = True
                    if curtime - starttime >= timeout:
                        accuracy = None
                        accuracy_list.append(0)
            elif visuals[visual_screen][1] == 'c' and 'Instructions' not in visual_screen:
                if curtime - starttime >= fixationtime:
                    finish_screen = True
            elif visuals[visual_screen][1] in keys:
                finish_screen = True
            
        else:
            if curtime - starttime >= visuals[visual_screen][1]:
                finish_screen = True
            
        if finish_screen:
            if rep + 1 >= visuals[visual_screen][3]:
                visual_screen_idx += 1
                rep = 0
            else:
                rep += 1
            
            finish_screen = False
            new_screen = True
            endtime = curtime
            duration = curtime - starttime
            if responsetime != None:
                if responsetime > starttime:
                    delta = responsetime - starttime
                else:
                    responsetime = None
                    delta = None
                    accuracy = None
                    response = None
                
            if 'Feedback' in visual_screen:
                if accuracy >= .75:
                    visual_screen_idx = visual_screens.index('Instructions6')
            if 'Feedback' in visual_screen or 'Break' in visual_screen:
                accuracy_list = []
        
            if visuals[visual_screen][2]:
                out_dict[visual_screen + '_' + str(rep)] = [starttime, endtime, duration, responsetime, delta, condition, response, accuracy]
                if withEEG:
                    p_port.setData(255)
                    send_pulse = True
                if cur_stim is not None and 'fixation' not in cur_stim and 'feedback' not in cur_stim:
                    slt.pushToStreamLabel('Offset ' + visual_screen)
        
            if visual_screen_idx == len(visual_screens):
                cont = False
            
        else:
            if withEEG and not send_pulse:
                p_port.setData(0)
    
        send_pulse = False

df = pd.DataFrame(out_dict)
df = df.transpose()            
df.to_csv(args.filename)

#x = pygaze.expdisplay.frameIntervals
#mean = 0
#for i in x:
#    mean += i
#mean = mean / len(x)
#f = open('x.txt', 'w')
#f.write(str(mean) + '\n')
#f.write(str(1 / mean))
#f.close()
#plt.plot(x)
#plt.show()
#pygaze.expdisplay.saveFrameIntervals(fileName = None, clear = True)

disp.close()

    
        
    
        
        
        



