from .global_var import g

import numpy as np
from tqdm import tqdm


def swe1D(bathymetry, t, input_wave, eps=1e-3, verbose=1):
    
    d = bathymetry.d
    
    dx = bathymetry.dx
    Nx = bathymetry.x.shape[0]
    
    dt = t[1] - t[0]
    Nt = t.shape[0]
    S = dt / dx
    
    e = np.zeros((Nx, Nt)) 
    u = np.zeros((Nx + 1, Nt))
    
    p = np.zeros((Nx + 1))
    hx = np.zeros((Nx + 1))

    i0 = 1
    loop = range(Nt - 1)
    if verbose == 1:
        loop = tqdm(loop)
    for n in loop:
        
        e0 = e[:, n]
        u0 = u[:, n]
        e1 = e[:, n+1]
        u1 = u[:, n+1]
        
        e0[0] = input_wave[0]
        e0[:] = np.maximum(e0, -d)

        hx[:], p[:] = _upwind1D(d, e0, u0, hx, p)


        # calculate e(x, y, t_{n + 1})
        e1[0] = input_wave[n + 1]
        e1[i0:] = e0[i0:] - S * (p[i0 + 1:] - p[i0:-1])
        e1[:] = np.maximum(e1, -d)
        h = d + e1
        
        # calculate u(x, y, t_{n + 1})
        wetx = h[i0 + 1:Nx] + h[i0:Nx - 1] > eps
        # wetx = (h[i0 + 1:Nx] > eps) & (h[i0:Nx - 1] > eps)
        pb1 = wetx * (p[i0:Nx - 1] + p[i0 + 1:Nx]) / 2
        pb2 = wetx * (p[i0 + 1:Nx] + p[i0 + 2:Nx + 1]) / 2
        u_1 = wetx * ((pb1 > 0) * u0[i0:Nx - 1] + (pb1 < 0) * u0[i0 + 1:Nx])
        u_2 = wetx * ((pb2 > 0) * u0[i0 + 1:Nx] + (pb2 < 0) * u0[i0 + 2:Nx + 1])
        hbarx = wetx * (h[i0:Nx - 1] + h[i0 + 1:Nx]) / 2
        hbarx[hbarx == 0] = -1
        uux = np.where(wetx > 0, (1 / hbarx) * (pb2 * u_2 - pb1 * u_1 - u0[i0 + 1:Nx] * (pb2 - pb1)), 0)
        uux = np.ma.fix_invalid(uux, fill_value=0).data
        u1[i0 + 1:Nx] = wetx * (u0[i0 + 1:Nx] - g * S * (e1[i0 + 1:Nx] - e1[i0:Nx - 1]) - S * uux)
        u1[i0] = u0[i0] - g * S * (e1[i0] - e1[i0 - 1])
        u1[-1] = 0

    return e, u


