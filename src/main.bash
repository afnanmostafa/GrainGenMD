#!/bin/bash

module load atomsk
# module load python        ## Uncomment if Python is not loaded by default

## =============================================================================================================================
##                                              written by Afnan Mostafa (12.12.2024)
## =============================================================================================================================
## ===================== definitions ==================================================
## lat_par          : lattice parameter
## lat_type         : lattice type (bcc or fcc)
## element          : element name (Mo for molybdenum, Cu for Copper)
## orientX          : X orientation [h_x k_x l_x]
## orientY          : Y orientation [h_y k_y l_y]
## orientZ          : Z orientation [h_z k_z l_z]
## nx               : number of replicas along x
## ny               : number of replicas along y
## nz               : number of replicas along z
## grain_type       : lagb, hagb, or mixed
## num_nodes        : number of total nodes (nodes = grains)
## num_localized    : localized grains/nodes near top edge (num_localized < num_nodes)
## localized        : yes or no
## =====================================================================================

## ===================== scripts/files =========================================================================================
## baseMo.xsf                                   : unit cell file (gemerated in atomsk)
## baseMo-repli.xsf                             : supercell file (gemerated in atomsk)
## gen_atomsk_polycrystal_file_voro_tess.py     : python script to generate atomsk polycrystal input file
## ${grain_type}_grains.txt                     : hagb_grains.txt or lagb_grains.txt or mixed_grains.txt
##                                                atomsk-compatible polycrystal input file
## poly-${grain_type}.xsf                       : atomsk-generated polycrystal file
## bulk-cutout.py                               : python script for generating cutout form bulk structure
## poly-cutout.py                               : python script for generating cutout form poly structure
## b-cutout.data                                : bulk cutout structure file (can be viewed in OVITO)
## b-cutout.data                                : poly cutout structure file (can be viewed in OVITO)
## gen_cutouts.sh                               : bash file for generating final structure file
## final_<randomID>.data                        : final structure file to be used in LAMMPS (more details in gen_cutouts.sh)
## ==============================================================================================================================

set -e  
trap 'echo "Error occurred on line $LINENO"; exit 1' ERR 

#------------- default values ------------#
lat_par=3.15
lat_type="bcc"
element="Mo"
orientX="[001]"
orientY="[-110]"
orientZ="[110]"
nx=125
ny=89
nz=35
grain_type="hagb"
num_nodes=16
num_localized=2
localized="yes"
#-----------------------------------------#

#------------------------------- function: calculate parameters ----------------------------#
calculate_params() {
    if [[ "$localized" == "no" ]]; then
        num_localized=0
        localized_label="0lcl"
    else
        localized_label="${num_localized}lcl"
    fi

    # parse orientation components
    read -r o1x o1y o1z <<< "$(echo "$orientX" | tr -d '[]' | sed -E 's/(-?[0-9])/\1 /g')"
    read -r o2x o2y o2z <<< "$(echo "$orientY" | tr -d '[]' | sed -E 's/(-?[0-9])/\1 /g')"
    read -r o3x o3y o3z <<< "$(echo "$orientZ" | tr -d '[]' | sed -E 's/(-?[0-9])/\1 /g')"

    # calculate lattice dimensions
    lat_x=$(echo "$lat_par * sqrt($o1x^2 + $o1y^2 + $o1z^2)" | bc -l)
    lat_y=$(echo "$lat_par * sqrt($o2x^2 + $o2y^2 + $o2z^2)" | bc -l)
    lat_z=$(echo "$lat_par * sqrt($o3x^2 + $o3y^2 + $o3z^2)" | bc -l)

    # calculate box dimensions
    lx=$(echo "$nx * $lat_x" | bc -l)
    ly=$(echo "$ny * $lat_y" | bc -l)
    lz=$(echo "$nz * $lat_z" | bc -l)

    # format dimensions to two decimal places
    lat_x=$(printf "%.2f" "$lat_x")
    lat_y=$(printf "%.2f" "$lat_y")
    lat_z=$(printf "%.2f" "$lat_z")
    lx=$(printf "%.3f" "$lx")
    ly=$(printf "%.3f" "$ly")
    lz=$(printf "%.3f" "$lz")

    # calculate origin
    originX=$(echo "$lx / 2" | bc -l)
    originY=$(echo "$ly / 2" | bc -l)
    originZ=$lz
}
#-------------------------------------------------------------------------------------------#

