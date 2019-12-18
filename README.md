# CMRIF_preprocess
Cornell University fMRI preprocessing script and library

software required:
Afni, Freesurfer, Fsl, Anaconda (python 3.7)

python packages required: 
boto3, pathlib, pybids, pydicom, nipype, pip

Ubuntu packages:
dcm2niix, pigz (optional)

Remote host packages:
xauth

Getting on the server via ssh:

1. Find the location of your .pem key
2. Open a terminal and type in the command:
```
ssh -i absolute/path/to/SWALLOW.pem -X ubuntu@ec2-18-220-67-88.us-east-2.compute.amazonaws.com
```
