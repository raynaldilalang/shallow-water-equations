from .global_var import g

import numpy as np
from tqdm import tqdm


def swe1D(bathymetry, t, initial_condition, boundary_condition, i0, i1, advection=True, eps=1e-3, verbose=1):
    
    d = bathymetry.d
    
    dx = bathymetry.dx
    Nx = bathymetry.x.shape[0]
    x_min, x_max = bathymetry.x[0], bathymetry.x[-1]
    x_ = np.arange(x_min - dx/2, x_max + dx, dx)
    
    dt = t[1] - t[0]
    Nt = t.shape[0]
    S = dt / dx
    
    e = np.zeros((Nx, Nt)) 
    u = np.zeros((Nx + 1, Nt))
    
    p = np.zeros((Nx + 1))
    hx = np.zeros((Nx + 1))

    # initial conditions
    e[:, 0] = initial_condition['eta']
    u[:, 0] = initial_condition['u']

    # boundary conditions
    if i0 == 0:
        u[0, :] = boundary_condition['left']
        u[0, :] = boundary_condition['left']
    else:
        e[0, :] = boundary_condition['left']
        e[0, :] = boundary_condition['left']
    if i1 == Nx:
        u[-1, :] = boundary_condition['right']
        u[-1, :] = boundary_condition['right']
    else:
        e[-1, :] = boundary_condition['right']
        e[-1, :] = boundary_condition['right']
        

    loop = range(Nt - 1)
    if verbose == 1:
        loop = tqdm(loop)
    for n in loop:
        
        e0 = e[:, n]
        u0 = u[:, n]
        e1 = e[:, n+1]
        u1 = u[:, n+1]

        e0[:] = np.maximum(e0, -d)
        hx[:], p[:] = _upwind1D(d, e0, u0, hx, p, advection=advection)

        # calculate e(x, t_{n + 1})
        e1[i0: i1] = e0[i0: i1] - S * (p[i0 + 1: i1 + 1] - p[i0: i1])
        e1[:] = np.maximum(e1, -d)
        if advection:
            h = d + e1
        else:
            h = d.copy()
        
        # calculate u(x, t_{n + 1})
        wetx = h[i0: i1 - 1] + h[i0 + 1: i1] > eps
        hbarx = wetx * (h[i0: i1 - 1] + h[i0 + 1: i1]) / 2
        hbarx[hbarx == 0] = -1
        if advection:
            pb1 = wetx * (p[i0: i1 - 1] + p[i0 + 1: i1]) / 2
            pb2 = wetx * (p[i0 + 1: i1] + p[i0 + 2: i1 + 1]) / 2
            u_1 = wetx * ((pb1 > 0) * u0[i0: i1 - 1] + (pb1 < 0) * u0[i0 + 1: i1])
            u_2 = wetx * ((pb2 > 0) * u0[i0 + 1: i1] + (pb2 < 0) * u0[i0 + 2: i1 + 1])
            uux = np.where(wetx > 0, (1 / hbarx) * (pb2 * u_2 - pb1 * u_1 - u0[i0 + 1: i1] * (pb2 - pb1)), 0)
            uux = np.ma.fix_invalid(uux, fill_value=0).data
        else:
            uux = np.zeros(i1 - i0 - 1)
        Rx = 1
        if bathymetry.porous:
            Rx = np.where((wetx > 0) & (x_[i0 + 1: i1] > bathymetry.porous0) & (x_[i0 + 1: i1] < bathymetry.porous1), 1 + bathymetry.cf*dt*np.abs(u0[i0 + 1: i1]) / hbarx, 1)
        u1[i0 + 1: i1] = wetx * (u0[i0 + 1: i1] - g * S * (e1[i0 + 1: i1] - e1[i0: i1 - 1]) - S * uux) / Rx
        if i0 == 1:
            u1[i0] = u0[i0] - g * S * (e1[i0] - e1[i0 - 1])
        if i1 == Nx - 1:
            u1[i1] = u0[i1] - g * S * (e1[i1] - e1[i1 - 1])

    return e, u


