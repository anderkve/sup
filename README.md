# sup -- the Simple Unicode Plotter

`sup` is a command-line tool for generating quick 1D and 2D data visualizations directly in your terminal using Unicode characters and ANSI colors. It can plot data from files (text or HDF5) or directly from mathematical functions.

## Features

*   Multiple plotting modes:
    *   `hist1d`, `hist2d`: 1D and 2D histograms.
    *   `max1d`, `max2d`, `min1d`, `min2d`, `avg1d`, `avg2d`: Plotting max, min, or average values.
    *   `post1d`, `post2d`: 1D and 2D posterior probability distributions.
    *   `plr1d`, `plr2d`: Profile likelihood ratios.
    *   `graph1d`, `graph2d`: Plotting functions y=f(x) and z=f(x,y).
    *   `list`: List dataset names and indices from input files.
    *   `colors`, `colormaps`: Display available colors and colormaps.
*   Supports text and HDF5 input files.
*   Customizable plot size, ranges, transformations (e.g., log scale).
*   Color and grayscale output, with optional white background.
*   Various colormaps for 2D plots.

## Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
2.  **Install using pip:**
    For local development/installation:
    ```bash
    pip install .
    ```
    This will install the `sup` command and its dependencies.

    (If the package were published to PyPI, you could install it with `pip install sup-plotter`.)

## Dependencies

*   Python >= 3.6
*   numpy
*   scipy
*   h5py

These dependencies will be automatically installed when you install `sup` using pip.

## Usage

Once installed, you can use the `sup` command from your terminal.

**General syntax:**
`sup <mode> [options...]`

Run `sup --help` to see all available modes and options.

### Examples

Here are a few examples based on the tool's capabilities:

**List datasets in a file:**
```bash
sup list data.hdf5
sup list data.txt --delimiter ","
```

**Plot a 1D histogram from `posterior.dat` (column 0):**
```bash
sup hist1d posterior.dat 0 -sz 40 20 -wb
```
(The `posterior.dat` file is included in this repository for testing.)

**Plot a 1D function `y = x * cos(2*pi*x)`:**
```bash
sup graph1d "x * np.cos(2 * np.pi * x)" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20
```

**Plot a 2D histogram from `posterior.dat` (columns 0 and 1):**
```bash
sup hist2d posterior.dat 0 1 -sz 40 40
```

**Plot a 2D function `z = sin(x^2 + y^2) / (x^2 + y^2)`:**
```bash
sup graph2d "np.sin(x**2 + y**2) / (x**2 + y**2)" --x-range -5 5 --y-range -5 5 -sz 40 40
```

**More examples from `sup --help`:**
```
modes:
  sup list        list dataset names and indices
  sup hist1d      plot the x histogram
  sup hist2d      plot the (x,y) histogram
  sup max1d       plot the maximum y value across the x axis
  sup max2d       plot the maximum z value across the (x,y) plane
  sup min1d       plot the minimum y value across the x axis
  sup min2d       plot the minimum z value across the (x,y) plane
  sup avg1d       plot the average y value across the x axis
  sup avg2d       plot the average z value across the (x,y) plane
  sup post1d      plot the x posterior probability distribution
  sup post2d      plot the (x,y) posterior probability distribution
  sup plr1d       plot the profile likelihood ratio across the x axis
  sup plr2d       plot the profile likelihood ratio across the (x,y) plane
  sup graph1d     plot the function y = f(x) across the x axis
  sup graph2d     plot the function z = f(x,y) across the (x,y) plane
  sup colormaps   display the available colormaps
  sup colors      display the colors available for creating colormaps (for development)

examples:
  sup list data.hdf5

  sup list data.txt --delimiter ","

  sup hist1d data.txt 0 --x-range -10 10 --size 100 20 --y-transf "np.log10(y)" --delimiter ","

  sup hist2d data.txt 0 1 --x-range -10 10 --y-range -10 10 --size 30 30 --delimiter "," --colormap 1

  sup post2d posterior.dat 2 3 --x-range -10 10 --y-range -10 10 --size 30 30 --delimiter " "

  sup plr2d data.hdf5 0 1 4 --x-range 0 10 --y-range 0 10 --size 20 20

  sup plr2d data.hdf5 2 1 4 --x-range 0 10 --y-range 0 20 --size 20 40 --x-transf "np.abs(x)"

  sup graph1d "x * np.cos(2 * np.pi * x)" --x-range 0.0 2.0 --y-range -2 2 --size 40 20 --white-bg

  sup graph2d "np.sin(x**2 + y**2) / (x**2 + y**2)" --x-range -5 5 --y-range -5 5 --size 50 50
```

## Development

The main script is `sup.py`, and the core plotting logic and modes are within the `sup/` directory. Tests can be run using the `runtests.sh` script (note: this script uses `./sup.py` directly, so you might need to adjust paths or run it as `python sup.py` if you haven't installed the package globally).

## License
This project is licensed under the MIT License. (Assuming MIT, update if different)
