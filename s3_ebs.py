import boto3
import argparse
import os
import sys
import botocore

def get_parser(): #parses flags at onset of command
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter
        , description=" s3_ebs.py -l 'some/local/directory' -s 's3/directory/file' -b 's3-bucket-name' --download  "
        , epilog="""
            Made by Aaron Earle-Richardson (ame224@cornell.edu)
            """)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-d',
        '--download',
        action='store_true',
        required=False,
        default=False,
        help="""
        
        """)
    group.add_argument(
        '-u',
        '--upload',
        action='store_true',
        required=False,
        default=False,
        help="""
        
        """)
    parser.add_argument(
        "-l"
        , "--local"
        , required=False
        , default=os.getcwd()
        , help="Local data directory(ies), Default: current directory"
        )
    parser.add_argument(
        "-s"
        , "--s3_file"
        , required=False
        , default=""
        , help="s3 data directory(ies), Default: all/root"
        )
    parser.add_argument(
        "-b"
        , "--bucket"
        , required=True
        , help="s3 bucket name, required"
        )

def download_dir(prefix, local, bucket, client=boto3.client('s3')):
    """
    params:
    - prefix: pattern to match in s3
    - local: local path to folder in which to place files
    - bucket: s3 bucket with target contents
    - client: initialized s3 client object
    """
    keys = []
    dirs = []
    next_token = ''
    base_kwargs = {
        'Bucket':bucket,
        'Prefix':prefix,
    }
    while next_token is not None:
        kwargs = base_kwargs.copy()
        if next_token != '':
            kwargs.update({'ContinuationToken': next_token})
        results = boto3.client('s3').list_objects_v2(**kwargs)
        contents = results.get('Contents')
        for i in contents:
            k = i.get('Key')
            if k[-1] != '/':
                keys.append(k)
            else:
                dirs.append(k)
        next_token = results.get('NextContinuationToken')
    for d in dirs:
        dest_pathname = os.path.join(local, d)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
    for k in keys:
        dest_pathname = os.path.join(local, k)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
        print("downloading {key} to {dir}".format(key=k,dir=dest_pathname))
        boto3.client('s3').download_file(bucket, k, dest_pathname)

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

def upload_dir(sourceDir,bucket_name,destDir):

    s3 = boto3.client('s3')

    #max size in bytes before uploading in parts. between 1 and 5 GB recommended
    MAX_SIZE = 5 * 1000 * 1000
    #size of parts when uploading in parts
    PART_SIZE = 1 * 1000 * 1000

    bucket = s3.Bucket(bucket_name)

    uploadFileNames = []
    for (sourceDir, dirname, filename) in os.walk(sourceDir):
        uploadFileNames.extend(filename)
        break

    for filename in uploadFileNames:
        sourcepath = os.path.join(sourceDir + filename)
        destpath = os.path.join(destDir, filename)
        print('Uploading %s to Amazon S3 bucket %s' % \
            (sourcepath, bucket_name))

        filesize = os.path.getsize(sourcepath)
        if filesize > MAX_SIZE:
            print("multipart upload")
            mp = bucket.create_multipart_upload(destpath)
            fp = open(sourcepath,'rb')
            fp_num = 0
            while (fp.tell() < filesize):
                fp_num += 1
                print("uploading part %i" %fp_num)
                mp.upload_part_from_file(fp, fp_num, cb=percent_cb, num_cb=10, size=PART_SIZE)

            mp.complete_upload()

        else:
            #print("singlepart upload")
            #k = botocore.s3.key.Key(bucket)
            #k.key = destpath
            #k.set_contents_from_filename(sourcepath,
                    #cb=percent_cb, num_cb=10)
            pass

if __name__ == "__main__":
    args = get_parser().parse_args()

    #locals().update(vars(args))
    s3_file = vars(args)['s3_file']
    local = vars(args)['local']
    bucket = vars(args)['bucket']
    download = vars(args)['download']
    upload = vars(args)['upload']

    if download:
        download_dir(s3_file,local,bucket)
    elif upload:
        pass