def swe2D(bathymetry, t, initial_condition, boundary_condition, i0, i1, j0, j1, advection=True, eps=0, verbose=1):
    
    d = bathymetry.d
    
    dx = bathymetry.dx
    dy = bathymetry.dy
    Nx = bathymetry.x.shape[0]
    Ny = bathymetry.y.shape[0]
    x_min, x_max = bathymetry.x[0], bathymetry.x[-1]
    x_ = np.arange(x_min - dx/2, x_max + dx, dx)
    y_min, y_max = bathymetry.y[0], bathymetry.y[-1]
    y_ = np.arange(y_min - dy/2, y_max + dy, dy)
    x_ = x_.reshape((Nx + 1, 1)) * np.ones((Nx + 1, Ny))
    y_ = y_.reshape((1, Ny + 1)) * np.ones((Nx, Ny + 1))
    
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

    # initial conditions
    e[:, :, 0] = initial_condition['eta'] if 'eta' in initial_condition else 0
    u[:, :, 0] = initial_condition['u'] if 'u' in initial_condition else 0
    v[:, :, 0] = initial_condition['v'] if 'v' in initial_condition else 0

    print('YE1')
    # boundary conditions
    if i0 == 0:
        u[0, :, :] = boundary_condition['left']
        u[0, :, :] = boundary_condition['left']
    else:
        e[0, :, :] = boundary_condition['left']
        e[0, :, :] = boundary_condition['left']
    if i1 == Nx:
        u[-1, :, :] = boundary_condition['right']
        u[-1, :, :] = boundary_condition['right']
    else:
        e[-1, :, :] = boundary_condition['right']
        e[-1, :, :] = boundary_condition['right']
    if j0 == 0:
        v[:, 0, :] = boundary_condition['top']
        v[:, 0, :] = boundary_condition['top']
    else:
        e[:, 0, :] = boundary_condition['top']
        e[:, 0, :] = boundary_condition['top']
    if j1 == Ny:
        v[:, -1, :] = boundary_condition['bottom']
        v[:, -1, :] = boundary_condition['bottom']
    else:
        e[:, -1, :] = boundary_condition['bottom']
        e[:, -1, :] = boundary_condition['bottom']
    print('YE2')

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
        
        e0[:, :] = np.maximum(e0, -d)
        hx[:, :], p[:, :] = _upwind2D(d, e0, u0, hx, p, advection=advection)
        hy[:, :], q[:, :] = _upwind2D(d, e0, v0, hy, q, advection=advection, transpose=True)

        # calculate e(x, y, t_{n + 1})
        e1[i0: i1, j0: j1] = (
            e0[i0: i1, j0: j1] - \
            S1 * (p[i0 + 1: i1 + 1, j0: j1] - p[i0: i1, j0: j1]) - \
            S2 * (q[i0: i1, j0 + 1: j1 + 1] - q[i0: i1, j0: j1])
        )
        e1[:, :] = np.maximum(e1, -d)
        if advection:
            h = d + e1
        else:
            h = d.copy()
        
        # calculate u(x, y, t_{n + 1})
        wetx = np.zeros((i1 - i0 - 1, Ny))
        wetx[(h[i0: i1 - 1, :] + h[i0 + 1: i1, :] > eps)] = 1
        hbarx = wetx * (h[i0: i1 - 1, :] + h[i0 + 1: i1, :]) / 2
        hbarx[hbarx <= eps] = -1
        vb = np.where(hbarx[:, 1: Ny - 1] > eps,
                    (v0[i0: i1 - 1, 1: Ny - 1] + v0[i0 + 1: i1, 1: Ny - 1] + v0[i0: i1 - 1, 2: Ny] + v0[i0 + 1: i1, 2: Ny]) / 4, 0)
        if advection:
            pb1x = wetx * (p[i0: i1 - 1, :] + p[i0 + 1: i1, :]) / 2
            pb2x = wetx * (p[i0 + 1: i1, :] + p[i0 + 2: i1 + 1, :]) / 2
            u_1x = wetx * ((pb1x > 0) * u0[i0: i1 - 1, :] + (pb1x < 0) * u0[i0 + 1: i1, :])
            u_2x = wetx * ((pb2x > 0) * u0[i0 + 1: i1, :] + (pb2x < 0) * u0[i0 + 2: i1 + 1, :])
            qb1x = wetx[:, 1: Ny - 1] * (q[i0: i1 - 1, 1: Ny - 1] + q[i0 + 1: i1, 1: Ny - 1]) / 2
            qb2x = wetx[:, 1: Ny - 1] * (q[i0: i1 - 1, 2: Ny] + q[i0 + 1: i1, 2: Ny]) / 2
            u_1y = wetx[:, 1: Ny - 1] * ((qb1x > 0) * u0[i0 + 1: i1, 0: Ny - 2] + (qb1x < 0) * u0[i0 + 1: i1, 1: Ny - 1])
            u_2y = wetx[:, 1: Ny - 1] * ((qb2x > 0) * u0[i0 + 1: i1, 1: Ny - 1] + (qb2x < 0) * u0[i0 + 1: i1, 2: Ny])
            uux = np.where(hbarx > eps, (1 / hbarx) * (pb2x * u_2x - pb1x * u_1x - u0[i0 + 1: i1, :] * (pb2x - pb1x)), 0)
            vuy = np.where(hbarx[:, 1: Ny - 1] > eps, (1 / hbarx[:, 1: Ny - 1]) * (qb2x * u_2y - qb1x * u_1y - u0[i0 + 1: i1, 1: Ny - 1] * (qb2x - qb1x)), 0)
            uux = np.ma.fix_invalid(uux, fill_value=0).data
            vuy = np.ma.fix_invalid(vuy, fill_value=0).data
        else:
            uux = np.zeros((i1 - i0 - 1, Ny))
            vuy = np.zeros((i1 - i0 - 1, Ny - 2))
        Rx = np.where((hbarx[:, 1: Ny - 1] > eps),
            1 + bathymetry.cf_x[i0 + 1: i1, 1: Ny - 1]*dt*np.sqrt((u0[i0 + 1: i1, 1: Ny - 1])**2 + (vb)**2) / hbarx[:, 1: Ny - 1], 1
        )
        u1[i0 + 1: i1, 1: Ny - 1] = wetx[:, 1: Ny - 1] * (u0[i0 + 1: i1, 1: Ny - 1] - g * S1 * (e1[i0 + 1: i1, 1: Ny - 1] - e1[i0: i1 - 1, 1: Ny - 1]) - S1 * uux[:, 1: Ny - 1] - S2 * vuy) / Rx
        u1[i0 + 1: i1, 0] = wetx[:, 0] * (u0[i0 + 1: i1, 0] - g * S1 * (e1[i0 + 1: i1, 0] - e1[i0: i1 - 1, 0]) - S1 * uux[:, 0])
        u1[i0 + 1: i1, -1] = wetx[:, -1] * (u0[i0 + 1: i1, -1] - g * S1 * (e1[i0 + 1: i1, -1] - e1[i0: i1 - 1, -1]) - S1 * uux[:, -1])
        if i0 == 1:
            u1[i0, :] = u0[i0, :] - g * S1 * (e1[i0, :] - e1[i0 - 1, :])
        if i1 == Nx - 1:
            u1[i1, :] = u0[i1, :] - g * S1 * (e1[i1, :] - e1[i1 - 1, :])
        
        # calculate v(x, y, t_{n + 1})
        wety = np.zeros((Nx, j1 - j0 - 1))
        wety[(h[:, j0: j1 - 1] + h[:, j0 + 1: j1] > eps)] = 1
        hbary = wety * (h[:, j0: j1 - 1] + h[:, j0 + 1: j1]) / 2
        hbary[hbary <= eps] = -1
        ub = np.where(hbary[1: Nx - 1, :] > eps,
                      (u0[1: Nx - 1, j0: j1 - 1] + u0[2: Nx, j0: j1 - 1] + u0[1: Nx - 1, j0 + 1: j1] + u0[2: Nx, j0 + 1: j1]) / 4, 0)
        if advection:
            qb1y = wety * (q[:, j0: j1 - 1] + q[:, j0 + 1: j1]) / 2
            qb2y = wety * (q[:, j0 + 1: j1] + q[:, j0 + 2: j1 + 1]) / 2
            v_1y = wety * ((qb1y > 0) * v0[:, j0: j1 - 1] + (qb1y < 0) * v0[:, j0 + 1: j1])
            v_2y = wety * ((qb2y > 0) * v0[:, j0 + 1: j1] + (qb2y < 0) * v0[:, j0 + 2: j1 + 1])
            pb1y = wety[1: Nx - 1, :] * (p[1: Nx - 1, j0: j1 - 1] + p[1: Nx - 1, j0 + 1: j1]) / 2
            pb2y = wety[1: Nx - 1, :] * (p[2: Nx, j0: j1 - 1] + p[2: Nx, j0 + 1: j1]) / 2
            v_1x = wety[1: Nx - 1, :] * ((pb1y > 0) * v0[0: Nx - 2, j0 + 1: j1] + (pb1y < 0) * v0[1: Nx - 1, j0 + 1: j1])
            v_2x = wety[1: Nx - 1, :] * ((pb2y > 0) * v0[1: Nx - 1, j0 + 1: j1] + (pb2y < 0) * v0[2: Nx, j0 + 1: j1])
            vvy = np.where(hbary > eps, (1 / hbary) * (qb2y * v_2y - qb1y * v_1y - v0[:, j0 + 1: j1] * (qb2y - qb1y)), 0)
            uvx = np.where(hbary[1: Nx - 1, :] > eps, (1 / hbary[1: Nx - 1, :]) * (pb2y * v_2x - pb1y * v_1x - v0[1: Nx - 1, j0 + 1: j1] * (pb2y - pb1y)), 0)
            vvy = np.ma.fix_invalid(vvy, fill_value=0).data
            uvx = np.ma.fix_invalid(uvx, fill_value=0).data
        else:
            vvy = np.zeros((Nx, j1 - j0 - 1))
            uvx = np.zeros((Nx - 2, j1 - j0 - 1))
        Ry = np.where((hbary[1: Nx - 1, :] > eps),
            1 + bathymetry.cf_y[1: Nx - 1, j0 + 1: j1]*dt*np.sqrt((ub)**2 + (v0[1: Nx - 1, j0 + 1: j1])**2) / hbary[1: Nx - 1, :], 1
        )
        v1[1: Nx - 1, j0 + 1: j1] = wety[1: Nx - 1, :] * (v0[1: Nx - 1, j0 + 1: j1] - g * S2 * (e1[1: Nx - 1, j0 + 1: j1] - e1[1: Nx - 1, j0: j1 - 1]) - S2 * vvy[1: Nx - 1, :] - S1 * uvx) / Ry
        v1[0, j0 + 1: j1] = wety[0, :] * (v0[0, j0 + 1: j1] - g * S2 * (e1[0, j0 + 1: j1] - e1[0, j0: j1 - 1]) - S2 * vvy[0, :])
        v1[-1, j0 + 1: j1] = wety[-1, :] * (v0[-1, j0 + 1: j1] - g * S2 * (e1[-1, j0 + 1: j1] - e1[-1, j0: j1 - 1]) - S2 * vvy[-1, :])
        if j0 == 1:
            v1[:, j0] = v0[:, j1] - g * S2 * (e1[:, j0] - e1[:, j0 - 1])
        if j1 == Ny - 1:
            v1[:, j1] = v0[:, j1] - g * S2 * (e1[:, j1] - e1[:, j1 - 1])
        
    return e, u, v


