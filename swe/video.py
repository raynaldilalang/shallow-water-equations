import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

def save_video1D(file, bathymetry, E, dt=1, fps=12, n_frames=None):
    x, d = bathymetry.x, bathymetry.d
    zmin = -np.abs(d).max()
    zmax = -zmin
    
    if n_frames is None:
        n_frames = E.shape[1]
    duration = dt * n_frames
    
    fps = min(fps, 1/dt)
    n_frames = int(duration * fps)
    skipped = E.shape[1] / n_frames
    
    def init():
        for line in plot:
            line.set_data([],[])
        return plot

    def update_plot(frame_number):
        n = int(frame_number * skipped)
        plot[0].set_data(x, E[:, n])
        plot[1].set_data(x, -d)
        return plot[0], plot[1]

    fig, ax = plt.subplots()
    plt.close()

    ax.set_xlim((x[0], x[-1]))
    ax.set_ylim((zmin, zmax))

    plot = [None] * 2
    plot[0], = ax.plot([], [], lw=2)
    plot[1], = ax.plot([], [], lw=2)
    ani = animation.FuncAnimation(fig, update_plot, frames=n_frames, interval=1000/fps, init_func=init, blit = True)
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=fps)
    ani.save(file, writer=writer)
    plt.close()

def save_video2D(file, bathymetry, E, dt=1, fps=1, n_frames=None):
    X, Y, d = bathymetry.X, bathymetry.Y, bathymetry.d
    zmin = -np.abs(d).max()
    zmax = -zmin
    
    if n_frames is None:
        n_frames = E.shape[2]
    duration = dt * n_frames
    
    fps = min(fps, 1/dt)
    n_frames = int(duration * fps)
    skipped = E.shape[2] / n_frames
    
    def update_plot(frame_number, z, plots):
        n = int(frame_number * skipped)
        ax.view_init(45, -120)
        z_masked = np.where(z[:, :, n] > -d, z[:, :, n], np.nan)
        z_masked = np.ma.masked_invalid(z_masked)
        plots[0].remove()
        plots[0] = ax.plot_surface(X, Y, -d, color='C1')
        plots[1].remove()
        plots[1] = ax.plot_surface(X, Y, z_masked, cmap='winter',
                                  rstride=1, cstride=1, vmin=zmin, vmax=zmax)
        return plots
        
    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111, projection='3d', xlabel='x', ylabel='y')
    ax.set_zlim(zmin, zmax)
    ax.view_init(45, -120)
    E_masked = np.where(E[:, :, 0] > -d, E[:, :, 0], np.nan)
    E_masked = np.ma.masked_invalid(E_masked)
    plots = [ax.plot_surface(X, Y, -d, color='C1'),
             ax.plot_surface(X, Y, E_masked, cmap='winter',
                             rstride=1, cstride=1, vmin=zmin, vmax=zmax)]
    ani = animation.FuncAnimation(fig, update_plot, frames=n_frames, fargs=(E, plots), interval=1000/fps, blit=True)
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=fps)
    ani.save(file, writer=writer)
    plt.close()