#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon July 29 11:43:54 2019

@author: Aaron Earle-Richardson
"""
import argparse
import os
import re
import nipype
import shutil
from bids import BIDSLayout, BIDSValidator
from bids.layout import models
from nipype.interfaces.fsl import BET
import nipype.interfaces.freesurfer as freesurfer
from nipype.interfaces import afni as afni

def get_parser(): #parses flags at onset of command
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter
        , description=""
        , epilog="""
            Made by Aaron Earle-Richardson (ame224@cornell.edu)
            """)

    parser.add_argument(
        "-i"
        , "--input_dir"
        , required=False
        , default=None
        , help="Input data directory(ies), Default: current directory"
        )
    
    parser.add_argument(
        "-verb"
        , "--verbose"
        , required=False
        , action='store_true' 
        , help="JSON configuration file (see example/config.json)",
        )
    
    parser.add_argument(
        "-o"
        , "--output_dir"
        , required=False
        , default=None
        , help="Output BIDS directory, Default: Inside current directory "
        )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-ex',
        '--exclude',
        nargs='*',
        required=False,
        default=None,
        help="""
        hi
        """)
    group.add_argument(
        '-in',
        '--include',
        nargs='*',
        required=False,
        default=None,
        help="""
        
        """)

    return(parser)

class Preprocessing():
    def __init__(self, input_dir=None, output_dir=None, multi_echo=None, include=None, exclude=None, verbose=False): #sets the .self globalization for self variables
        self._input_dir = None
        self._output_dir = None

        self.set_data_dir(input_dir)
        self.set_out_dir(output_dir)
        self.set_verbosity(verbose)
        if self._data_dir is not None:
            self.set_bids(include,exclude)

    def set_verbosity(self,verbosity):
        if verbosity:
            self._is_verbose = True
        else:
            self._is_verbose = False

    def set_bids(self,include,exclude):

        if exclude is not None:
            parsestr = "|".join(exclude)
        elif include is not None:
            parsestr = "|".join(include)
        else:
            parsestr = None

        if parsestr is not None:
            patterns = ""
            for i in range(len(parsestr)):
                if parsestr[i] in "sS":
                    patterns += ".*sub-"
                elif parsestr[i] in "rR":
                    patterns += ".*run-"
                elif parsestr[i] in "eE":
                    patterns += ".*echo-"
                elif parsestr[i] in "0123456789":
                    if i < len(parsestr)-1:
                        if parsestr[i+1] not in "0123456789":
                            if parsestr[i-1] in "0123456789":
                                patterns += parsestr[i-1:i+1]
                            elif parsestr[i] is "0":
                                    ".*".join(patterns.split(".*")[:-1]) 
                            else:
                                patterns += parsestr[i].zfill(2)
                    elif parsestr[i-1] in "0123456789":
                        patterns += parsestr[i-1:i+1] + ".*"
                    elif parsestr[i] not in "123456789":
                        ".*".join(patterns.split(".*")[:-1]) +".*"
                    else:
                        patterns += parsestr[i].zfill(2) + ".*"
                   
        #print(patterns)
        ignore = []
        for root, _, files in os.walk(self._data_dir):
            for file in files:
                if exclude is not None and re.match(patterns,file):
                    ignore.append(os.path.join(root,file))
                elif include is not None and not re.match(patterns,file):
                    ignore.append(os.path.join(root,file))

        self.BIDS_layout = BIDSLayout(self._data_dir, derivatives=True,ignore=ignore)   

    def get_data_dir(self):
        return self._data_dir

    def set_data_dir(self, data_dir): #check if input dir is listed
        if data_dir is None:
            self._data_dir = os.getcwd()
        else:
            self._data_dir = data_dir

    def set_out_dir(self, output_dir):
        if output_dir is None:
            self._output_dir = self._data_dir + "/derivatives/preprocessing"
        else:
            self._output_dir = output_dir

    def FuncHandler(self,fileobj,output,suffix):

        if type(fileobj) == models.BIDSImageFile: #setting file to temp file before performing operation
            fileobj = fileobj.path
        elif type(fileobj) is not str:
            raise TypeError('file inputs must be either a BIDSImageFile, pathlike string')

        smatch = re.match("(.*\.nii(?:\.gz))(((?:\[|\{)\d+(?:\.\.\d+|)(?:\]|\})){1,2})",fileobj) #sub-brick parser similar to afni's
        if smatch:
            fileobj = smatch.group(1)
            sbmatch = re.match(".*\[(\d+)\].*",smatch.group(2))
            brmatch = re.match(".*\{(\d+)\}.*",smatch.group(2))
            if sbmatch:
                sub_brick = sbmatch.group(1)
            else:
                sub_brick = None
            if brmatch:
                brick_range = brmatch.group(1)
            else:
                brick_range = None
        else:
            sub_brick = None
            brick_range = None
        
        if not os.path.isabs(fileobj) or not os.path.isfile(fileobj): #checking if file exists and address is absolute
            tempfileobj = os.path.abspath(fileobj)
            if not os.path.isfile(tempfileobj) and self._data_dir is not None: #checking working directory for file
                tempfileobj = os.path.join(self.BIDS_layout.root,fileobj)
                if not os.path.isfile(tempfileobj) and self._output_dir is not None: #checiking BIDS root directory for file
                    tempfileobj = os.path.join(self._output_dir, fileobj)
                    if not os.path.isfile(tempfileobj):         #checking BIDS derivatives derectory for file
                        raise FileNotFoundError("could not find {filename} in derivatives, working, or root directory, check naming and try again".format(filename=fileobj))
                    else:
                        fileobj = tempfileobj
                else:
                    fileobj = tempfileobj
            else:
                fileobj = tempfileobj

        if output == None and suffix == None:
            output = fileobj
            fileobj = output.split('.nii.gz')[0] + "_desc-temp.nii.gz"
            os.replace(output,fileobj)
        elif output == None:
            output = fileobj.split('.nii.gz')[0] + "_desc-" + suffix + '.nii.gz'
        elif suffix == None:
            pass
        else:
            print("both suffix and output filename detected as input, using filename given")
        return(fileobj,output)
            


    ### These are the standalone tools, useable on their own and customiseable for alternate preprocessing algorithms.
    # it is recommended that you not edit anything above this line (excluding package imports) without a serious knowledge of python and this script 

    #cortical reconstruction
    def cortical_recon(self,filepath=None):
        if filepath == None:
            filepath = self._data_dir
        freesurfer.ReconAll(filepath)

    def skullstrip(self,fileobj=None,out_file=None,args=None,suffix=None):

        #setting files
        fileobj, out_file = self.FuncHandler(fileobj,out_file,suffix=suffix)

        args_in = "" #add in terminal flags here (ex: "-overwrite") if you want them called with ubiquity
                    #accross the whole script any time this command is called. Otherwise add flags the the "args" argument of the command
        if args is not None:
            args_in = args_in + args
        #running skull stripping (change this to change skull stripping program)
        BET(in_file=fileobj,out_file=out_file,args=args_in).run()

        #remove temp files
        if type(fileobj) == models.BIDSImageFile:
            fileobj = os.path.join(self._output_dir,fileobj.filename)
        if "_desc-temp" in fileobj:
            os.remove(fileobj)

    def despike(self,fileobj=None,out_file=None,args=None,suffix=None):

        #setting files
        fileobj, out_file = self.FuncHandler(fileobj,out_file,suffix=suffix)
        args_in = "-overwrite" #add in terminal flags here (ex: "-overwrite") if you want them called with ubiquity
                    #accross the whole script any time this command is called. Otherwise add flags the the "args" argument of the command
        if args is not None:
            args_in = args_in + args

        afni.Despike(in_file=fileobj,out_file=out_file,args=args_in).run()

        #remove temp files
        if type(fileobj) == models.BIDSImageFile:
            fileobj = os.path.join(self._output_dir,fileobj.filename)
        if "_desc-temp" in fileobj:
            os.remove(fileobj)

    def warp(self,fileobj1=None,fileobj2=None,out_file=None,transformation=None,args=None,saved_mat_file=None,suffix=None):

        #setting files
        fileobj1, out_file = self.FuncHandler(fileobj1,out_file,suffix=None)
    
        ThreeDWarp = afni.Warp(in_file=fileobj1,out_file=out_file)
        if args is not None:
            ThreeDWarp.inputs.args=args
        if transformation == 'card2oblique':
            ThreeDWarp.inputs.oblique_parent = fileobj2
            
        elif transformation == 'deoblique':
            ThreeDWarp.inputs.deoblique = True
        elif transformation == 'mni2tta':
            ThreeDWarp.inputs.mni2tta = True
        elif transformation == 'tta2mni':
            ThreeDWarp.inputs.tta2mni = True
        elif transformation == 'matrix':
            ThreeDWarp.inputs.matparent = fileobj2
        elif transformation == None:
            print("Warning: no transformation input given")
        else:
            print("Warning: none of the transformation options given match the possible arguments. Matching arguments are card2oblique,"+
             " deoblique, mni2tta, tta2mni, and matrix")

        if saved_mat_file: #this is for if the pipline requires saving the 1D matrix tranformation information
            print('saving matrix')
            ThreeDWarp.inputs.verbose = True
            ThreeDWarp.inputs.save_warp = True
            
        ThreeDWarp.run()

        #remove temp files
        if type(fileobj1) == models.BIDSImageFile:
            fileobj1 = os.path.join(self._output_dir,fileobj1.filename)
        if "_desc-temp" in fileobj1:
            os.remove(fileobj1)

    def axialize(self,fileobj=None,out_file=None,args=None,suffix=None):

        fileobj, out_file = self.FuncHandler(fileobj,out_file,suffix=suffix)

        args_in = "-overwrite" #add in terminal flags here (ex: "-overwrite") if you want them called with ubiquity
                    #accross the whole script any time this command is called. Otherwise add flags the the "args" argument of the command
        if args is not None:
            args_in = args_in + args
        
        afni.Axialize(in_file=fileobj,out_file=out_file, args=args_in).run()

        #remove temp files
        if type(fileobj) == models.BIDSImageFile:
            fileobj = os.path.join(self._output_dir,fileobj.filename)
        if "_desc-temp" in fileobj:
            os.remove(fileobj)

    def volreg(self,in_file=None,out_file=None,suffix=None,base=None,tshift=None,interpolation=None):

        in_file, out_file = self.FuncHandler(in_file,out_file,suffix=suffix)

   
    
if __name__ == "__main__":
    args = get_parser().parse_args()
    pre = Preprocessing(**vars(args))

    #delete any preprocessing files not supposed to be there
    for root,_,files in os.walk(pre._output_dir):
        for file in files:
            if ".nii.gz" in file or ".mat" in file or ".1D" in file:
                filepath = os.path.join(root,file)
                os.remove(filepath)

    #getting all the subjects into place
        sub_ids = pre.BIDS_layout.get_subjects()

    #Main preprocessing pipeline: uses tools defined above
    for sub_id in sub_ids :


        #Defining which images we care about and setting the basenames
        all_fobj = []
        for BIDSFiles in pre.BIDS_layout.get(scope='raw',subject=sub_id,suffix='bold',extension='.nii.gz'):
            all_fobj.append(BIDSFiles)

        for BIDSFiles in pre.BIDS_layout.get(scope='raw',extension='.nii.gz',suffix='T1w',acquisition='MPRAGE', subject=sub_id):
            all_fobj.append(BIDSFiles)

        #copying those files to a new derivatives directory so we can mess with them
        for i in range(len(all_fobj)):
            if pre._is_verbose:
                print("copying {filename} to preprocessing derivatives directory".format(filename=all_fobj[i].path))
            try:
                shutil.copy(all_fobj[i].path,pre._output_dir)
            except shutil.SameFileError:
                print("{files} already exists in the preprocessing directory, overwriting...".format(files=all_fobj[i].filename))

        # skull stripping
        if pre._is_verbose:
            print("performing skull stripping")
        filenames = pre.BIDS_layout.get(scope='derivatives', subject=sub_id, extension='.nii.gz',return_type="filename",acquisition="MPRAGE")
        for filename in filenames:
            print(filename)
            pre.skullstrip(filename)
            pre.warp(filename,transformation='deoblique',out_file=filename.split('.nii.gz')[0] + "_do.nii.gz")

        #Calculate and save motion and obliquity parameters, despiking first if not disabled, and separately save and mask the base volume
        #assuming only one anatomical image
        if pre._is_verbose:
            print("denoising and saving motion parameters")
        for fobj in pre.BIDS_layout.get(scope='derivatives', subject=sub_id, extension='.nii.gz', suffix='bold', echo='01'):
            for anat in pre.BIDS_layout.get(scope='derivatives', subject=sub_id, extension='.nii.gz',acquisition='MPRAGE'):
                pre.warp(fileobj2=fobj.path,fileobj1=anat.path,args="-newgrid 1.000000",saved_mat_file=True, 
                transformation='card2oblique',suffix="anat_to_s"+str(fobj.get_entities()['subject']).zfill(2)+"r"+
                str(fobj.get_entities()['run']).zfill(2))  #saving the transformation matrix for later
            pre.despike(fobj.path,out_file=fobj.path.split(".nii.gz")[0]+"_desc-vrA.nii.gz")
            pre.axialize(fobj.path.split(".nii.gz")[0]+"_desc-vrA.nii.gz")

        #print("Performing cortical reconstruction on %s" %sub_id)
        #preprocess.cortical_recon(bids_obj)
    #preprocess.anat()