def swe2D(bathymetry, t, input_wave, eps=0, verbose=1):
    
    d = bathymetry.d
    
    dx = bathymetry.dx
    dy = bathymetry.dy
    Nx = bathymetry.x.shape[0]
    Ny = bathymetry.y.shape[0]
    
    dt = t[1] - t[0]
    Nt = t.shape[0]
    S1 = dt / dx
    S2 = dt / dy
    
    e = np.zeros((Nx, Ny, Nt)) 
    u = np.zeros((Nx + 1, Ny, Nt)) 
    v = np.zeros((Nx, Ny + 1, Nt))
    
    p = np.zeros((Nx + 1, Ny))
    q = np.zeros((Nx, Ny + 1))
    hx = np.zeros((Nx + 1, Ny))
    hy = np.zeros((Nx, Ny + 1))

    i0 = 1
    loop = range(Nt - 1)
    if verbose == 1:
        loop = tqdm(loop)
    for n in loop:
        
        e0 = e[:, :, n]
        u0 = u[:, :, n]
        v0 = v[:, :, n]
        e1 = e[:, :, n+1]
        u1 = u[:, :, n+1]
        v1 = v[:, :, n+1]
        
        e0[0, :] = input_wave[0]
        e0[:, :] = np.maximum(e0, -d)

        hx[:, :], p[:, :] = _upwind2D(d, e0, u0, hx, p)
        hy[:, :], q[:, :] = _upwind2D(d, e0, v0, hy, q, transpose=True)


        # calculate e(x, y, t_{n + 1})
        e1[0, :] = input_wave[n + 1]
        e1[i0: Nx + 1, :] = (
            e0[i0: Nx + 1, :] - \
            S1 * (p[i0 + 1: Nx + 1, :] - p[i0: Nx, :]) - \
            S2 * (q[i0: Nx + 1, 1: Ny + 1] - q[i0: Nx + 1, 0: Ny])
        )
        e1[:, :] = np.maximum(e1, -d)
        h = d + e1
        
        # calculate u(x, y, t_{n + 1})
        wetx = np.zeros((Nx - 1 - i0, Ny))
        wetx[(h[i0 + 1:Nx, :] > eps) & (h[i0:Nx - 1, :] > eps)] = 1
        pb1x = wetx * (p[i0:Nx - 1, :] + p[i0 + 1:Nx, :]) / 2
        pb2x = wetx * (p[i0 + 1:Nx, :] + p[i0 + 2:Nx + 1, :]) / 2
        u_1x = wetx * ((pb1x > 0) * u0[i0:Nx - 1, :] + (pb1x < 0) * u0[i0 + 1:Nx, :])
        u_2x = wetx * ((pb2x > 0) * u0[i0 + 1:Nx, :] + (pb2x < 0) * u0[i0 + 2:Nx + 1, :])
        qb1x = wetx[:, 1:Ny - 1] * (q[i0:Nx - 1, 1:Ny - 1] + q[i0 + 1:Nx, 1:Ny - 1]) / 2
        qb2x = wetx[:, 1:Ny - 1] * (q[i0:Nx - 1, 2:Ny] + q[i0 + 1:Nx, 2:Ny]) / 2
        u_1y = wetx[:, 1:Ny - 1] * ((qb1x > 0) * u0[i0 + 1:Nx, 0:Ny - 2] + (qb1x < 0) * u0[i0 + 1:Nx, 1:Ny - 1])
        u_2y = wetx[:, 1:Ny - 1] * ((qb2x > 0) * u0[i0 + 1:Nx, 1:Ny - 1] + (qb2x < 0) * u0[i0 + 1:Nx, 2:Ny])
        hbarx = wetx * (h[i0:Nx - 1, :] + h[i0 + 1:Nx, :]) / 2
        hbarx[hbarx <= eps] = -1
        uux = np.where(hbarx > eps, (1 / hbarx) * (pb2x * u_2x - pb1x * u_1x - u0[i0 + 1:Nx, :] * (pb2x - pb1x)), 0)
        vuy = np.where(hbarx[:, 1:Ny - 1] > eps, (1 / hbarx[:, 1:Ny - 1]) * (qb2x * u_2y - qb1x * u_1y - u0[i0 + 1:Nx, 1:Ny - 1] * (qb2x - qb1x)), 0)
        uux = np.ma.fix_invalid(uux, fill_value=0).data
        vuy = np.ma.fix_invalid(vuy, fill_value=0).data
        u1[i0 + 1:Nx, 1:Ny - 1] = wetx[:, 1:Ny - 1] * (u0[i0 + 1:Nx, 1:Ny - 1] - g * S1 * (e1[i0 + 1:Nx, 1:Ny - 1] - e1[i0:Nx - 1, 1:Ny - 1]) - S1 * uux[:, 1:Ny - 1] - S2 * vuy)
        u1[i0 + 1:Nx, 0] = wetx[:, 0] * (u0[i0 + 1:Nx, 0] - g * S1 * (e1[i0 + 1:Nx, 0] - e1[i0:Nx - 1, 0]) - S1 * uux[:, 0])
        u1[i0 + 1:Nx, -1] = wetx[:, -1] * (u0[i0 + 1:Nx, -1] - g * S1 * (e1[i0 + 1:Nx, -1] - e1[i0:Nx - 1, -1]) - S1 * uux[:, -1])
        u1[i0, :] = u0[i0, :] - g * S1 * (e1[i0, :] - e1[i0 - 1, :])
        u1[-1, :] = 0
        
        # calculate v(x, y, t_{n + 1})
        wety = np.zeros((Nx, Ny - 1))
        wety[(h[:, 1:Ny] > eps) & (h[:, 0:Ny - 1] > eps)] = 1
        qb1y = wety * (q[:, 0:Ny - 1] + q[:, 1:Ny]) / 2
        qb2y = wety * (q[:, 1:Ny] + q[:, 2:Ny + 1]) / 2
        v_1y = wety * ((qb1y > 0) * v0[:, 0:Ny - 1] + (qb1y < 0) * v0[:, 1:Ny])
        v_2y = wety * ((qb2y > 0) * v0[:, 1:Ny] + (qb2y < 0) * v0[:, 2:Ny + 1])
        pb1y = wety[1:Nx - 1, :] * (p[1:Nx - 1, 0:Ny - 1] + p[1:Nx - 1, 1:Ny]) / 2
        pb2y = wety[1:Nx - 1, :] * (p[2:Nx, 0:Ny - 1] + p[2:Nx, 1:Ny]) / 2
        v_1x = wety[1:Nx - 1, :] * ((pb1y > 0) * v0[0:Nx - 2, 1:Ny] + (pb1y < 0) * v0[1:Nx - 1, 1:Ny])
        v_2x = wety[1:Nx - 1, :] * ((pb2y > 0) * v0[1:Nx - 1, 1:Ny] + (pb2y < 0) * v0[2:Nx, 1:Ny])
        hbary = wety * (h[:, 0:Ny - 1] + h[:, 1:Ny]) / 2
        hbary[hbary <= eps] = -1
        vvy = np.where(hbary > eps, (1 / hbary) * (qb2y * v_2y - qb1y * v_1y - v0[:, 1:Ny] * (qb2y - qb1y)), 0)
        uvx = np.where(hbary[1:Nx - 1, :] > eps, (1 / hbary[1:Nx - 1, :]) * (pb2y * v_2x - pb1y * v_1x - v0[1:Nx - 1, 1:Ny] * (pb2y - pb1y)), 0)
        vvy = np.ma.fix_invalid(vvy, fill_value=0).data
        uvx = np.ma.fix_invalid(uvx, fill_value=0).data
        v1[1:Nx - 1, 1:Ny] = wety[1:Nx - 1, :] * (v0[1:Nx - 1, 1:Ny] - g * S2 * (e1[1:Nx - 1, 1:Ny] - e1[1:Nx - 1, 0:Ny - 1]) - S2 * vvy[1:Nx - 1, :] - S1 * uvx)
        v1[0, 1:Ny] = wety[0, :] * (v0[0, 1:Ny] - g * S2 * (e1[0, 1:Ny] - e1[0, 0:Ny - 1]) - S2 * vvy[0, :])
        v1[-1, 1:Ny] = wety[-1, :] * (v0[-1, 1:Ny] - g * S2 * (e1[-1, 1:Ny] - e1[-1, 0:Ny - 1]) - S2 * vvy[-1, :])
        v1[:, 0] = 0
        v1[:, -1] = 0
        
    return e, u, v


