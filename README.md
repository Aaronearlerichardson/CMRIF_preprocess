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
2. Open a terminal and type in the command:
```
ssh -i absolute/path/to/SWALLOW.pem -X ubuntu@ec2-18-220-67-88.us-east-2.compute.amazonaws.com
```
