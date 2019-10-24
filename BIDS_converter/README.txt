The main script of this conversion folder is the fMRI_BIDS_convert.sh

This shell script calls the python script data2bids.py, the main script in terms of BIDS conversion. This python code reads in MRI data based on the settings that can be set in the config.json file. 

For more details on how this works or so that you can simply call the data2bids.py script yourself, go to the github at https://github.com/SIMEXP/Data2Bids