#------------------------------------------------ function: display usage --------------------------------------------------#
usage() {
    echo "Usage: $0 [-n nx] [-m ny] [-k nz] [-a lat_par] [-g grain_type] [-n num_localized] [-t num_nodes] [-o localized]"
    echo "  -n nx                Number of duplicates in x direction (default: $nx)"
    echo "  -m ny                Number of duplicates in y direction (default: $ny)"
    echo "  -k nz                Number of duplicates in z direction (default: $nz)"
    echo "  -a lat_par           Lattice parameter (default: $lat_par)"
    echo "  -g grain_type        Grain type (hagb/lagb, default: $grain_type)"
    echo "  -n num_localized     Number of localized grains (default: $num_localized)"
    echo "  -t num_nodes         Number of nodes for Voronoi tessellation (default: $num_nodes)"
    echo "  -o localized         Localized grains (yes/no, default: $localized)"
    exit 1
}
#---------------------------------------------------------------------------------------------------------------------------#

#------------------- parse cmd arguments --------------------#
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -n) nx=$2; shift ;;
        -m) ny=$2; shift ;;
        -k) nz=$2; shift ;;
        -a) lat_par=$2; shift ;;
        -g) grain_type=$2; shift ;;
        -n) num_localized=$2; shift ;;
        -t) num_nodes=$2; shift ;;
        -o) localized=$2; shift ;;
        -h|--help) usage ;;
        *) echo "Unknown parameter passed: $1"; usage ;;
    esac
    shift
done
#------------------------------------------------------------#

#-------- calculate origins and dimensions ---------#
calculate_params
#---------------------------------------------------#

#------------------------------------------- generate a unique directory -----------------------------------------------------#
random_id=$((RANDOM))
output_dir="./${element}_${grain_type}_${num_nodes}gr_${localized_label}_x${orientX}_y${orientY}_z${orientZ}_rnd${random_id}"
mkdir -p "$output_dir"
#-----------------------------------------------------------------------------------------------------------------------------#

#----------------------- display user inputs ---------------------#
echo "Using the following parameters:"
echo "  nx: $nx"
echo "  ny: $ny"
echo "  nz: $nz"
echo "  Lattice parameter: $lat_par"
echo "  Grain type: $grain_type"
echo "  Number of localized grains: $num_localized"
echo "  Number of nodes: $num_nodes"
echo "  Localized: $localized"
echo "  Orientations: X($orientX), Y($orientY), Z($orientZ)"
echo "  Box dimensions: lx=$lx, ly=$ly, lz=$lz"
echo "  Output directory: $output_dir"
echo "  Origin: (${originX}, ${originY}, ${originZ})"
#----------------------------------------------------------------#

#---------------------------------------- generate base Mo structures --------------------------------------------#
atomsk --create $lat_type $lat_par $element orient "$orientX" "$orientY" "$orientZ" baseMo.xsf
atomsk --create $lat_type $lat_par $element orient "$orientX" "$orientY" "$orientZ" -duplicate $nx $ny $nz baseMo-repli.xsf
mv baseMo.xsf baseMo-repli.xsf "$output_dir/"
#-----------------------------------------------------------------------------------------------------------------#

#------------ generate atomsk input file for polyscrystals -----------#
python gen_atomsk_polycrystal_file_voro_tess.py \
    --x "$lx" --y "$ly" --z "$lz" \
    --localized "$localized" \
    --num_localized "$num_localized" \
    --grain_type "$grain_type" \
    --num_nodes "$num_nodes" \
    --output_file "${grain_type}_grains.txt"
if [[ ! -f "${grain_type}_grains.txt" ]]; then
    echo "Error: ${grain_type}_grains.txt was not generated."
    exit 1
fi
mv "${grain_type}_grains.txt" "$output_dir/"
#---------------------------------------------------------------------#

#------------------------ generate polycrystal structure in atomsk ----------------------#
cd "$output_dir" || exit
atomsk --polycrystal baseMo.xsf "${grain_type}_grains.txt" poly-${grain_type}.xsf -wrap
#----------------------------------------------------------------------------------------#

#----------------------------- generate cutout structures ---------------------------------------#
python ../bulk-cutout.py baseMo-repli.xsf b-cutout.data --radius 80 --a 1.5 --b 1 --c 1
python ../poly-cutout.py "poly-${grain_type}.xsf" p-cutout.data --radius 80 --a 1.5 --b 1 --c 1
#------------------------------------------------------------------------------------------------#

#---------------- generate final structure -------------------#
bash ../gen_final_from_cutouts.sh b-cutout.data p-cutout.data
#-------------------------------------------------------------#

