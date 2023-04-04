import numpy as np


class Bathymetry1D:
    def __init__(self, x, d):
        self.x = x
        self.d = d
        
        self._dx = np.mean(x[1:] - x[: -1])

        self.porous = False
        self.cf = np.zeros(self.x.shape)
    
    @property
    def dx(self):
        self._dx = np.mean(self.x[1:] - self.x[: -1])
        return self._dx

    def set_porous(self, cf):
        self.porous = True
        self.cf = cf


class Bathymetry2D:
    def __init__(self, x, y, d):
        self.x = x
        self.y = y
        self.d = d
        
        _X, _Y = np.meshgrid(self.x, self.y)
        self._X, self._Y = _X.T, _Y.T
        
        self._dx = np.mean(x[1:] - x[: -1])
        self._dy = np.mean(x[1:] - x[: -1])
        
        self.porous = False
        self.cf = np.zeros(self._X.shape)
        self.cf_x = np.zeros((len(x)+1, len(y)))
        self.cf_y = np.zeros((len(x), len(y)+1))
    
    @property
    def X(self):
        _X, _Y = np.meshgrid(self.x, self.y)
        self._X, self._Y = _X.T, _Y.T
        return self._X
    
    @property
    def Y(self):
        _X, _Y = np.meshgrid(self.x, self.y)
        self._X, self._Y = _X.T, _Y.T
        return self._Y
    
    @property
    def dx(self):
        self._dx = np.mean(self.x[1:] - self.x[: -1])
        return self._dx
    
    @property
    def dy(self):
        self._dy = np.mean(self.y[1:] - self.y[: -1])
        return self._dx

    def set_porous(self, cf):
        self.porous = True
        self.cf = cf
        self.cf_x = np.concatenate((cf, np.zeros((1, len(self.y)))), axis=0)
        self.cf_y = np.concatenate((cf, np.zeros((len(self.x), 1))), axis=1)