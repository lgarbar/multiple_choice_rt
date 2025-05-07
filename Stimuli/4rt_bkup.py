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

# Define image paths (using f-strings for clarity)
# These specific paths for waiting/break images seem unused in the loop logic,
# which builds paths dynamically. Keeping them for reference but they aren't
# directly used to load images in the main loop.
waiting_1 = 'Stimuli/Images/1_option/options.png'
waiting_2 = 'Stimuli/Images/2_options/options.png'
waiting_4 = 'Stimuli/Images/4_options/options.png'
break_1 = 'Stimuli/Images/1_option/break.png'
break_2 = 'Stimuli/Images/2_options/break.png'
break_4 = 'Stimuli/Images/4_options/break.png'

# Corrected paths for base images used in Feedback/Break lists
# These are now only used if you decide to make Feedback/Break image-based again.
# Reverting Feedback/Break to text screens for now.
# break_image_path = 'Stimuli/Images/break.png'
# options_image_path = 'Stimuli/Images/options.png'


visuals = {
    '4RTStart': ['Next activity starting soon.', 'space', True], # Text screen
    'Instructions1': ["You will see images presented on the screen that correspond to the buttons on the device you are holding.\n\nWhen the image appears, press the corresponding button.", 'space', False], # Text screen
    'Instructions2': ["At first, only the stimulus that matches the left button will appear,\n\nand so you'll only be responding using that left button.\n\nGo ahead and press the left button once you see the diagonal line appear on screen.", 'space', False], # Text screen
    'Example1': [['line.png', 'feedback'], 'c', True], # List of items (stimulus, feedback)
    'Instructions3': ["Next, the stimuli that match the left or right buttons will appear,\n\nso you'll have to respond using the left or right buttons.\n\nGo ahead and press the right button once you see the square appear on screen.", 'space', False], # Text screen
    'Example2': [['square.png', 'feedback'], 'c', True], # List of items (stimulus, feedback)
    'Instructions4': ["In the final phase, you will respond to any of the four stimuli using all four buttons.\n\nGo ahead and press the middle button with the circle once you see the circle appear on screen.", 'space', False], # Text screen
    'Example4': [['circle.png', 'feedback'], 'c', True], # List of items (stimulus, feedback)
    'Instructions5': ['Now you will have a chance to practice the task before moving on to the first phase.\n\nPay attention to the instructions on screen to know which stimuli could appear.', 'space', False], # Text screen
    # Revert Feedback screens to text, content will be set dynamically based on accuracy
    'Feedback1': [['options.png'], 'space', True], # Text screen (content will be set dynamically)
    'Practice1': [], # Initial empty list, will be replaced with generated list
    # Revert Feedback screens to text
    'Feedback2': [['options.png'], 'space', True], # Text screen (content will be set dynamically)
    'Practice2': [], # Initial empty list, will be replaced
    # Revert Feedback screens to text
    'Feedback3': [['options.png'], 'space', True], # Text screen (content will be set dynamically)
    'Practice4': [], # Initial empty list, will be replaced
    'Instructions6': ['Good job on the practice trials. You can now move on to the test trials.\n\nYou will do the same task as in the practice, completing a distinct blocks of trials for each of the phases described earlied.\n\nEach block will last about 3-5 minutes long. You will have a short break in between these trials.', 'space', False], # Text screen
    # Revert Break screens to text
    'Break1': [['options.png'], 'space', True], # Text screen
    'Stim1': [], # Initial empty list, will be replaced
    # Revert Break screens to text
    'Break2': [['break.png'], 'space', True], # Text screen
    'Stim2': [], # Initial empty list, will be replaced
    # Revert Break screens to text
    'Break4': [['break.png'], 'space', True], # Text screen
    'Stim4': [], # Initial empty list, will be replaced
    '4RTEnd': ['Thank you!', 'space', True] # Text screen
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
    new_order_list = []
    for item in order_list:
        new_order_list.append('waiting.png')
        new_order_list.append(item)
        if practice:
            new_order_list.append('feedback')
    # Reverted truncation [:20] to use the full list, matching flanker.py behavior
    return new_order_list

# Use relative paths if the script is run from the project root
image_text = 'Stimuli/Images/{}'
one_opt_dirs = 'Stimuli/Order/1_option'
two_opt_dirs = 'Stimuli/Order/2_options'
four_opt_dirs = 'Stimuli/Order/4_options'

one_opt_fname_list = get_order_file(one_opt_dirs)
one_opt_fname = one_opt_fname_list[0]
one_opt_prac_fname = one_opt_fname_list[1]

two_opt_fname_list = get_order_file(two_opt_dirs)
two_opt_fname = two_opt_fname_list[0]
two_opt_prac_fname = two_opt_fname_list[1]

four_opt_fname_list = get_order_file(four_opt_dirs)
four_opt_fname = four_opt_fname_list[0]
four_opt_prac_fname = four_opt_fname_list[1]

stimlist1, stimlist2, stimlist4 = get_order_list(one_opt_fname), get_order_list(two_opt_fname), get_order_list(four_opt_fname) # Corrected order to match Stim1, Stim2, Stim4
practicelist1, practicelist2, practicelist4 = get_order_list(one_opt_prac_fname, practice=True), get_order_list(two_opt_prac_fname, practice=True), get_order_list(four_opt_prac_fname, practice=True) # Corrected order to match Practice1, Practice2, Practice4

# Corrected assignments: Replace the entire list value for these keys
# The structure is [list_of_items, wait_condition, log_data_bool]
visuals['Stim1'] = [stimlist1, 'c', True] # Stim1 uses 4_options list
visuals['Stim2'] = [stimlist2, 'c', True] # Stim2 uses 2_options list
visuals['Stim4'] = [stimlist4, 'c', True] # Stim4 uses 1_option list
visuals['Practice1'] = [practicelist1[:20], 'c', True] # Practice1 uses 1_option list
visuals['Practice2'] = [practicelist2[:20], 'c', True] # Practice2 uses 2_options list
visuals['Practice4'] = [practicelist4[:20], 'c', True] # Practice4 uses 4_options list


disp = Display(disptype='psychopy', bgc='black')
scr = Screen(disptype='psychopy', bgc='black')
event.Mouse(visible=False)
center_text = psychopy.visual.TextStim(win=pygaze.expdisplay, text='', height=50, wrapWidth=1080)
image = psychopy.visual.ImageStim(win=pygaze.expdisplay, image=None)

val_dict = {'line.png': 1, 'circle.png': 2, 'triangle.png': 3, 'square.png': 4}

# Variables to store outcome of the last stimulus trial for feedback
last_stim_responsetime = None
last_stim_accuracy = None
last_stim_response = None

# Variables for stimulus trials (used within the item processing)
response_received = False
correct_value = np.nan
current_value = None # Value from pynput listener

# List to collect accuracies for a block (used for Feedback screens)
accuracy_list = []

# Data dictionary
out_dict = {'sectionname': ['starttime', 'endtime', 'duration', 'responsetime', 'delta', 'condition', 'response', 'accuracy']}

def on_click(x, y, button, pressed):
    global current_value, response_received
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

cont = True
visual_screens = list(visuals.keys())
visual_screen_idx = 0
task_clock = core.Clock()
current_rep = 0 # Index within a list of stimuli/items

# Define stimulus display duration
image_display_duration = 2.0

while cont:
    visual_screen_name = visual_screens[visual_screen_idx]
    visual_screen_data = visuals[visual_screen_name]
    screen_content = visual_screen_data[0]
    screen_wait_condition = visual_screen_data[1] # Screen-level wait condition (only used for text screens)
    log_screen_data = visual_screen_data[2] # Log data for the screen itself? (Used for text screens)

    scr.screen.clear() # Clear screen from previous item/screen

    if isinstance(screen_content, str): # Text screen (Instructions, Break, Start, End, Feedback)
        item_starttime = task_clock.getTime() # Log start time for text screen
        item_condition = None # Condition is None for text screens
        item_responsetime = None
        item_response = None
        item_accuracy = None
        item_delta = None

        if 'Feedback' in visual_screen_name:
            # Calculate accuracy for the preceding practice block
            if accuracy_list:
                mean_accuracy = np.mean(accuracy_list)
                if mean_accuracy >= 0.75 or visual_screen_name == 'Feedback3': # Assuming Feedback3 is the last practice feedback
                    center_text.text = 'Good job!'
                else:
                    center_text.text = 'Good job! You will now do another practice round. Remember to respond only to the central arrow' # This text might need adjustment based on which practice block failed
                item_accuracy = mean_accuracy # Log the mean accuracy for the feedback screen entry
            else:
                 center_text.text = 'No practice trials completed.' # Should not happen in normal flow
            accuracy_list = [] # Clear accuracy list after feedback

        else: # Other text screens (Instructions, Break, Start, End)
            center_text.text = screen_content

        scr.screen.append(center_text)
        disp.fill(screen=scr)
        disp.show()

        # Wait for screen-level input (usually 'space')
        if screen_wait_condition == 'space':
            keys = event.waitKeys(keyList=['space', 'escape'])
            if 'escape' in keys:
                print("Escape key pressed. Exiting...")
                cont = False
            else:
                item_endtime = task_clock.getTime() # Log end time
                item_duration = item_endtime - item_starttime # Log duration
                # Log data for the text screen
                if log_screen_data:
                     out_dict[visual_screen_name] = [item_starttime, item_endtime, item_duration, item_responsetime, item_delta, item_condition, item_response, item_accuracy]
                visual_screen_idx += 1
                current_rep = 0 # Reset rep for the next screen
                if visual_screen_idx >= len(visual_screens):
                    cont = False
        else:
             # Should not happen for text screens based on visuals dict
             pass # Or handle other screen_wait_conditions if needed for text screens

    elif isinstance(screen_content, list): # List of items (Examples, Practice, Stim)
        if current_rep < len(screen_content):
            cur_item = screen_content[current_rep]

            # Reset item-specific response variables
            item_responsetime = None
            item_response = None
            item_accuracy = None
            item_condition = None # Will be set for specific item types
            item_delta = None

            if cur_item == 'waiting.png':
                # Display waiting image
                pre_text = '1_option' if '1' in visual_screen_name else ('2_options' if '2' in visual_screen_name else '4_options')
                image.setImage(image_text.format(f'{pre_text}/{cur_item}'))
                scr.screen.append(image)
                disp.fill(screen=scr)
                disp.show()

                item_starttime = task_clock.getTime() # Log start time
                item_condition = cur_item.split('.')[0] # Log condition as waiting

                # Wait for random duration
                wait_duration = round(random.uniform(0.5, 3), 2)
                core.wait(wait_duration)

                item_endtime = task_clock.getTime() # Log end time
                item_duration = item_endtime - item_starttime
                item_delta = None # No response expected

                # Log data for waiting screen
                item_key = f"{visual_screen_name}_{current_rep}"
                out_dict[item_key] = [item_starttime, item_endtime, item_duration, item_responsetime, item_delta, item_condition, item_response, item_accuracy]

                current_rep += 1 # Move to next item

            elif cur_item == 'feedback':
                # Display feedback based on the *previous* stimulus trial's outcome
                if last_stim_responsetime is None: # Timeout on previous trial
                    center_text.text = "Too Slow."
                elif last_stim_accuracy == 1: # Correct on previous trial
                    center_text.text = "Correct!"
                else: # Incorrect on previous trial
                    center_text.text = "Incorrect."

                scr.screen.append(center_text)
                disp.fill(screen=scr)
                disp.show()

                item_starttime = task_clock.getTime() # Log start time
                item_condition = cur_item # Log condition as feedback

                # Wait for a short duration (e.g., 1 second)
                core.wait(1.0)

                item_endtime = task_clock.getTime() # Log end time
                item_duration = item_endtime - item_starttime
                item_delta = None # No response expected

                # Log data for feedback screen
                item_key = f"{visual_screen_name}_{current_rep}"
                out_dict[item_key] = [item_starttime, item_endtime, item_duration, item_responsetime, item_delta, item_condition, item_response, item_accuracy]

                current_rep += 1 # Move to next item

            # Handle list items that are images (stimuli)
            elif cur_item.endswith('.png'):
                # Determine image path prefix for subfolders
                pre_text = '1_option' if '1' in visual_screen_name else ('2_options' if '2' in visual_screen_name else '4_options')
                image_path = image_text.format(f'{pre_text}/{cur_item}') # Use subfolder path

                image.setImage(image_path)
                scr.screen.append(image)
                disp.fill(screen=scr)
                disp.show()

                item_starttime = task_clock.getTime() # Log start time
                item_condition = cur_item.split('.')[0] # Log condition as image name

                # This is a stimulus image, it expects a response
                # Determine correct value for stimulus
                if cur_item in val_dict:
                    correct_value = val_dict[cur_item]
                else:
                    correct_value = np.nan # Should not happen for actual stimuli

                # Reset response variables for this stimulus trial
                response_received = False
                current_value = None # Value from pynput listener
                item_responsetime = None
                item_response = None
                item_accuracy = 0 # Assume incorrect/timeout initially

                # Wait for response or timeout
                while task_clock.getTime() - item_starttime < image_display_duration:
                    keys = event.getKeys(keyList=['escape'])
                    if 'escape' in keys:
                        print("Escape key pressed. Exiting...")
                        cont = False
                        break # Exit inner loop
                    if response_received:
                        item_responsetime = task_clock.getTime() # Log response time
                        # Determine response string
                        if current_value == 1: item_response = 'left'
                        elif current_value == 2: item_response = 'middle_l'
                        elif current_value == 3: item_response = 'middle_l'
                        elif current_value == 4: item_response = 'right'
                        # Calculate accuracy
                        if correct_value is not np.nan and current_value == correct_value:
                            item_accuracy = 1
                        else:
                            item_accuracy = 0 # Incorrect button
                        break # Exit inner loop

                # Store outcome for potential feedback item that follows
                last_stim_responsetime = item_responsetime
                last_stim_accuracy = item_accuracy
                last_stim_response = item_response

                # Append accuracy to list for block feedback
                if item_accuracy is not None:
                    accuracy_list.append(item_accuracy)


                item_endtime = task_clock.getTime() # Log end time
                item_duration = item_endtime - item_starttime # Log duration
                item_delta = item_responsetime - item_starttime if item_responsetime is not None else None # Log delta

                # Log data for this stimulus trial
                item_key = f"{visual_screen_name}_{current_rep}"
                out_dict[item_key] = [item_starttime, item_endtime, item_duration, item_responsetime, item_delta, item_condition, item_response, item_accuracy]

                current_rep += 1 # Move to next item


        else: # Finished the list for this visual_screen
            current_rep = 0 # Reset rep for the next screen
            visual_screen_idx += 1
            if visual_screen_idx >= len(visual_screens):
                cont = False

# End of while cont loop

# Stop the pynput listener
listener.stop()

# Save data
# Use from_dict with orient='index' to handle keys as row labels
df = pd.DataFrame.from_dict(out_dict, orient='index', columns=['starttime', 'endtime', 'duration', 'responsetime', 'delta', 'condition', 'response', 'accuracy'])
df.index.name = 'sectionname' # Set the index name for the index column
df.to_csv(args.filename)

disp.close()