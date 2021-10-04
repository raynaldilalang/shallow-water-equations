import numpy as np


class Bathymetry1D:
    def __init__(self, x, d):
        self.x = x
        self.d = d
        
        self._dx = np.mean(x[1:] - x[: -1])
    
    @property
    def dx(self):
        self._dx = np.mean(self.x[1:] - self.x[: -1])
        return self._dx


class Bathymetry2D:
    def __init__(self, x, y, d):
        self.x = x
        self.y = y
        self.d = d
        
        _X, _Y = np.meshgrid(self.x, self.y)
        self._X, self._Y = _X.T, _Y.T
        
        self._dx = np.mean(x[1:] - x[: -1])
        self._dy = np.mean(x[1:] - x[: -1])
    
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