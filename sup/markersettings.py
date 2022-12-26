# -*- coding: utf-8 -*-
import numpy as np
import sup.defaults as defaults

class MarkerSettings:
    """A class to contain settings for plot markers.

    Attributes:
        regular_marker (str): The regular marker used to fill plots.

        regular_marker_up (str): The regular marker, shifted upwards.

        regular_marker_down (str): The regular marker, shifted downwards.

        fill_marker (str): The marker used for to fill vertical blocks, e.g.
            e.g. for use in 1d histograms.

        special_marker (str): The marker used to highlight special points.

        empty_bin_marker (str): The marker used for empty bins.

    """

    def __init__(self):
        """Constructor."""
        
        self.regular_marker = defaults.regular_marker
        self.regular_marker_up = defaults.regular_marker_up
        self.regular_marker_down = defaults.regular_marker_down

        self.fill_marker = defaults.fill_marker
        self.special_marker = defaults.special_marker
        self.empty_bin_marker = defaults.empty_bin_marker_1d

