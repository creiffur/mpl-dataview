#!usr/bin/env python
# -*- coding: utf-8 -*-

"""Time series data exploration in Matplotlib figure instance.

Display time series data interactively with samples >1e6 in a
Matplotlib figure window. Rather than subclassing a matplotlib
backend, a monkey-patched approach is used to limit the number of
rendered data points.

Known problem with this approach: Arbitrarily reducing the sampling
rate unfortunately leads to aliasing effects.

clemens.reiffurth@gmail.com (2015)
"""

from __future__ import print_function, division  
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import ipdb


class DataPlot(object):
    """Create time series plot with reduced number of data points."""

    default_kwargs = dict(subpl_adj={'right':0.93, 'left':0.07},
                          figsize=(18, 6), point_max=1e4)
    
    def __init__(self, data, *args, **kwargs):
        """Set up the data for plotting.
        
        Parameters
        ----------
        data : ndarray or 2-element list/tuple/array of arrays
            Data is accepted as a y vector with or without sampling
            rate (fs) or as a 2-element sequence of two vectors
        kwargs : dict
            fs should be supplied as a keyword argument
        fs : float (optional, kwargs)
            Sampling rate (Hz). When no fs is supplied it will be
            calculated to enable computing of the downsampling
            factor. From the sampling rate fs we calculate the
            sampling interval ts.
        args : list
            args will hold the y vector, if 2 vectors (x,y) are
            supplied
        """

        if kwargs.has_key('fs'):
            self.fs = kwargs.get('fs') # sampling rate
        else:
            self.fs = None
        
        # data: single array (y)
        if hasattr(data, 'shape') and not args and len(data) > 2:
            y_data = data
            # sampling rate (fs) supplied
            if self.fs:
                self.ts = 1 / self.fs # sampling interval
            # otherwise set fs to 1
            else:
                self.fs = 1
                self.ts = 1 / self.fs
            x_data = np.arange(len(data))/self.fs # create time vector
            self.data = (x_data, y_data)

        # data: x- and y-vector
        elif hasattr(data, 'shape') and len(args) > 0:
            x_data = data
            y_data = args[0]
            self.data = (x_data, y_data)
            
        # data: two-element sequence (tuple, list, ndarray of arrays)
        elif len(data) == 2 and isinstance(data, (list, tuple, ndarray)):
            self.data = data
        if self.fs:
            self.ts = 1 / self.fs
        else:
            # Calculate sampling interval from x vector (we assume
            # a constant sampling interval)
            self.ts = self.data[0][1] - self.data[0][0]
            print("\nSampling interval: %g", self.ts)
                
        # max number of plotted data points
        self._point_max = self.default_kwargs['point_max'] 

        # ipdb.set_trace()
        self._plotdata()


    def _plotdata(self):
        """Plot data."""
        self.fig, self.ax = plt.subplots(figsize=self.default_kwargs['figsize'])
        # adjust subplots
        self.fig.subplots_adjust(**self.default_kwargs['subpl_adj'])

        self.cid = self.fig.canvas.mpl_connect('button_release_event',
                                               self._onrelease)
        point_num = len(self.data[0])
        if point_num > self._point_max:
            # plot reduced number of points
            down_fact = self._calc_downfact(point_num)
            self.line, = self.ax.plot(self.data[0][::down_fact],
                                      self.data[1][::down_fact],
                                      visible=False)
        else:
            # plot everything
            self.line, = self.ax.plot(self.data[0], self.data[1], visible=False)
            
        self.line.set_visible(True)
        self.ax.callbacks.connect('xlim_changed', self._onchanged)

        
    def _onrelease(self, event):
        """Mouse button release callback."""
        # do not allow negative indices
        if self.changed[0] < 0: 
            xlim_low, xlim_high = 0, self.changed[1]
        else:
            xlim_low, xlim_high = self.changed
        # number of plotted data points
        point_num = int((xlim_high - xlim_low) / self.ts)
        print("Number of data points: ", point_num)
        # ipdb.set_trace()
        if point_num > self._point_max:
            down_fact = self._calc_downfact(point_num)
            print("down_fact: ", down_fact)
            self.line.set_data(self.data[0][::down_fact],
                               self.data[1][::down_fact])
        else:
            self.line.set_data(self.data[0],
                               self.data[1])

            
    def _calc_downfact(self, point_num):
        """Calculate downsampling factor."""
        down_fact = int(ceil(point_num / self._point_max))
        return down_fact

            
    def _onchanged(self, ax):
        """Axes limits change callback."""
        self.changed = ax.get_xlim()

        
def plotdata(data, *args, **kwargs):
    """Instantiate DataPlot class.

    Returns
    -------
        dp : DatPlot instance
    """
    dp = DataPlot(data, *args, **kwargs)
    return dp
        
        
def test_data(n_points=1e6):
    """Create some testing data.
    """
    x = np.arange(0, 100, 100/n_points)
    y = 3 * np.cos(x) + 2 * np.sin(10 * x) + np.random.randn(len(x))
    return (x,y)

       
if __name__ == '__main__':
    try:
        x
    except NameError:
        x, y = test_data(1e7)
    dp = DataPlot(sig)
