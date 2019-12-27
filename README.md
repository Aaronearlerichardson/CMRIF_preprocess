# CMRIF_preprocess
This program is a centralized hub for all your MRI preprocessing needs. It has three main features: A disk image optimized for MRI computation, a script that takes DICOM or NIFTI images and organizes them into BIDS standard formatting, and finally a modular preprocessing script that uses nipype to allow you to mix and match different preprocessing packages from different software (such as using BET from FSL and AFNI's anat2epi).

# Disk Image Includes
Software:
Afni, Freesurfer, Fsl, Anaconda (python 3.7)

Python packages: 
boto3, pathlib, pybids, pydicom, nipype, pip, tedana

Ubuntu packages:
dcm2niix, pigz

# Host Requirements

### Linux:
xauth

### Mac:
xQuartz

***
To begin, head over to our [Getting Started](https://github.coecis.cornell.edu/kms424/CMRIF_preprocess/wiki/Getting-Started) page.
