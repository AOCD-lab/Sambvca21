#!/usr/bin/python
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import subprocess                 # For issuing commands to the OS.
import os
import sys                        # For determining the Python version.
from pylab import *

# defining function to read surface xyz from sys.argv[1]
def readcontour(fname):
#   c = 0;
    fh = open(fname)
    lines = fh.readlines()
    fh.close()

    val = 0

    # Create 3D space and fill it with zeros
    # Find min and max x,y values, plus spacing
    zdata = []
    xmin = +999.0
    xmax = -999.0
    ymin = +999.0
    ymax = -999.0
    for i in range(0, len(lines), 1):
        fields = lines[i].split()
        if (len(fields) > 1):
            zdata.append(float(fields[2]))
            val = val + 1
            if (float(fields[0]) < xmin):
                xmin = float(fields[0])
            if (float(fields[0]) > xmax):
                xmax = float(fields[0])
            if (float(fields[1]) < ymin):
                ymin = float(fields[1])
            if (float(fields[1]) > ymax):
                ymax = float(fields[1])

    d = int(sqrt(val))
    x = zeros(d, float)
    y = zeros(d, float)
    z = zeros((d, d), float)
    grid_mesh = float((xmax - xmin) / (d - 1))
    print('Info:   ', 'Filename', sys.argv[1])
    print('Info:   ', 'Map range and spacing ', xmin, xmax, grid_mesh)
    print('Info:   ', 'Number of points on x,y axes ', d)
    print('Info:   ', 'Isocontour levels every ', sys.argv[2])

    # Setting grid mesh values here
    for i in range(0, d, 1):
        x[i] = xmin + i * grid_mesh
        y[i] = ymax - i * grid_mesh  # keep original top-to-bottom ordering

    c = 0
    for j in range(0, d, 1):
        for i in range(0, d, 1):
            z[j, i] = zdata[c]
            c = c + 1

    return (x, y, z, xmin, xmax)
# end def readcontour

# Main program below

# checking arguments are passed from command line
if (len(sys.argv) < 3):
    print(' ')
    sys.exit(' Usage: mappa.py surface-file.dat spacing')

# Read z(x,y) file
(cx, cy, cz, xmin, xmax) = readcontour(sys.argv[1])
spacing = float(sys.argv[2])

# -------- Heatmap with white below xmin --------
plt.figure()

# Create a colormap and set "underflow" (values < vmin) to white
cmap = plt.cm.get_cmap('jet').copy()
cmap.set_under('white')

# vmin=xmin defines the start of the scale; anything below is drawn with "under" color (white)
heat = plt.pcolormesh(cx, cy, cz, shading='auto',
                      cmap=cmap, vmin=xmin, vmax=xmax)

plt.colorbar(heat, label='Z')

# Make cells look square-ish in plot space
plt.gca().set_aspect('equal', adjustable='box')

# Show (no-op under Agg) and save
show()

filename, file_extension = os.path.splitext(sys.argv[1])
plt.savefig(filename + ".ps")
plt.savefig(filename + ".png", dpi=300)

print('Info:   ', 'PS  map image in file ', filename + ".ps")
print('Info:   ', 'PNG map image in file ', filename + ".png")
print('Info:   ', 'Normal termination')

