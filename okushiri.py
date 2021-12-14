from swe.bottom import Bathymetry
from swe.model import swe
from swe.video import save_video2D
from swe.global_var import g
from swe.utils import interpolate_depth, interpolate_input_wave

import numpy as np
import pandas as pd
from scipy import interpolate

import time

# loading data
# https://nctr.pmel.noaa.gov/benchmark/Laboratory/Laboratory_MonaiValley/index.html

df_bottom = pd.read_csv("data/MonaiValley_Bottom.csv")
df_input_wave = pd.read_csv("data/MonaiValley_InputWave.csv")

# bottom profile
x, y, d = interpolate_depth(df_bottom, dx=0.025, dy=0.025)
bathymetry = Bathymetry(x, y, d)

# wave
g = 9.8
H = d.max()
c = np.sqrt(g * H)
dt = 0.5 / (c * np.sqrt(1/bathymetry.dx**2 + 1/bathymetry.dy**2))
input_wave = interpolate_input_wave(df_input_wave, dt)
t_max = 22

if __name__ == '__main__':
    start = time.time()

    E, _, _ = swe(bathymetry, dt, t_max, input_wave, verbose=1)
    end_1 = time.time()
    print(f'SWE finished in {end_1 - start} s')

    save_video2D('okushiri.mp4', bathymetry, E, dt=dt, fps=1)
    end_2 = time.time()
    print(f'Saving video finished in {end_2 - end_1} s')
