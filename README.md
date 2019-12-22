# CMRIF_preprocess
This program is a centralized hub for all your MRI preprocessing needs. It has three main features: A disk image optimized for MRI computation, a script that takes DICOM or NIFTI images and organizes them into BIDS standard formatting, and finally a modular preprocessing script that uses nipype to allow you to mix and match different preprocessing packages from different software (such as using BET from FSL and AFNI's anat2epi).

# Disk Image Includes
Software:
Afni, Freesurfer, Fsl, Anaconda (python 3.7)

Python packages: 
boto3, pathlib, pybids, pydicom, nipype, pip

Ubuntu packages:
dcm2niix, pigz (optional)

# Host Requirements
Linux:
xauth

Mac:

# Getting Started

## Starting a Server

1. ![]{Images/scree
Getting on the server via ssh:

1. Find the location of your .pem key
2. Open a terminal and type in the command:
```
ssh -i absolute/path/to/SWALLOW.pem -X ubuntu@ec2-18-220-67-88.us-east-2.compute.amazonaws.com
```
