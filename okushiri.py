from swe.bottom import Bathymetry2D
from swe.model import swe2D
from swe.video import save_video2D
from swe.global_var import g
from swe.utils import interpolate_depth2D, interpolate_input_wave

import numpy as np
import pandas as pd
from scipy import interpolate

import time

# loading data
# https://nctr.pmel.noaa.gov/benchmark/Laboratory/Laboratory_MonaiValley/index.html

df_bottom = pd.read_csv("data/MonaiValley_Bottom.csv")
df_input_wave = pd.read_csv("data/MonaiValley_InputWave.csv")

# bottom profile
x, y, d = interpolate_depth2D(df_bottom, dx=0.025, dy=0.025)
bathymetry = Bathymetry2D(x, y, d)

# wave
g = 9.8
H = d.max()
c = np.sqrt(g * H)
dt = 0.5 / (c * np.sqrt(1/bathymetry.dx**2 + 1/bathymetry.dy**2))
t_max = 22
t, input_wave = interpolate_input_wave(df_input_wave, dt, t_min=0, t_max=t_max)

if __name__ == '__main__':
    start = time.time()

    # E, _, _ = swe2D(bathymetry, dt, t_max, input_wave, i0=1, i1=x.shape[0]-1, j0=1, j1=y.shape[0]-1, verbose=1)
    E, _, _ = swe2D(bathymetry, t, boundary_condition={'left': input_wave, 'right': 0, 'top': 0, 'bottom': 0}, eps=1e-6, linearity='non-linear')
    end_1 = time.time()
    print(f'SWE finished in {end_1 - start} s')

    save_video2D('okushiri_.mp4', bathymetry, E, dt=dt, fps=1)
    end_2 = time.time()
    print(f'Saving video finished in {end_2 - end_1} s')
