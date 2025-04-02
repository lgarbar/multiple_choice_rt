import psychopy.visual
from psychopy import prefs
from psychopy import core, event
from pynput import mouse as pynput_mouse
from pygaze.libinput import Keyboard
from pygaze.libscreen import Display, Screen
from pygaze.eyetracker import EyeTracker
import pygaze
import argparse
import pandas as pd
import os
import random
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='')
parser.add_argument('--filename', dest='filename', type=str, help='name of output data file (.csv)', required=True)
args = parser.parse_args()

visuals = {
    '4RTStart': ['Next activity starting soon.', 'space', True],
    'Instructions1': ["You will see images presented on the screen that correspond to the buttons on the device you are holding.\n\nWhen the image appears, you'll press the corresponding button.", 'space', False],
    'Instructions2': ["At first, only the stimulus that matches the left button will appear,\n\nand so you'll only be responding using that left button.\n\nGo ahead and press the left button once you see the diagonal line appear on screen.", 'space', False],
    'Example1': [['line.png', 'feedback'], 'c', True],
    'Instructions3': ["Next, the stimuli that match the left or right buttons will appear,\n\nso you'll have to respond using the left or right buttons.\n\nGo ahead and press the right button once you see the square appear on screen.", 'space', False],
    'Example2': [['square.png', 'feedback'], 'c', True],
    'Instructions4': ["In the final phase, you will respond to any of the four stimuli using all four buttons.\n\nGo ahead and press the middle button with the circle once you see the circle appear on screen.", 'space', False],
    'Example4': [['circle.png', 'feedback'], 'c', True],
    'Instructions5': ['Now you will have a chance to practice the task before moving on to the first phase.\n\nPay attention to the instructions on screen to know which stimuli could appear.', 'space', False],
    'Feedback1': ['You will respond to 1 stimulus', 'space', True],
    'Practice1': [],
    'Feedback2': ['You will respond to 2 stimuli', 'space', True],
    'Practice2': [],
    'Feedback3': ['You will respond to 4 stimuli', 'space', True],
    'Practice4': [],
    'Instructions6': ['Good job on the practice trials. You can now move on to the test trials.\n\nYou will do the same task as in the practice, completing a distinct blocks of trials for each of the phases described earlied.\n\nEach block will last about 3-5 minutes long. You will have a short break in between these trials.\n\nAnd remember, in this first phase, you will respond using only the left button.', 'space', False],
    'Stim1': [],
    'Break1': ['Take a break!', 'space', True],
    'Stim2': [],
    'Break2': ['Take a break!', 'space', True],
    'Stim4': [],
    '4RTEnd': ['Thank you!', 'space', True]
}

def get_order_file(order_dirs):
    order_list = os.listdir(order_dirs)
    random.shuffle(order_list)
    order_list = order_list[:2]
    return [os.path.join(order_dirs, file) for file in order_list]

def get_order_list(txt_path, practice=False):
    with open(txt_path, 'r') as file:
        order_list = [line.strip() for line in file]
    order_list = [f'{file}.png' for file in order_list]
    if practice:
        new_order_list = []
        for item in order_list:
            new_order_list.append('waiting.png')
            new_order_list.append(item)
            new_order_list.append('feedback')
        return new_order_list[:20]
    else:
        new_order_list = []
        for item in order_list:
            new_order_list.append('waiting.png')
            new_order_list.append(item)
        return new_order_list[:20]

image_text = '/Users/AP-CNL/Desktop/4RT/Stimuli/Images/{}'
one_opt_dirs = '/Users/AP-CNL/Desktop/4RT/Stimuli/Order/1_option'
two_opt_dirs = '/Users/AP-CNL/Desktop/4RT/Stimuli/Order/2_options'
four_opt_dirs = '/Users/AP-CNL/Desktop/4RT/Stimuli/Order/4_options'

one_opt_fname_list = get_order_file(one_opt_dirs)
one_opt_fname = one_opt_fname_list[0]
one_opt_prac_fname = one_opt_fname_list[1]

two_opt_fname_list = get_order_file(two_opt_dirs)
two_opt_fname = two_opt_fname_list[0]
two_opt_prac_fname = two_opt_fname_list[1]

four_opt_fname_list = get_order_file(four_opt_dirs)
four_opt_fname = four_opt_fname_list[0]
four_opt_prac_fname = four_opt_fname_list[1]

