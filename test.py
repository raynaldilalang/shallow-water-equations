from swe.bottom import Bathymetry
from swe.model import swe
from swe.video import save_video2D
from swe.global_var import g

import numpy as np

# bottom profile
dx = 0.5
dy = 0.5
x = np.arange(-100, 20 + dx/2, dx)
y = np.arange(-10, 10 + dy/2, dy)
X, Y = np.meshgrid(x,y)
X, Y = X.T, Y.T
d = - X / 20
bathymetry = Bathymetry(x, y, d)

# wave
g = 9.8
H = d.max()
c = np.sqrt(g * H)
dt = 0.5 / (c * np.sqrt(1/dx**2 + 1/dy**2))
t_max = 60
t = np.arange(0, t_max, dt)
A = 0.2
omega =  2 * np.pi / 30
input_wave = A * np.sin(omega * t)

if __name__ == '__main__':
    E, _, _ = swe(bathymetry, dt, t_max, input_wave)
    save_video2D('test.mp4', bathymetry, E, dt=dt, fps=1)
