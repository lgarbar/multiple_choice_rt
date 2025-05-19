# 4RT Task Script

## Description

`4rt.py` is a Python script designed to present a cognitive task involving visual stimuli and mouse button responses. The task presents a series of instructions and stimuli, requiring participants to respond to the stimuli using specific mouse button presses. The script records the timing and accuracy of these responses, outputting the data to a CSV file.

## Use

The script is intended for use in psychological experiments or cognitive assessments where precise timing and response recording are necessary.

## Setup and Installation

### Prerequisites

Before running the script, ensure you have the following installed:

*   **Python 3.x**: The script is written in Python 3.
*   **Psychopy**: A library for creating behavioral experiments.
*   **Pygaze**: A library for eye tracking and experiment control (though eye tracking functionality may not be fully implemented in this script).
*   **Pynput**: A library to control and monitor input devices such as mouse and keyboard.
*   **Pandas**: A library for data manipulation and analysis.
*   **Numpy**: A library for numerical computations.
*   **Matplotlib**: A library for creating visualizations (though visualizations may not be directly created by this script).

### Installation Instructions

1.  **Install Python**: If you don't have Python installed, download it from [python.org](https://www.python.org/) and follow the installation instructions.

2.  **Install Required Libraries**: Open a terminal or command prompt and run the following command to install the necessary libraries:

    ```bash
    pip install psychopy pygaze pynput pandas numpy matplotlib
    ```

### Directory Structure

The script expects a specific directory structure for stimuli and order files:

*   `Stimuli/`: Contains all stimuli-related files.
    *   `Images/`: Contains the image files used as stimuli.
        *   `1_option/`: Images for the first block of trials.
        *   `2_options/`: Images for the second block of trials.
        *   `4_options/`: Images for the third block of trials.
    *   `Order/`: Contains the order files (text files listing image names).
        *   `1_option/`: Order files for the first block of trials.
        *   `2_options/`: Order files for the second block of trials.
        *   `4_options/`: Order files for the third block of trials.

Ensure that the paths defined in the script (`image_text`, `one_opt_dirs`, `two_opt_dirs`, `four_opt_dirs`) match your actual directory structure.

## Running the Script

To run the script, execute the following command in the terminal or command prompt:

bash
```
python Stimuli/4rt.py --filename <output_file_name.csv>
```

### Command-Line Arguments

*   `--filename`: Specifies the name of the output CSV file where the data will be saved. This argument is required.

## Output

The script generates a CSV file containing the data recorded during the task. The CSV file includes the following columns:

*   `sectionname`: The name of the section or trial (e.g., instruction, stimulus).
*   `starttime`: The start time of the section.
*   `endtime`: The end time of the section.
*   `duration`: The duration of the section.
*   `responsetime`: The time at which the participant responded.
*   `delta`: The time difference between the stimulus onset and the response.
*   `condition`: The stimulus condition.
*   `response`: The participant's response (mouse button pressed).
*   `accuracy`: Whether the response was correct (1) or incorrect (0).

## Customization

### Visual Stimuli

The visual stimuli and instructions are defined in the `visuals` dictionary within the script. You can modify this dictionary to change the content and order of the stimuli.

### Order Files

The order of stimuli is determined by the text files located in the `Stimuli/Order/` directories. Each text file lists the names of the image files to be presented in a specific block of trials.

### Response Mapping

The mapping between mouse buttons and responses is defined in the `on_click` function. You can modify this function to change the response mapping.

### Timing

The timing of the task (e.g., stimulus duration, inter-trial interval) can be adjusted by modifying the `image_display_duration` variable and other timing-related parameters in the script.

## Notes

*   Ensure that the image files used as stimuli are located in the correct directories and that the file names match the names listed in the order files.
*   The script uses the `psychopy` and `pygaze` libraries for display and timing. Make sure these libraries are properly installed and configured.
*   The script records mouse button responses using the `pynput` library. Ensure that the necessary permissions are granted for the script to access the mouse.

# TODO
* Update practice blocks (no practicing each condition in a separate block. Rather, 2 blocks of quad choice blocks: block 1 - spatial cue; block 2: central presentation)
* Update each experimental block to have 2 subblocks: block 1 - spatial cue; block 2: central presentation