def _upwind1D(d, e0, u0, hx, q, advection=True, transpose=False):
    
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
    if advection:
        hx[1: Nx][idxPos] = d[0: Nx - 1][idxPos] + e0[0: Nx - 1][idxPos]
        hx[1: Nx][idxNeg] = d[1: Nx][idxNeg] + e0[1: Nx][idxNeg]
        hx[1: Nx][idxZero] = (
            d[0: Nx - 1][idxZero] + e0[0: Nx - 1][idxZero] + \
            d[1: Nx][idxZero] + e0[1: Nx][idxZero]
        ) / 2
        hx[0] = d[0] + e0[0]
        hx[Nx] = d[Nx - 1] + e0[Nx - 1]
    else:
        hx[1: Nx][idxPos] = d[0: Nx - 1][idxPos].copy()
        hx[1: Nx][idxNeg] = d[1: Nx][idxNeg].copy()
        hx[1: Nx][idxZero] = (
            d[0: Nx - 1][idxZero] + \
            d[1: Nx][idxZero]
        ) / 2
        hx[0] = d[0]
        hx[Nx] = d[Nx - 1]

    # get values of h and q at half-integer
    hx = np.maximum(hx, 0) 
    q[0: Nx + 1] = hx[0: Nx + 1] * u0[0: Nx + 1]
    
    if transpose:
        d, e0, u0, hx, q = d.T, e0.T, u0.T, hx.T, q.T 
    
    return hx, q


