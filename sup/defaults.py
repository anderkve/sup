# -*- coding: utf-8 -*-

"""Default settings.

A sup module for collecting default settings that are used by several run modes. 

Attributes:
    xy_bins (pair of ints): The default number of bins to be used along the 
    x-axis and y-axis.

    ff (format string): The default format string for floating-point numbers,
        with a reserved space for the sign.

    ff2 (format string): The default format string for floating-point numbers,
        without a reserverd space for the sign.
"""

xy_bins = (40, 40)

ff = "{: .2e}"
ff2 = "{:.2e}"
