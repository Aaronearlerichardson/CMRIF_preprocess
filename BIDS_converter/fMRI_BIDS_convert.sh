#
# A code that automatically converts CMRIF NIFTI 1 and DICOM files into BIDS format
# requires dcm2niix and dos2unix to be installed 
# total list of subjects:1299	1329	1351	1358	1409	1421	1437	1440	1675	1685	1669	1709	1713	1717	1722	1731	1734	1743	1752	1773	1777	1780	1846	1870	1877	1941	1996	2000	2083	2910
    
ORIG_DATA_DIR="/media/sf_Ubuntu_files/sourcedata/DICOM" #input directory, on server: \\132.236.250.219\fMRI\RAW Backups of medata \\132.236.250.219\fMRI\projects\tempAttnAudT\/tAAT[sp]##/medata

OUTPUT_DIR="/media/sf_Ubuntu_files/sourcedata/nifti-1" #on server:

TSV_DIR="/media/sf_Ubuntu_files/sourcedata/nifti-1/timing_files" #on server: \\132.236.250.219\fMRI\projects\tempAttnAudT\analysis

README_DIR="/media/sf_Ubuntu_files/sourcedata/nifti-1/readme_files" #on server: \\132.236.250.219\fMRI\projects\tempAttnAudT

BIDS_DIR="/media/sf_Ubuntu_files/Workspace"

SUB_IDS=(3033) 

#declare -l mylist[30]

for SUB_ID in ${SUB_IDS[@]}
 do 
    if [ $(hostname -d) -eq "us-east-2.compute.internal" ] && [ ! -d $ORIG_DATA_DIR/$SUB_ID ] ; then 
        cd ..
        python3 s3_ebs.py -l $OUTPUT_DIR -s "RAW/$SUB_ID" -b "amplab-master" --download
        cd /BIDS_converter
    fi

    #echo $MELIST
    
	#the big bad python code to convert the renamed files to BIDS
	#requires numpy, nibabel, and pathlib modules
    echo $PWD
    python3 data2bids.py -c config.json -d $ORIG_DATA_DIR/$SUB_ID -o $BIDS_DIR || { echo "BIDS conversion for $SUB_ID failed, trying next subject" ; continue; }

    # preprocess the BIDS formatted subject
    # requires pybids, nipype, 
    cd .. 
    python3 CMRIF_preprocess.py -i $BIDS_DIR -in s${SUB_NUM} -verb || { echo "preprocessing for $SUB_ID failed, trying next subject" ; cd $CWD; continue; }
    cd /BIDS_converter

    RAN_SUBS+=${SUB_ID}" "
    echo "subjects ran: $RAN_SUBS"

    #python data2bids.py -d /media/sf_Ubuntu_files/Workspace/${SUB_NUM} -c /media/sf_Ubuntu_files/BIDS_converter/config.json -o /media/sf_Ubuntu_files/workspace/bids -m 4

    #-f %c_%d_%e_%f_%i_%n_%p_%t_%z
done
echo "Finished"