#
# A code that automatically converts CMRIF NIFTI 1 and DICOM files into BIDS format
# requires dcm2niix and dos2unix to be installed 
# total list of subjects:1299	1329	1351	1358	1409	1421	1437	1440	1675	1685	1669	1709	1713	1717	1722	1731	1734	1743	1752	1773	1777	1780	1846	1870	1877	1941	1996	2000	2083	2910
    
ORIG_DATA_DIR="~/ebs" #input directory, on server: \\132.236.250.219\fMRI\RAW Backups of medata \\132.236.250.219\fMRI\projects\temp$

OUTPUT_DIR="~/ebs/nifti" #on server:

TSV_DIR="~/timing_files" #on server: \\132.236.250.219\fMRI\projects\tempAttnAudT\analysis

README_DIR="~/readme_files" #on server: \\132.236.250.219\fMRI\projects\tempAttnAudT

BIDS_DIR="~/ebs/BIDS"

SUB_IDS=(1846) 

#declare -l mylist[30]

for SUB_ID in ${SUB_IDS[@]}
 do 
    if [[ $(hostname -d) == "us-east-2.compute.internal" ]]; then
        if [[ -d $ORIG_DATA_DIR/$SUB_ID ]] ; then
            rm -rf $ORIG_DATA_DIR/$SUB_ID
        fi
        cur_dir=$CWD
        cd ..
        python3 s3_ebs.py -l $ORIG_DATA_DIR -s "RAW/$SUB_ID" -b "amplab-master" --download
        cd $cur_dir
    fi
    MELIST=()
    DATA_DIR=($ORIG_DATA_DIR/$SUB_ID) #input directory

    #start by finding the correct readme file for any particular subject
    #then scan the readme for date and scan label using sed
    for LABEL in $README_DIR/tAAT* ; do #search all the readme files for the subid
        num=$(echo ${LABEL} | sed -rn 's/(.*tAAT[sp])(.*)/\2/p')
        string="$(cat $(ls ${LABEL}/*README.txt) | sed -n '/Exam#:/p')"
        if  [[ $string == *$SUB_ID* ]]  ; then
	    #echo $LABEL
            SUB_NUM=$( printf '%02d' ${num})
            README_FILE=$(ls ${LABEL}/*README.txt)
            if [[ "$(cat $README_FILE | sed -n '/Pilot/p')" != "" ]] ; then
                SUB_NUM=$(echo p$SUB_NUM)
                letter="p"
            else letter="s"
            fi
	    #the command below is only necessary if you are getting erroneous '$' or '\r' characters in your file names. It requires that you have 
            #dos2unix "${LABEL}/tAAT$letter${num}_README.txt"
           
            while read p; do
                if [[ $p =~ ^[1-9][0-9]?\..*$ ]]; then
                    if [ "$(echo $p | awk '{print $2}' )" == "ax" ] ; then
                        mylist[$(echo $p | sed -n 's/\([0-9]\{1,2\}\)\.\([^_]*\) .*/\1/p')]="$(echo $p | awk '{print $2,$3,$4}' )"
                    else
                        mylist[$(echo $p | sed -n 's/\([0-9]\{1,2\}\)\.\([^_]*\) .*/\1/p')]="$(echo $p | awk '{print $2}' )"
                    fi
                #echo "$(echo $p | awk '{print $2}' )"
                elif [[ $p =~ ^[0-9]{1,2}-[0-9]{1,2}(,?\ ?[0-9]{1,2})*\..*$ ]]; then
                    first=$(echo $p | sed -n 's/\([0-9]\{1,2\}\)-\([0-9]\{1,2\}\)\..*$/\1/p')
                    second=$(echo $p | sed -n 's/\([0-9]\{1,2\}\)-\([0-9]\{1,2\}\)\..*$/\2/p')
                    for i in $(seq $first $second) ; do mylist[$i]="$(echo $p | awk '{print $2}' )"; done
                    if [[ $p =~ ^[0-9]{1,2}-[0-9]{1,2}(,?\ ?[0-9]{1,2})+\..*$ ]] ; then
                        for i in $( printf "$p" | sed 's/,/ /g' | sed -n 's/\([0-9]\{1,2\}\)-\([0-9]\{1,2\}\)\(\(\ \+\([0-9]\{1,2\}\)\)\{0,20\}\)\..*$/\3/p')
                            do mylist[$i]=$( printf "$p" | sed 's/,/ /g' | sed -n 's/\([0-9]\{1,2\}\)-\([0-9]\{1,2\}\)\(\(\ \+\([0-9]\{1,2\}\)\)\{0,20\}\)\.\ \?\([^\ ]\+\).*$/\6/p')
                        done
                    fi
                elif  [[ $p =~ ^(,?\ ?[0-9]{1,2})+\.[^@]*$ ]]; then 
                    for i in $( printf "$p" | sed 's/,/ /g' | sed -n 's/\(\(\ \+\([0-9]\{1,2\}\)\)\{0,20\}\)\..*$/\1/p')
                    do
						mylist[$i]=$( printf "$p" | sed 's/,/ /g' | sed -n 's/\(\(\ \+\([0-9]\{1,2\}\)\)\{0,20\}\)\.\ \?\([^\ ]\+\).*$/\4/p') 
                    done
                    #else echo "Error, README file scans not correctly enumerated at this line: $p" 1>&2
                    #exit 64    
                    #eval mylist[$(seq $first $second)]="$(echo $p | sed -n 's/\([0-9]\{1,2\}\)-\([0-9]\{1,2\}\)\.\([^ tab]\+\).*$/\3/p')"
                fi
            done <$README_FILE
            #for i in {1..15} ; do echo "${mylist[i]}" ; done
            #break 3
            #else
            #echo "no participant files for scan $SUB_ID" 1>&2  
        fi
    done

    #start with the DICOM files

    CWD=$(pwd)
	if [[ ! -d "$OUTPUT_DIR/BIDS/" ]] ; then
    	mkdir $OUTPUT_DIR/BIDS
	fi

    cd $OUTPUT_DIR
    if [[ -d "$OUTPUT_DIR/sub${SUB_NUM}/" ]] ; then
        rm -rfd $OUTPUT_DIR/sub${SUB_NUM}/
        echo "deleting preexisting directory for subject ${SUB_NUM}"
    fi
    mkdir sub${SUB_NUM} #making a directory for dcm2bids to play and not destroy anything
    cd sub${SUB_NUM}

    cp $README_FILE $OUTPUT_DIR/sub${SUB_NUM}/README.txt
    mkdir $OUTPUT_DIR/sub${SUB_NUM}/condition-timing
    mkdir $OUTPUT_DIR/sub${SUB_NUM}/fso-timing
    cp $TSV_DIR/condition-timing/stimes-${SUB_ID}*.1D $OUTPUT_DIR/sub${SUB_NUM}/condition-timing/
    for tfiles in $TSV_DIR/fso-timin*/stimes-${SUB_ID}*.1D ; do
	if ! [ -f $OUTPUT_DIR/sub${SUB_NUM}/fso-timing/$(echo $tfiles | sed -n 's/.*\/\(stimes.*\.1D\).*$/\1/p' ) ] ; then
		cp $tfiles $OUTPUT_DIR/sub${SUB_NUM}/fso-timing/
	fi
    done
    for i in $(seq 1 ${#mylist[@]}) ; do
        SCAN_NUM=$( printf '%04d' ${i})
        SWITCH=0
		if [[ -d $DATA_DIR/medata/ ]]; then 
		    for j in $DATA_DIR/medata/run* ; do
		        if [[ $j == *run${SCAN_NUM:2:4}* ]] ; then SWITCH=1 ; fi
		    done
		fi
        anotherlist[$i]=$SWITCH
        #continue
        if [[ $SWITCH == 0 ]] ; then #echo "peforming dcm2niix" 
            dcm2niix -z y -f %f_%p_%t_%s -o $OUTPUT_DIR/sub${SUB_NUM}/ -b y $DATA_DIR/$SCAN_NUM #; fi #perform full dcm2niix only if there is no ME .nii file already there
        else dcm2niix -z y -f %f_%p_%t_%s -o $OUTPUT_DIR/sub${SUB_NUM}/ -s y -b y $DATA_DIR/$SCAN_NUM/000001*
        fi
        
    done


    #add all extra files to temp output

    
    #Copying Multi-echo files and replacing the bad dcm converted version. 
    #also renaming all the files to the data2bids friendly format
    SWITCH=0
    n=0
    for FILE in *nii.gz
     do
        filestring=$(echo $FILE | sed -n "s/\([0-9]\{4\}\)_\([^\.]*\)\.nii\(.gz\)\?/\2/p")
	if [[ $filestring == _* ]] ; then 
            filestring=${%?filestring}
        fi 
        RUNNUM=${FILE:2:2}
        if [[ $RUNNUM == *_ ]] ; then 
            RUNNUM=${RUNNUM%?}
        fi

        #renaming the rest of the MRI files assuming the DICOMS were stored in a folder with the name of the subject id

        IMAGEID=${mylist[$( echo ${RUNNUM} | awk '$0*=1')]}
	IMAGEID=$(echo $IMAGEID | tr -dc '[[:alnum:]-_]\n')
		#echo $IMAGEID
        if [[ $IMAGEID == *_ ]] ; then 
            IMAGEID=${IMAGEID%?}
        fi
        echo ${filestring}
        ANAT_IDENT=$( echo $filestring | sed -n 's/^.*[0-9]\{12,14\}_\([0-9]\{1,2\}[^_]\?\).*$/\1/p')
        if [[ ANAT_IDENT != "" ]] ; then
            ANAT_IDENT+="_"
        fi
	ANAT_IDENT=$( echo $ANAT_IDENT | tr -d '\r')
	SESSION=$( echo $filestring | sed -n 's/^.*_\([0-9]\{12,14\}\)_.*$/\1/p')
	#echo $SESSION
        if [[ ${anotherlist[$( echo ${RUNNUM} | awk '$0*=1')]} == 1 ]]  #if we are looking at the Multi-echo data
         then
            i=0
            for DATFILE in $DATA_DIR/medata/run$RUNNUM* #copy over the good ME files
             do
                i=$((i+1))
                NUM=$( printf '%02d' $i )

                #copying, renaming and duplicating Multi-echo files and sidecars
                cp ${DATFILE} $OUTPUT_DIR/sub${SUB_NUM}/run${RUNNUM}_${IMAGEID}_$( echo $SESSION )_sub${SUB_NUM}.e${NUM}.nii
		#gzip $OUTPUT_DIR/sub${SUB_NUM}/run${RUNNUM}_${IMAGEID}_$( echo $SESSION )_sub${SUB_NUM}.e${NUM}.nii
                cp ${FILE:0:2}${RUNNUM}*json $OUTPUT_DIR/sub${SUB_NUM}/run${RUNNUM}_${IMAGEID}_$( echo $SESSION )_sub${SUB_NUM}.e${NUM}.json

            done

            MELIST+=($( echo ${RUNNUM} | awk '$0*=1'))
            rm ${FILE:0:4}*.json #remove old .json for ME
            rm $OUTPUT_DIR/sub${SUB_NUM}/$FILE #remove the bad DICOM converted file

        else
	    #echo "$FILE $OUTPUT_DIR/sub${SUB_NUM}/run${RUNNUM}_${IMAGEID}_${ANAT_IDENT}$( echo $SESSION )_sub${SUB_NUM}.nii.gz"
            mv ${FILE:0:4}_${filestring}.json ${OUTPUT_DIR}/sub${SUB_NUM}/run${RUNNUM}"_"${IMAGEID}"_"${ANAT_IDENT}$( echo $SESSION )"_"sub${SUB_NUM}.json
            mv $FILE $OUTPUT_DIR/sub${SUB_NUM}/run${RUNNUM}_${IMAGEID}_${ANAT_IDENT}$( echo $SESSION )_sub${SUB_NUM}.nii.gz
        fi
        n=$((n+1))
    done

    #echo ${MELIST[@]}
    #activating data2bids

    cd $CWD
    #echo $MELIST
    
	#the big bad python code to convert the renamed files to BIDS
	#requires numpy, nibabel, and pathlib modules
    python3 data2bids.py -i $OUTPUT_DIR/sub${SUB_NUM} -c $CWD/config.json -d $DATA_DIR -o $BIDS_DIR -m ${MELIST[@]} || { echo "BIDS conversion for $SUB_ID failed, trying next subject" ; continue; }

    # preprocess the BIDS formatted subject
    # requires pybids, nipype, 
    cd .. 
    python3 CMRIF_preprocess.py -i $BIDS_DIR -in s${SUB_NUM} -verb || { echo "preprocessing for $SUB_ID failed, trying next subject" ; cd $CWD; continue; }
    cd $CWD


    RAN_SUBS+=${SUB_ID}" "
    echo "subjects ran: $RAN_SUBS"

    #python data2bids.py -d /media/sf_Ubuntu_files/Workspace/${SUB_NUM} -c /media/sf_Ubuntu_files/BIDS_converter/config.json -o /media/sf_Ubuntu_files/workspace/bids -m 4

    #-f %c_%d_%e_%f_%i_%n_%p_%t_%z
done
echo "Finished"
