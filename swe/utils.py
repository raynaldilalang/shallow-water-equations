import numpy as np
import pandas as pd
from scipy import interpolate


def interpolate_depth1D(df_bottom, dx):
    bottom_func = interpolate.interp1d(df_bottom.iloc[:, 0], df_bottom.iloc[:, 1])
    x = np.arange(df_bottom.iloc[:, 0].min(), df_bottom.iloc[:, 0].max(), dx)
    d = bottom_func(x)

    return x, d


def interpolate_depth2D(df_bottom, dx, dy):
    df_bottom = df_bottom.pivot(index='x', columns='y', values='z')
    d_old = df_bottom.to_numpy()
    x_old, y_old = df_bottom.index.to_numpy(), df_bottom.columns.to_numpy()
    Nx_old, Ny_old = x_old.shape[0], y_old.shape[0]
    x_min, y_min = x_old.min(), y_old.min()
    x_max, y_max = x_old.max(), y_old.max()

    x, y = np.arange(x_min, x_max, dx), np.arange(y_min, y_max, dy)
    Nx, Ny = x.shape[0], y.shape[0]
    d_mid = np.zeros((Nx_old, Ny))
    for i in range(Nx_old):
        depth_func = interpolate.interp1d(y_old, d_old[i, :], kind='linear')
        d_mid[i, :] = depth_func(y)

    d = np.zeros((Nx, Ny))
    for j in range(Ny):
        depth_func = interpolate.interp1d(x_old, d_mid[:, j], kind='linear')
        d[:, j] = depth_func(x)

    del x_old, y_old, d_old, d_mid, depth_func

    return x, y, d


def interpolate_input_wave(df_input_wave, dt):
    input_wave_func = interpolate.interp1d(df_input_wave.iloc[:, 0], df_input_wave.iloc[:, 1])
    t = np.arange(df_input_wave.iloc[:, 0].min(), df_input_wave.iloc[:, 0].max(), dt)
    input_wave = input_wave_func(t)

    return t, input_wave