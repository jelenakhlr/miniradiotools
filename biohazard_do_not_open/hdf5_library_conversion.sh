#!/bin/bash
#SBATCH --job-name=convert_library_to_hdf5
#SBATCH --account="hk-project-p0022320"
#SBATCH --output=/hkfs/work/workspace/scratch/bj4908-corsika_sims/china_stshps/logs/hdf5_conversion_log%j.out
#SBATCH --error=/hkfs/work/workspace/scratch/bj4908-corsika_sims/china_stshps/logs/hdf5_conversion_log%j.err
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --time=09:00:00
#SBATCH --tasks=1
######SBATCH --mem=50gb
######SBATCH --export=NONE
#######################SBATCH --gres=gpu:4

# Directory to search for .reas files
DIRECTORY=/hkfs/work/workspace/scratch/bj4908-corsika_sims/china_stshps/

# Check if directory is provided
if [ -z "$DIRECTORY" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Find all .reas files in the specified directory and its subdirectories
find "$DIRECTORY" -type f -name "SIM[0-9][0-9][0-9][0-9][0-9][0-9].reas" | while read -r REAS_FILE; do
    # Run the Python script on each .reas file in the respective directory
    SUBDIR=$(dirname $REAS_FILE)
    echo "$SUBDIR"
    python ~/software/corsika-77550/coast/CorsikaOptions/CoREAS/coreas_to_hdf5.py "$REAS_FILE" --flow 50 --fhigh 100 -hl --ignoreATMfile --outputDirectory "$SUBDIR" --not_store_full_simulation
done