stimlist1, stimlist2, stimlist4 = get_order_list(one_opt_fname), get_order_list(two_opt_fname), get_order_list(four_opt_fname)
practicelist1, practicelist2, practicelist4 = get_order_list(one_opt_prac_fname, practice=True), get_order_list(two_opt_prac_fname, practice=True), get_order_list(four_opt_prac_fname, practice=True)

visuals['Stim1'] = [stimlist1, 'c', True]
visuals['Stim2'] = [stimlist2, 'c', True]
visuals['Stim4'] = [stimlist4, 'c', True]
visuals['Practice1'] = [practicelist1, 'c', True]
visuals['Practice2'] = [practicelist2, 'c', True]
visuals['Practice4'] = [practicelist4, 'c', True]

disp = Display(disptype='psychopy', bgc='black')
scr = Screen(disptype='psychopy', bgc='black')
event.Mouse(visible=False)
center_text = psychopy.visual.TextStim(win=pygaze.expdisplay, text='', height=50, wrapWidth=1080)
image = psychopy.visual.ImageStim(win=pygaze.expdisplay, image=None)

image_base_dir = '/Users/AP-CNL/Desktop/4RT/Stimuli/Images'
out_dict = {'sectionname': ['starttime', 'endtime', 'duration', 'responsetime', 'delta', 'condition', 'response', 'accuracy']}
val_dict = {'line.png': 1, 'circle.png': 2, 'triangle.png': 3, 'square.png': 4}
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
image_display_duration = 2.0
image_start_time = 0.0
response_received = False
correct_value = np.nan

def on_click(x, y, button, pressed):
    global current_value, response_received, correct_value
    if pressed:
        if button == pynput_mouse.Button.left:
            current_value = 1
        elif button == pynput_mouse.Button.middle:
            current_value = 2
        elif button == pynput_mouse.Button.x1:
            current_value = 3
        elif button == pynput_mouse.Button.right:
            current_value = 4
        response_received = True

listener = pynput_mouse.Listener(on_click=on_click)
listener.start()

while cont:
    visual_screen = visual_screens[visual_screen_idx]
    center_text.text = visuals[visual_screen][0] if isinstance(visuals[visual_screen][0], str) else ''
    scr.screen.clear()
    scr.screen.append(center_text)

    if not isinstance(visuals[visual_screen][0], str):
        if rep < len(visuals[visual_screen][0]):
            cur_stim = visuals[visual_screen][0][rep]
            if cur_stim == 'feedback':
                while core.getTime() - image_start_time < image_display_duration:
                    if response_received:
                        if correct_value == current_value:
                            center_text.text = "Correct"
                        else:
                            center_text.text = "Incorrect"
                        scr.screen.clear()
                        scr.screen.append(center_text)
                        disp.fill(screen=scr)
                        disp.show()
                        core.wait(1)
                        break
                if not response_received:
                    center_text.text = "Too Slow"
                    scr.screen.clear()
                    scr.screen.append(center_text)
                    disp.fill(screen=scr)
                    disp.show()
                    core.wait(1)
            else:
                if '1' in visual_screen:
                    pre_text = '1_option'
                elif '2' in visual_screen:
                    pre_text = '2_options'
                else:
                    pre_text = '4_options'

                if cur_stim != 'waiting.png':
                    correct_value = val_dict[cur_stim]
                if cur_stim == 'waiting.png':
                    image.setImage(image_text.format(f'{pre_text}/{cur_stim}'))
                    scr.screen.append(image)
                    disp.fill(screen=scr)
                    disp.show()
                    core.wait(round(random.uniform(1, 4), 2))
                else:
                    image.setImage(image_text.format(f'{pre_text}/{cur_stim}'))
                    scr.screen.append(image)
                    image_start_time = core.getTime()
                    response_received = False
                    disp.fill(screen=scr)
                    disp.show()
                    while core.getTime() - image_start_time < image_display_duration:
                        if response_received:
                            break
            rep += 1
        else:
            rep = 0
            visual_screen_idx += 1
            if visual_screen_idx >= len(visual_screens):
                cont = False
    else:
        disp.fill(screen=scr)
        disp.show()
        if visuals[visual_screen][1] == 'space':
            keys = event.waitKeys(keyList=['space', 'escape'])
            if 'escape' in keys:
                print("Escape key pressed. Exiting...")
                cont = False
            else:
                visual_screen_idx += 1
                if visual_screen_idx >= len(visual_screens):
                    cont = False
        else:
            core.wait(1)
            visual_screen_idx += 1
            if visual_screen_idx >= len(visual_screens):
                cont = False

df = pd.DataFrame(out_dict)
df = df.transpose()
df.to_csv(args.filename)
disp.close()