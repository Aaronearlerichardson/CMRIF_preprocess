from __future__ import division
import boto3
import argparse
import os
import sys
import botocore
import tarfile
import io
from multiprocessing import Pool, current_process, cpu_count

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
    parser.add_argument(
        "-v"
        , "--verbose"
        , required=False
        , help="verbosity"
    )
    
    return(parser)

class Transfer():
    def __init__(self,bucket,download=False,upload=False,local=os.getcwd(),s3_file="",verbose=False):
        self._bucket_name = bucket
        self._local = local
        self._download = download
        self._upload = upload
        self._s3_file = s3_file
        self._is_verbose = verbose


    def download_dir(self, prefix, local, bucket, client=boto3.client('s3'), num_chunks=1000):
        """
        params:
        - prefix: pattern to match in s3
        - local: local path to folder in which to place files
        - bucket: s3 bucket with target contents
        - client: initialized s3 client object
        - num_chunks: number of chunks the filedata is split up into during multiprocessing
        """
        keys = []
        dirs = []
        next_token = ''
        base_kwargs = {
            'Bucket':bucket,
            'Prefix':prefix,
        }
        print("finding all files...")
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


        p2 = Pool()
        sys.stderr.write("\n")
        chunksize = max(int(len(keys)/(cpu_count()*num_chunks)),1)
        for i, _ in enumerate(p2.imap(self.download_thread, keys, chunksize), 1):
            sys.stderr.write('\rDownloading Files: {0:.2%}'.format(i/len(keys)))
        p2.close()
        p2.join()

    def download_thread(self,k):
        dest_pathname = os.path.join(self._local, k)
        os.makedirs(os.path.dirname(dest_pathname),exist_ok=True)
        process_name = current_process().name
        if self._is_verbose:
            print("{pid} is downloading {key} to {dir} \n".format(key=k,dir=dest_pathname,pid=process_name))
        boto3.client('s3').download_file(self._bucket_name, k, dest_pathname)
        if (dest_pathname.endswith("tar.gz")):
            if self._is_verbose:
                print("{pid} is unzipping {key} to {dir} \n".format(key=dest_pathname,dir=dest_pathname.split(".tar.gz")[0],pid=process_name))
            sys.stderr.write("\n")
            tar = tarfile.open(dest_pathname, "r:gz", fileobj=ProgressFileObject(dest_pathname))
            tar.extractall(os.path.dirname(dest_pathname))
            tar.close()
            os.remove(dest_pathname)
        elif (dest_pathname.endswith(",tar")):
            if self._is_verbose:
                print("{pid} is unzipping {key} to {dir} \n".format(key=dest_pathname,dir=dest_pathname.split(",tar")[0],pid=process_name))
            sys.stderr.write("\n")
            tar = tarfile.open(dest_pathname, "r:")
            tar.extractall(os.path.dirname(dest_pathname))
            tar.close()
            os.remove(dest_pathname)

    def percent_cb(self, complete, total):
        sys.stdout.write('.')
        sys.stdout.flush()

    def upload_dir(self, sourceDir,bucket_name,destDir):

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
                    mp.upload_part_from_file(fp, fp_num, cb=self.percent_cb, num_cb=10, size=PART_SIZE)

                mp.complete_upload()

            else:
                #print("singlepart upload")
                #k = botocore.s3.key.Key(bucket)
                #k.key = destpath
                #k.set_contents_from_filename(sourcepath,
                        #cb=percent_cb, num_cb=10)
                pass

def get_file_progress_file_object_class():
    class FileProgressFileObject(tarfile.ExFileObject):
        def read(self, size, *args):
            on_progress(self.name, super.position, super.size)
            return tarfile.ExFileObject.read(self, size, *args)
    return FileProgressFileObject

tarfile.TarFile.fileobject = get_file_progress_file_object_class()
    
def on_progress(filename, position, total_size):
    print("%s: %d of %s" %(filename, position, total_size))

class TestFileProgressFileObject(tarfile.ExFileObject):
    def read(self, size, *args):
        on_progress(self.name, super.position, super.size)
        return tarfile.ExFileObject.read(self, size, *args)

class ProgressFileObject(io.FileIO):
    def __init__(self, path, *args, **kwargs):
        self._total_size = os.path.getsize(path)
        io.FileIO.__init__(self, path, *args, **kwargs)

    def read(self, size):
        sys.stderr.write("\rUnzipping file: {0:.2%}".format(self.tell()/self._total_size))
        return io.FileIO.read(self, size)



if __name__ == "__main__":
    args = get_parser().parse_args()
    tr = Transfer(**vars(args))

    if tr._download:
        print("Beginning download")
        tr.download_dir(tr._s3_file,tr._local,tr._bucket_name)
    elif tr._upload:
        pass
