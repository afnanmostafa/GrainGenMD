## =============================================================
## Combine atomic data from bulk and poly cutout files
## =============================================================
## Written by: Afnan Mostafa (12.12.2024)
## 
## Description:
## This script combines atomic data from two LAMMPS-compatible cutout files 
## (bulk and poly) into a single file. The resulting file has a 
## properly formatted header, renumbered atom indices, and updated atom counts.
## The script ensures compatibility with tools like OVITO/LAMMPS.
##
## Inputs:
## 1. Bulk cutout file: A LAMMPS-compatible file containing bulk atomic data.
## 2. poly cutout file: A LAMMPS-compatible file containing atomic data for the poly.
##
## Outputs:
## - A new LAMMPS-compatible file (`final_<random_number>.data`) that combines 
##   data from both input files into a single dataset.
##
## Usage:
## ./gen_final_from_cutouts.sh bulk-cutout.data poly-cutout.data
##
## Steps:
## 1. Extract atomic data from both input files starting at the `Atoms` section.
## 2. Combine and renumber the atom indices for the combined dataset.
## 3. Update the total number of atoms in the header of the output file.
## 4. Save the combined data in `final_<random_number>.data`.
##
## Requirements:
## - Ensure both input files exist and are formatted correctly.
##
## =============================================================

#!/bin/bash

##------ check: correct number of arguments (2: single and poly crystal cutout files) ------##
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <b-cutout-file> <h-cutout-file>"
    exit 1
fi

##------ input files ------##
B_CUTOUT_FILE=$1
H_CUTOUT_FILE=$2

##------ generates a random number for the unique output file name ------##
RANDOM_NUMBER=$((RANDOM))

##------ output file name ------##
FINAL_FILE="final_${RANDOM_NUMBER}.data"

##------ data excerpts ------##
sed -n '/Atoms/,$p' "$B_CUTOUT_FILE" | sed '1,2d' > bulk-dataonly.data
sed -n '/Atoms/,$p' "$H_CUTOUT_FILE" | sed '1,2d' > poly-dataonly.data
sed '/Atoms/ q' "$B_CUTOUT_FILE" > initials.data

##------ combine ------##
cat bulk-dataonly.data poly-dataonly.data > bulk-poly-dataonly.data

##------ fix index ------##
awk '{print NR, $2, $3, $4, $5}' bulk-poly-dataonly.data > fixed-index-dataonly.data

##------ add gap between files since OVITO can't read a file if there is no gap between 'Atoms' and first row of data ------##
echo "" > blank.txt

##------ merge into final data ------##
awk 1 initials.data blank.txt fixed-index-dataonly.data > "$FINAL_FILE"

##------ count total no. of lines ------##
countNew=$(wc -l < fixed-index-dataonly.data)
countOld=$(wc -l < bulk-dataonly.data)

##------ fix no. of atoms ------##
sed -i "s/$countOld/$countNew/" "$FINAL_FILE"

##------ remove temp files (uncomment to preserve) ------##
rm 'blank.txt' 'bulk-dataonly.data' 'poly-dataonly.data' 'initials.data' 'bulk-poly-dataonly.data'

##------ print the name of the final file ------##
echo "********************************************"
echo "*                                          *"
echo "*               SUCCESS!                   *"
echo "*                                          *"
echo "********************************************"
echo "Generated final file: $FINAL_FILE"