def _upwind2D(d, e0, u0, hx, q, advection=True, transpose=False):
    
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
    if advection:
        hx[1: Nx, :][idxPos] = d[0: Nx - 1, :][idxPos] + e0[0: Nx - 1, :][idxPos]
        hx[1: Nx, :][idxNeg] = d[1: Nx, :][idxNeg] + e0[1: Nx, :][idxNeg]
        hx[1: Nx, :][idxZero] = (
            d[0: Nx - 1, :][idxZero] + e0[0: Nx - 1, :][idxZero] + \
            d[1: Nx, :][idxZero] + e0[1: Nx, :][idxZero]
        ) / 2
        hx[0, :] = d[0, :] + e0[0, :]
        hx[Nx, :] = d[Nx - 1, :] + e0[Nx - 1, :]
    else:
        hx[1: Nx, :][idxPos] = d[0: Nx - 1, :][idxPos]
        hx[1: Nx, :][idxNeg] = d[1: Nx, :][idxNeg]
        hx[1: Nx, :][idxZero] = (
            d[0: Nx - 1, :][idxZero] + \
            d[1: Nx, :][idxZero]
        ) / 2
        hx[0, :] = d[0, :].copy()
        hx[Nx, :] = d[Nx - 1, :].copy()

    # get values of h and p at half-integer
    hx = np.maximum(hx, 0) 
    q[0: Nx + 1, :] = hx[0: Nx + 1, :] * u0[0: Nx + 1, :]
    
    if transpose:
        d, e0, u0, hx, q = d.T, e0.T, u0.T, hx.T, q.T 
    
    return hx, q