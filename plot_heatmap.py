#!/usr/bin/python3
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import os
import sys
import math
import argparse

def readcontour(fname, zmin_arg=None, zmax_arg=None):
    # load x,y,z (ignore empty/bad lines)
    data = np.loadtxt(fname, usecols=(0, 1, 2))
    if data.ndim == 1:  # single row case
        data = data.reshape(1, 3)

    xs, ys, zs_flat = data[:, 0], data[:, 1], data[:, 2]

    # ranges
    xmin, xmax = xs.min(), xs.max()
    ymin, ymax = ys.min(), ys.max()
    zmin = float(math.floor(zs_flat.min())) if zmin_arg is None else float(zmin_arg)
    zmin = float(math.floor(xmin))  # (kept as in your script)
    zmax = float(math.ceil(zs_flat.max())) if zmax_arg is None else float(zmax_arg)

    # infer square grid size
    npts = zs_flat.size
    d = int(round(np.sqrt(npts)))
    if d * d != npts:
        raise ValueError(f"Input is not a square grid: {npts} points ≠ {d}×{d}")

    # spacing and axes
    grid_mesh = (xmax - xmin) / (d - 1) if d > 1 else 0.0
    x = np.linspace(xmin, xmax, d)
    y = np.linspace(ymax, ymin, d)  # descending to match your original

    # reshape z to (d, d) in row-major order
    Z = zs_flat.reshape(d, d)

    print('Info:   ', 'Filename', fname)
    print('Info:   ', 'Map grid range and spacing ', xmin, xmax, grid_mesh)
    print('Info:   ', 'Map contours range ', zmin, zmax)
    print('Info:   ', 'Number of points on x,y axes ', d)
    return x, y, Z, xmin, xmax, zmin, zmax

# ---- main ----
parser = argparse.ArgumentParser(description="Heatmap plot of xyz data.")
parser.add_argument("mapfile", help="Input surface file (x y z columns)")
parser.add_argument("--zmin", type=float, default=None, help="Optional minimum z value (override auto)")
parser.add_argument("--zmax", type=float, default=None, help="Optional maximum z value (override auto)")
args = parser.parse_args()

cx, cy, cz, xmin, xmax, zmin, zmax = readcontour(args.mapfile, args.zmin, args.zmax)

plt.figure()

# --- RAW HEATMAP ---
heat = plt.pcolormesh(cx, cy, cz, shading='auto',
                      cmap='jet', vmin=zmin, vmax=zmax)

plt.colorbar(heat, label='Z')
plt.gca().set_aspect('equal', adjustable='box')
plt.tight_layout()

base, _ = os.path.splitext(args.mapfile)
plt.savefig(base + ".ps")
plt.savefig(base + ".png", dpi=300)

print('Info:   ', 'PS  map image in file ', base + ".ps")
print('Info:   ', 'PNG map image in file ', base + ".png")
print('Info:   ', 'Normal termination')

