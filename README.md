# GrainGenMD

**GrainGenMD** is a collection of tools for generating, processing, and visualizing polycrystalline structures for molecular dynamics (MD) simulations. The repository provides streamlined scripts for tasks such as creating grain boundary configurations, filtering atomic data using geometric constraints, and preparing LAMMPS-compatible input files.

---

## Features
- **Grain File Generation**: Create Atomsk-compatible grain files for polycrystalline structures.
- **Geometric Filtering**: Filter atoms within or outside custom geometric shapes (e.g., ellipsoids).
- **Visualization**: Visualize grain distributions in 2D and 3D using Matplotlib.
- **Compatibility**: Seamlessly integrates with Atomsk and LAMMPS for pre- and post-processing of atomic structures.
- **Flexible Inputs**: Supports customizable lattice parameters, orientations, grain types, and box dimensions.

---

## Getting Started

### Prerequisites
1. **Python 3.6+**
   - Required libraries: `numpy`, `matplotlib`
   - Install dependencies:  
     ```bash
     pip install numpy matplotlib
     ```
2. **Atomsk**
   - Download from [Atomsk official site](https://atomsk.univ-lille.fr).
3. **LAMMPS** (optional)
   - Ensure compatibility with the generated `.data` files.

### Installation
Clone the repository:
```bash
git clone https://github.com/your-username/GrainGenMD.git
cd GrainGenMD

