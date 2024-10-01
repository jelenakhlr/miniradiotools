# author: Jelena
# combine coreas_to_hdf5 and fluencemap codes to automatically produce fluencemaps for all showers in a simulation set

import glob
import numpy as np
import subprocess
from optparse import OptionParser
import os
from re import search

from coreas_to_hdf5_mods import *

# dark plots (e.g. for slides):
# plt.style.use("dark_background")

parser = OptionParser()
parser.add_option("--directory", "--dir", "-d", type="str", dest="directory",
                  help="Specify the full path to the inp directory of the simulation set.\
                  It assumes that the .reas files are in subdirectories of the specified one.\
                  ")
parser.add_option("--file", "-f", type="str", dest="file",
                  help="Specify the full path to the reas file you want to analyze.")

(options, args) = parser.parse_args()


# * * * * * * * * * * * * * *
# * * * *  functions  * * * *
# * * * * * * * * * * * * * *
# read values from SIM.reas or RUN.inp
def find_input_vals(line):
  return search(r'[-+]?\ *[0-9]+\.?[0-9]*(?:[Ee]\ *[-+]?\ *[0-9]+)?', line)

def read_params(input_file, param):
  # works for both SIM.reas and RUN.inp, as long as you are looking for numbers
  val = "1111"
  with open(input_file, "r") as datafile:
    for line in datafile:
      if param in line:
        line = line.lstrip()
        if find_input_vals(line):
          val = find_input_vals(line).group()
          print(param, "=", val)
          break 
          # this is a problem for AutomaticTimeBoundaries, because it also shows up in other comments
          # therefore, just break after the first one is found. this can definitely be improved
  return float(val)
# * * * * * * * * * * * * * *

# GRAND freq range:
flow = "50"
fhigh = "200"
freqband = f"{flow}-{fhigh}"

if __name__ == '__main__':
    # for plotting a single file:
    if options.file:
        print(f"One shower to plot!")
        reas_filename = glob.glob(options.file)[0]
        print("********************************")
        print(f"Now analyzing {reas_filename}")
        # get zenith from inp file:
        zenith = int(read_params(reas_filename.split(".reas")[0] + ".inp", "THETAP"))
        # get obslevel from reas file:
        obslevel = int(read_params(reas_filename, "CoreCoordinateVertical")) # in cm

        # get just the path:
        path_to_reas = reas_filename.split("SIM")[-2]
        # define the name for the highlevel hdf5
        output_filename_hl = reas_filename.split(".reas")[0] + "_highlevel.hdf5"
        
        # Run coreas_to_hdf5_mods.py
        coreas_to_hdf5 = [
            'python', 'coreas_to_hdf5_mods.py', str(reas_filename), '-hl', '--flow', str(flow), '--fhigh', str(fhigh), # '--rm13',
            "--outputDirectory", str(path_to_reas)
        ]
        subprocess.run(coreas_to_hdf5, check=True)
        print(f"Created {reas_filename}_highlevel.hdf5")

        # Run fluencemap_mods.py
        fluencemap_command = [
            'python', 'fluencemap_mods.py', str(output_filename_hl), str(obslevel), str(freqband), str(zenith)
        ]
        subprocess.run(fluencemap_command, check=True)
        print(f"Plotted fluencemap for {output_filename_hl}")

        # Generate the new filename
        sim_number = reas_filename.split("SIM")[-1].split(".reas")[0]
        new_filename = f"SIM{sim_number}.png"

        # Rename the HDF5 file to the new PNG filename
        os.rename(output_filename_hl, new_filename)
        print(f"Renamed {output_filename_hl} to {new_filename}")
        print(f"Finished analyzing {reas_filename}")
        print("********************************")


    # for many plots in a given directory
    else:
        print(f"Searching directory {options.directory} for .reas files")
        # find .reas files with glob
        reas_names = np.array(glob.glob(options.directory + "/**/**/**/**/**" + "/SIM??????.reas"))
        # find .long files to check the amount of sims that crashed
        long_names = np.array(glob.glob(options.directory + "/**/**/**/**/**" + "/DAT??????.long"))
        # use ** iif you want to go through all subdirectories, use * if you want to go only one level deeper
        print(f"Found {len(reas_names)} showers to with input files!")
        print(f"Found {len(long_names)} showers that have Corsika output!")
        # loop over all reas files

        long_log = open(options.directory + "/crashed_sims_log.txt", 'w')
        long_log.write("# Simulation .reas files that didn't run\n")
        # put mask for 
        for reas_filename in reas_names:
            print("********************************")
            print(f"Now analyzing {reas_filename}")

            # Isolate simulation number
            sim_number = reas_filename.split("SIM")[-1].split(".reas")[0]


            # get zenith from inp file:
            zenith = int(read_params(reas_filename.split(".reas")[0] + ".inp", "THETAP"))
            # get obslevel from reas file:
            obslevel = int(read_params(reas_filename, "CoreCoordinateVertical")) # in cm

            # get just the path:
            path_to_reas = reas_filename.split("SIM")[-2]
            # define the name for the highlevel hdf5
            output_filename_hl = reas_filename.split(".reas")[0] + "_highlevel.hdf5"
            long_file = f"{path_to_reas}/DAT{sim_number}.long"
          
            if not os.path.isfile(long_file):
              print("Skipping file: ", long_file)
              long_log.write(f"{reas_filename}\n")
              continue
            
            # Run coreas_to_hdf5_mods.py
            coreas_to_hdf5 = [
                'python', 'coreas_to_hdf5_mods.py', str(reas_filename), '-hl', '--flow', str(flow), '--fhigh', str(fhigh), # '--rm13',
                "--outputDirectory", str(path_to_reas)
            ]
            subprocess.run(coreas_to_hdf5, check=True)
            print(f"Created {reas_filename}_highlevel.hdf5")

            # Run fluencemap_mods.py
            # fluencemap_command = [
            #     'python', 'fluencemap_mods.py', str(output_filename_hl), str(obslevel), str(freqband), str(zenith)
            # ]
            # subprocess.run(fluencemap_command, check=True)
            # print(f"Plotted fluencemap for {output_filename_hl}")

            # new_filename = f"SIM{sim_number}.png"

            # Rename the HDF5 file to the new PNG filename
            # os.rename(output_filename_hl, new_filename)
            # print(f"Renamed {output_filename_hl} to {new_filename}")

        print(f"Finished analyzing files in {options.directory}")
        print("********************************")

        long_log.close()

# TODO: skip if one shower happens to be incomplete. currently this crashes the whole process
