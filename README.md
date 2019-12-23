# CMRIF_preprocess
This program is a centralized hub for all your MRI preprocessing needs. It has three main features: A disk image optimized for MRI computation, a script that takes DICOM or NIFTI images and organizes them into BIDS standard formatting, and finally a modular preprocessing script that uses nipype to allow you to mix and match different preprocessing packages from different software (such as using BET from FSL and AFNI's anat2epi).

# Disk Image Includes
Software:
Afni, Freesurfer, Fsl, Anaconda (python 3.7)

Python packages: 
boto3, pathlib, pybids, pydicom, nipype, pip, tedana

Ubuntu packages:
dcm2niix, pigz (optional)

# Host Requirements

### Linux:
xauth

### Mac:

# Getting Started

## Starting a Server

1. Once you've logged in to your Corenll AWS account, open the services tab and click on "EC2"

![Once you've logged in to your Corenll AWS account, open the services tab and click on "EC2"](images/Screenshot%20(18).png)

***

2. Locate the "AMI" tab on the left and select it to access the Amazon Machine Image

![Locate the "AMI" tab on the left and select it to access the Amazon Machine Image](images/Screenshot%20(10).png)

***

3. Select the image you want to start. If this is your first time or you are startign from scratch, select the "Base Image." Once selected, start the image by clicking launch in the actions tab.

![Select the image you want to start. If this is your first time or you are startign from scratch, select the "Base Image." Once selected, start the image by clicking launch in the actions tab.](images/Screenshot%20(11).png)

***

4.Select your machine specifications to fit your needs. A detailed description of instance types and how to choose them can be found [here](https://aws.amazon.com/blogs/aws/choosing-the-right-ec2-instance-type-for-your-application/). In short, either t2 or c instances tend to fit the best for faster preprocessing. It should also be noted that a memory (RAM) of less than 8 gigabytes is not recommended and less than 4 will not function whatsoever. In addition, every cpu you have will make the job finish that many times quicker than if you didn't. A 4 cpu machine will work twice as fast as a 2 cpu one. When finished, advance to configure the instance details.

![Select your machine specifications to fit your needs. A detailed description of instance types and how to choose them can be found [here](https://aws.amazon.com/blogs/aws/choosing-the-right-ec2-instance-type-for-your-application/). In short, either t2 or c instances tend to fit the best for faster preprocessing. It should also be noted that a memory (RAM) of less than 8 gigabytes is not recommended and less than 4 will not function whatsoever. In addition, every cpu you have will make the job finish that many times quicker than if you didn't. A 4 cpu machine will work twice as fast as a 2 cpu one. When finished, advance to configure the instance details.](images/Screenshot%20(13).png)

***

5. Select your IAM role. This step is important as an incorrect IAM role will lead to many different and seemingly unrelated errors (such as being unable to connect to the internet). Move to the next step to configure storage.

![Select your IAM role. This step is important as an incorrect IAM role will lead to many different and seemingly unrelated errors (such as being unable to connect to the internet). Move to the next step to configure storage.](images/Screenshot%20(14).png)

***

6. Select what storage size you would like _in the **ebs** volume_ (Not the root volume on top). Remember that the included software takes up 31 gb of space so a volume of 40 gb only has 9 gb free. You may choose just about any type of storage, and may read more about the differences between them [here](https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/ebs-volume-types.html). Make sure to check the delete when terminated box for the ebs volume, otherwise when you are finished using the instance you will leave behind an un-paired ebs volume. Finish the set up by clicking "Review and Launch."

![Select what storage size you would like _in the **ebs** volume_ (Not the root volume on top). Remember that the included software takes up 31 gb of space so a volume of 40 gb only has 9 gb free. You may choose just about any type of storage, and may read more about the differences between them [here](https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/ebs-volume-types.html). Make sure to check the delete when terminated box for the ebs volume, otherwise when you are finished using the instance you will leave behind an un-paired ebs volume. Finish the set up by clicking "Review and Launch."](images/Screenshot%20(15).png)

***

7. Review the server you are starting and launch

![Review the server you are starting and launch](images/Screenshot%20(16).png)

***

8. Choose and existing key pair and select the SWALLOW key (assuming you have the SWALLOW.pem file, if it is a different key, choose that). Finish up and launch.

![Choose and existing key pair and select the SWALLOW key (assuming you have the SWALLOW.pem file, if it is a different key, choose that). Finish up and launch.](images/Screenshot%20(17).png)

***

## Getting on the server:

1. Find the location of your .pem key
2. Copy the Public DNS for the server to your clipboard

![Copy the Public DNS for the server to your clipboard](images/Screenshot%20(19).png)

3. Open a terminal and type in the command (without parenthesis):
```
ssh -i (absolute/path/to)/SWALLOW.pem -X ubuntu@(paste DNS here)
```
4. If it is your first time, type "yes" when asked to trust the site

## Using the Server

Upon logging in you should see both a copy of this repository and an "ebs" folder. That folder is the mounted EBS drive with the installed software. The repo contains three python scripts and one bash script that gives an example of how to use them. 

### s3_ebs.py 

usage: `s3_ebs.py [-h] (-d | -u) [-l LOCAL] [-s S3_FILE] -b BUCKET [-v VERBOSE]`

 
This script is intended for the prupose of transferring data between the ebs and an s3 bucket. 
If downloading, the tool will download an s3 file which are already tar zipped. It will then unzip them for use. 
If uploading, the tool will tar zip and then upload the zipped file to the s3 bucket of your choice.
Example: `s3_ebs.py -l 'some/local/directory' -s 's3/directory/file' -b 's3-bucket-name' --download`
        

Arguments:
```
  -h, --help            show this help message and exit
  -d, --download        Download file from s3 to ebs. Downloads a tar zipped
                        file and then unzips it. Mutually exculsive with the
                        upload flag.
  -u, --upload          Upload file from ebs to s3. Tar zips the file and then
                        uploads it. Mutually exclusive with the download flag.
  -l LOCAL, --local LOCAL
                        Local data directory where the data is either
                        downloaded to or uploaded from, Default: current
                        directory
  -s S3_FILE, --s3_file S3_FILE
                        s3 data directory where the data is either uploaded to
                        or downloaded from. Used as an object key for boto3.
                        For an explanation on keys, see https://boto3.amazonaw
                        s.com/v1/documentation/api/latest/reference/services/s
                        3.html?highlight=key#S3.Object.key Default: entire
                        bucket
  -b BUCKET, --bucket BUCKET
                        s3 bucket name, required
  -v VERBOSE, --verbose VERBOSE
                        verbosity
```

### data2bids.py

usage: `data2bids.py [-h] [-i INPUT_DIR] [-c CONFIG] [-o OUTPUT_DIR] [-d DICOM_PATH] [-m [MULTI_ECHO [MULTI_ECHO ...]]] [-verb]`

Data2bids is a script based on the SIMEXP lab script to convert nifti MRI files into BIDS format. This script has been modified to 
also parse README data as well as include conversion of DICOM files to nifti. The script utilizes Chris Rorden's Dcm2niix program for 
actual conversion. 

This script takes one of two formats for conversion. The first is a series of DICOM files in sequence with an optional "medata" folder which
contains any number of single or multi-echo uncompressed nifti files (.nii). Note that nifti files in this case must also have a corresponding 
DICOM scan run, but not necessarily scan echo (for example, one DICOM scan for run 5 but three nifti files which are echoes 1, 2, and 3 of
run 5). The other format is a series of nifti files and a README.txt file formatted the same way as it is in the example. Both formats are 
shown in the examples folder.

Both formats use a .json config file that maps either DICOM tags or text within the nifti file name to BIDS metadata. The syntax and formatting of this .json file 
can be found here https://github.com/SIMEXP/Data2Bids#heuristic .

The only thing this script does not account for is event files. If you have the 1D files that's taken care of, but chances are you have some other 
format. If this is the case, I recommend https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/05-task-events.html
so that you can make BIDS compliant event files.

Data2bids documentation at https://github.com/SIMEXP/Data2Bids
Dcm2niix documentation at https://github.com/rordenlab/dcm2niix

Arguments: ```
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir INPUT_DIR
                        Input data directory(ies), must include a readme.txt
                        file formatted like example under examples folder.
                        Mutually exclusive with DICOM directory option.
                        Default: current directory
  -c CONFIG, --config CONFIG
                        JSON configuration file (see https://github.com/SIMEXP
                        /Data2Bids/blob/master/example/config.json)
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Output BIDS directory, Default: Inside current
                        directory
  -d DICOM_PATH, --DICOM_path DICOM_PATH
                        Optional DICOM directory, Mutually exclusive with
                        input directory option
  -m [MULTI_ECHO [MULTI_ECHO ...]], --multi_echo [MULTI_ECHO [MULTI_ECHO ...]]
                        indicator of multi-echo dataset. Only necessary if NOT
                        converting DICOMs. For example, if runs 3-6 were all
                        multi-echo then the flag should look like: -m 3 4 5 6
                        . Additionally, the -m flag may be called by itself if
                        you wish to let data2bids auto-detect multi echo data,
                        but it will not be able to tell you if there is a
                        mistake.
  -verb, --verbose      verbosity
    ```

Made by Aaron Earle-Richardson (ame224@cornell.edu)



