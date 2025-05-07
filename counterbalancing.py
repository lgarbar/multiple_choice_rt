import numpy as np
import pandas as pd
from brainiak.utils.fmrisim import generate_stimfunction, convolve_hrf
import os

np.random.seed(42)

n_trials = 120
stim_duration = 2
min_iti = 0.5
max_iti = 4
TR = 2
temporal_resolution = 0.1
n_schedules = 200

output_dir = "/Users/danielgarcia-barnett/Desktop/4RT/Stimuli/Order/1_option"
os.makedirs(output_dir, exist_ok=True)

def generate_schedule():
    onsets = []
    curr_time = 0
    itis = np.random.uniform(min_iti, max_iti, n_trials)

    for iti in itis:
        curr_time += iti
        onsets.append(curr_time)
        curr_time += stim_duration

    return np.array(onsets)
def evaluate_schedule(onsets, total_time):
    durations = [stim_duration] * len(onsets)
    stim_func = generate_stimfunction(
        [onsets],  # wrap onsets inside a list
        [durations],  # wrap durations inside a list
        total_time,
        temporal_resolution
    )
    hrf_signal = convolve_hrf(stim_func, tr_duration=temporal_resolution)
    design = hrf_signal[::int(TR / temporal_resolution)]
    return design

best_score = float('inf')
best_onsets = None
best_design = None

for _ in range(n_schedules):
    onsets = generate_schedule()
    total_time = int(onsets[-1] + stim_duration + 10)
    design = evaluate_schedule(onsets, total_time)
    corr = np.corrcoef(design.T)
    score = np.abs(corr[0, 0] - 1)
    if score < best_score:
        best_score = score
        best_onsets = onsets
        best_design = design

df = pd.DataFrame({
    'onset': best_onsets,
    'duration': [stim_duration] * len(best_onsets),
    'trial_type': ['line'] * len(best_onsets)
})

df.to_csv(os.path.join(output_dir, "optimized_schedule.csv"), index=False)