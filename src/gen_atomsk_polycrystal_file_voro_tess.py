#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================
Generate Grain Files for Atomsk
-- written by Afnan Mostafa (12.12.2024)
========================================

This script generates an Atomsk-compatible grain boundary file for molecular dynamics simulations.
It supports both localized and non-localized grains, and allows customization of grain properties.

Inputs:
-------
1. --x (float, required)           : Box dimension in X direction (Å).
2. --y (float, required)           : Box dimension in Y direction (Å).
3. --z (float, required)           : Box dimension in Z direction (Å).
4. --localized (str, required)     : Specify "yes" to add localized grains near the top surface, "no" otherwise.
5. --num_localized (int, optional) : Number of localized grains (default: 5).
6. --grain_type (str, required)    : Type of grain boundaries ("lagb", "hagb", or "mixed").
7. --num_nodes (int, required)     : Total number of grains/nodes in the box.
8. --output_file (str, optional)   : Path to the output file (default: "grains.txt").

Outputs:
--------
1. An Atomsk parameter file (e.g., grains.txt) with the following details:
   - Box dimensions.
   - Grain node positions.
   - Random misorientation angles for grains.

Additional Features:
--------------------
1. Ensures a minimum distance between nodes to avoid overlap.
2. Plots the node positions in 2D or 3D, highlighting localized grains in red.

Usage:
------
Run the script from the command line as follows:
    python generate_grains.py --x 400 --y 400 --z 200 --localized yes --num_localized 5 --grain_type hagb --num_nodes 50 --output_file grains.txt

Example:
--------
    python gen_atomsk_polycrystal_file_voro_tess.py --x 500 --y 500 --z 300 --localized no --grain_type lagb --num_nodes 100
    python gen_atomsk_polycrystal_file_voro_tess.py
    python gen_atomsk_polycrystal_file_voro_tess.py --localized yes --num_localized 3 --grain_type hagb --num_nodes 50
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt

def is_valid_position(new_pos, existing_positions, min_dist):
    """
    Check if the new position is at least `min_dist` away from all existing positions.
    """
    for pos in existing_positions:
        if np.linalg.norm(new_pos - pos) < min_dist:
            return False
    return True

def plot_nodes(all_nodes, localized_nodes, box_size, view="3D"):
    """
    Plot all nodes in the specified view (2D or 3D) and separately highlight localized nodes in red.
    """
    all_positions = np.array([node[:3] for node in all_nodes])
    localized_positions = np.array([node[:3] for node in localized_nodes])

    other_positions = np.array([
        pos for pos in all_positions if pos.tolist() not in localized_positions.tolist()
    ])

    if view == "2D":
        plt.figure(figsize=(8, 6))
        plt.scatter(other_positions[:, 0], other_positions[:, 1], c='green', label="Non-Localized Nodes", s=20)
        if localized_positions.size > 0:
            plt.scatter(localized_positions[:, 0], localized_positions[:, 1], c='red', label="Localized Nodes", s=50)
        plt.xlabel("X (Å)")
        plt.ylabel("Y (Å)")
        plt.title("Top View of Grain Nodes (X-Y Plane)")
        plt.legend()
        plt.grid(True)
        plt.show()

    elif view == "3D":
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(other_positions[:, 0], other_positions[:, 1], other_positions[:, 2], c='green', label="Non-Localized Nodes", s=20)
        if localized_positions.size > 0:
            ax.scatter(localized_positions[:, 0], localized_positions[:, 1], localized_positions[:, 2], c='red', s=50, label="Localized Nodes")
        ax.set_xlabel("X (Å)")
        ax.set_ylabel("Y (Å)")
        ax.set_zlabel("Z (Å)")
        ax.set_title("3D View of Grain Nodes")
        ax.legend()
        plt.show()
    else:
        raise ValueError("Invalid view option! Choose '2D' or '3D'.")

def generate_grain_file(box_size, num_nodes, grain_type, top_surface=False, localized_grains=5, radius=50, min_distance=10, output_file="grains.txt"):
    """
    Generate an Atomsk-compatible file for grains with minimum distance constraint.
    """
    box_x, box_y, box_z = box_size
    if grain_type.lower() == "lagb":
        angle_min, angle_max = 1, 10
    elif grain_type.lower() == "hagb":
        angle_min, angle_max = 10, 45
    elif grain_type.lower() == "mixed":
        angle_min, angle_max = 1, 45
    else:
        raise ValueError("Invalid grain_type! Choose 'lagb', 'hagb', or 'mixed'.")

    nodes = []
    localized_nodes = []

    if top_surface:
        center_x, center_y, center_z = box_x / 2, box_y / 2, box_z
        for _ in range(localized_grains):
            while True:
                pos = np.array([
                    np.random.uniform(center_x - radius, center_x + radius),
                    np.random.uniform(center_y - radius, center_y + radius),
                    center_z
                ])
                if np.linalg.norm(pos[:2] - [center_x, center_y]) <= radius and \
                   is_valid_position(pos, np.array([node[:3] for node in nodes]), min_distance):
                    break
            angles = np.random.uniform(angle_min, angle_max, 3)
            localized_nodes.append((*pos, *angles))
            nodes.append((*pos, *angles))

    for _ in range(num_nodes - len(nodes)):
        while True:
            pos = np.random.uniform([0, 0, 0], [box_x, box_y, box_z])
            if is_valid_position(pos, np.array([node[:3] for node in nodes]), min_distance):
                break
        angles = np.random.uniform(angle_min, angle_max, 3)
        nodes.append((*pos, *angles))

    with open(output_file, "w") as f:
        f.write(f"# Atomsk parameter file for {grain_type.upper()} grain boundaries\n")
        f.write(f"box       {box_x:.6f}      {box_y:.6f}      {box_z:.6f}\n")
        for node in nodes:
            f.write(f"node       {node[0]:.6f}      {node[1]:.6f}      {node[2]:.6f}      {node[3]:.2f}      {node[4]:.2f}      {node[5]:.2f}\n")

    print(f"Grain data has been saved to '{output_file}'.")
    plot_nodes(nodes, localized_nodes, box_size)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate grain files for molecular dynamics simulations.")
    parser.add_argument("--x", type=float, required=True, help="Box dimension in X direction (Å)")
    parser.add_argument("--y", type=float, required=True, help="Box dimension in Y direction (Å)")
    parser.add_argument("--z", type=float, required=True, help="Box dimension in Z direction (Å)")
    parser.add_argument("--localized", type=str, choices=["yes", "no"], required=True, help="Add localized grains near the top surface (yes/no)")
    parser.add_argument("--num_localized", type=int, default=5, help="Number of localized grains (default: 5)")
    parser.add_argument("--grain_type", type=str, choices=["lagb", "hagb", "mixed"], required=True, help="Grain type: lagb, hagb, or mixed")
    parser.add_argument("--num_nodes", type=int, required=True, help="Total number of nodes (grains)")
    parser.add_argument("--output_file", type=str, default="grains.txt", help="Output file name (default: grains.txt)")
    args = parser.parse_args()

    box_size = (args.x, args.y, args.z)
    top_surface = args.localized.lower() == "yes"
    generate_grain_file(
        box_size=box_size,
        num_nodes=args.num_nodes,
        grain_type=args.grain_type,
        top_surface=top_surface,
        localized_grains=args.num_localized,
        output_file=args.output_file
    )