def _upwind1D(d, e0, u0, hx, q, transpose=False):
    
    d, e0, u0, hx, q = d.copy(), e0.copy(), u0.copy(), hx.copy(), q.copy()
    
    if transpose:
        d, e0, u0, hx, q = d.T, e0.T, u0.T, hx.T, q.T

    u0 = u0.copy()
    Nx = u0.shape[0] - 1
    
    # indexing x by sign
    idxPos = u0[1: Nx] > 0
    idxNeg = u0[1: Nx] < 0
    idxZero = u0[1: Nx] == 0

    # upwind
    hx[1: Nx][idxPos] = d[0: Nx - 1][idxPos] + e0[0: Nx - 1][idxPos]
    hx[1: Nx][idxNeg] = d[1: Nx][idxNeg] + e0[1: Nx][idxNeg]
    hx[1: Nx][idxZero] = (
        d[0: Nx - 1][idxZero] + e0[0: Nx - 1][idxZero] + \
        d[1: Nx][idxZero] + e0[1: Nx][idxZero]
    ) / 2

    # get values of h and p at half-integer
    hx[0] = d[0] + e0[0]
    hx[Nx] = d[Nx - 1] + e0[Nx - 1]
    hx = np.maximum(hx, 0) 
    q[0: Nx + 1] = hx[0: Nx + 1] * u0[0: Nx + 1]
    
    if transpose:
        d, e0, u0, hx, q = d.T, e0.T, u0.T, hx.T, q.T 
    
    return hx, q


def _upwind2D(d, e0, u0, hx, q, transpose=False):
    
    d, e0, u0, hx, q = d.copy(), e0.copy(), u0.copy(), hx.copy(), q.copy()
    
    if transpose:
        d, e0, u0, hx, q = d.T, e0.T, u0.T, hx.T, q.T

    u0 = u0.copy()
    Nx = u0.shape[0] - 1
    
    # indexing x by sign
    idxPos = u0[1: Nx, :] > 0
    idxNeg = u0[1: Nx, :] < 0
    idxZero = u0[1: Nx, :] == 0

    # upwind
    hx[1: Nx, :][idxPos] = d[0: Nx - 1, :][idxPos] + e0[0: Nx - 1, :][idxPos]
    hx[1: Nx, :][idxNeg] = d[1: Nx, :][idxNeg] + e0[1: Nx, :][idxNeg]
    hx[1: Nx, :][idxZero] = (
        d[0: Nx - 1, :][idxZero] + e0[0: Nx - 1, :][idxZero] + \
        d[1: Nx, :][idxZero] + e0[1: Nx, :][idxZero]
    ) / 2

    # get values of h and p at half-integer
    hx[0, :] = d[0, :] + e0[0, :]
    hx[Nx, :] = d[Nx - 1, :] + e0[Nx - 1, :]
    hx = np.maximum(hx, 0) 
    q[0: Nx + 1, :] = hx[0: Nx + 1, :] * u0[0: Nx + 1, :]
    
    if transpose:
        d, e0, u0, hx, q = d.T, e0.T, u0.T, hx.T, q.T 
    
    return hx, q