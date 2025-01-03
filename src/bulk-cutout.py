"""
=========================================================
Keep atoms only outside of an ellipsoid from an .xsf file
-- written by Afnan Mostafa (12.12.2024)
=========================================================

This script reads atomic data from an .xsf file, deletes atoms that lie inside 
a specified ellipsoid, and writes the filtered data to a LAMMPS-compatible data file.

Inputs:
-------
1. input_file (str)             : Path to the input .xsf file containing super cell of atomic data
2. output_file (str)            : name of the output file for bulk structure
3. --radius (float, optional)   : Radius of the ellipsoid (default: 80)
4. --a (float, optional)        : Parameter a for the ellipsoid equation (default: 1.5)
5. --b (float, optional)        : Parameter b for the ellipsoid equation (default: 1.0)
6. --c (float, optional)        : Parameter c for the ellipsoid equation (default: 1.0)

Outputs:
--------
1. A LAMMPS data file containing atoms that fall outside the specified ellipsoid.

Usage:
------
Run the script from the command line as follows:
    python bulk-cutout.py input_file.xsf output_file.data --radius 80 --a 1.5 --b 1.0 --c 1.0

Example:
--------
    python bulk-cutout.py baseMo.xsf output.data --radius 80 --a 1.5 --b 1.0 --c 1.0
    python bulk-cutout.py baseMo.xsf output.data
    python bulk-cutout.py baseMo.xsf output.data --radius 50
    python bulk-cutout.py baseMo.xsf output.data --radius 50 --a 1.0 --b 1.0 --c 1.0   ## circle of radius 50 Angstrom 
"""

import numpy as np
import argparse

# function to check if a point is inside the ellipsoid
def inside_ellipsoid(x, y, z, lx, ly, lz, a, b, c, radius_squared):
    """
    Checks if a point (x, y, z) is inside the ellipsoid defined by:
    (x - lx/2)^2 / a + (y - ly/2)^2 / b + (z - lz)^2 / c <= radius_squared
    """
    return ((x - lx / 2) ** 2 / a) + ((y - ly / 2) ** 2 / b) + ((z - lz) ** 2 / c) <= radius_squared

# argument parser for input parameters
parser = argparse.ArgumentParser(description="Filter atoms inside an ellipsoid from an .xsf file and save as LAMMPS data file.")
parser.add_argument("input_file", type=str, help="Path to the input .xsf file.")
parser.add_argument("output_file", type=str, help="Path to the output LAMMPS data file.")
parser.add_argument("--radius", type=float, default=80, help="Radius of the ellipsoid (default: 80).")
parser.add_argument("--a", type=float, default=1.5, help="Ellipsoid parameter a (default: 1.5).")
parser.add_argument("--b", type=float, default=1.0, help="Ellipsoid parameter b (default: 1.0).")
parser.add_argument("--c", type=float, default=1.0, help="Ellipsoid parameter c (default: 1.0).")

args = parser.parse_args()

# extract parameters
input_file = args.input_file
output_file = args.output_file
radius_squared = args.radius ** 2
a, b, c = args.a, args.b, args.c

try:
    # read the .xsf file
    with open(input_file, "r") as file:
        lines = file.readlines()

    # extract lattice vectors and atomic coordinates
    lattice_vectors = []
    atoms = []
    parse_atoms = False

    for i, line in enumerate(lines):
        if "PRIMVEC" in line or "CONVVEC" in line:  # Lattice vectors
            lattice_vectors = [
                list(map(float, lines[i + 1].split())),
                list(map(float, lines[i + 2].split())),
                list(map(float, lines[i + 3].split())),
            ]
        elif "PRIMCOORD" in line:  # Start of atomic data
            atom_start = i + 2  # Skip the header line in PRIMCOORD
            parse_atoms = True

    if not parse_atoms:
        raise ValueError("PRIMCOORD section not found in the .xsf file.")

    # extract lattice dimensions
    lx, ly, lz = lattice_vectors[0][0], lattice_vectors[1][1], lattice_vectors[2][2]
    print(f"Lattice dimensions: lx={lx}, ly={ly}, lz={lz}")
    print(f"Ellipsoid parameters: a={a}, b={b}, c={c}, radius={args.radius}")

    # extract atomic data
    for line in lines[atom_start:]:
        parts = line.split()
        if len(parts) == 4:  # Format: type x y z
            atom_type, x, y, z = int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])
            atoms.append((1, x, y, z))  # Set second column to 1

    # keep atoms outside the ellipsoid
    keep_atoms = [
        (t, x, y, z) for t, x, y, z in atoms if not inside_ellipsoid(x, y, z, lx, ly, lz, a, b, c, radius_squared)
    ]

    # get box dimensions for LAMMPS
    x_min, x_max = 0, lx
    y_min, y_max = 0, ly
    z_min, z_max = 0, lz

    # write the LAMMPS data file
    with open(output_file, "w") as file:
        file.write("LAMMPS data file generated from .xsf\n\n")
        file.write(f"{len(keep_atoms)} atoms\n")
        file.write("1 atom types\n\n")  # Only 1 atom type
        file.write(f"{x_min:.6f} {x_max:.6f} xlo xhi\n")
        file.write(f"{y_min:.6f} {y_max:.6f} ylo yhi\n")
        file.write(f"{z_min:.6f} {z_max:.6f} zlo zhi\n\n")
        file.write("Masses\n\n")
        file.write("1 95.94\n\n")
        file.write("Atoms\n\n")
        for i, (atom_type, x, y, z) in enumerate(keep_atoms, start=1):
            file.write(f"{i} 1 {x:.6f} {y:.6f} {z:.6f}\n")  # Second column is always 1

    print(f"LAMMPS data file saved as {output_file}")

except FileNotFoundError:
    print(f"Error: Input file '{input_file}' not found.")
except ValueError as ve:
    print(f"Error: {ve}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
