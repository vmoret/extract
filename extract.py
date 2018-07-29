"""extract.py

Extracts commonly used archives recursively.

Usage:
------
python extract.py .\logfiles_ngp001.tgz
python extract.py .\bcmc-logs.tar.gz

History:
--------
V1.0 - VIMO - 28-Jul-2016: initial version
V1.1 - VIMO - 29-Jul-2016: parse params with optparse and add "-d" commandline option.

Dependencies:
-------------
None
"""

import os
import sys
import tarfile
import zipfile
import gzip
from optparse import OptionParser

__version__ = "1.1"


class DummyExtractor:
    def extractall(self, path):
        pass

    def close(self):
        pass

        
class GzipFile:

    def __init__(self, path):
        self.path = path

    def extractall(self, path):
        fh_in = gzip.open(self.path, 'rb')
        fh_out = open(path, 'wb')
        fh_out.write(fh_in.read())
        fh_in.close()
        fh_out.close()
        
        os.remove(self.path)
        
    def close(self):
        pass


def is_archive(path):
    return os.path.isfile(path) and os.path.splitext(path)[-1].lower() in ('.gz', '.tar', '.zip', '.tar', '.tgz')


def find_extractor(path):
    file_name = path.lower()

    return tarfile.open(path, "r:gz") if file_name.endswith(".tar.gz") or file_name.endswith(".tgz") else \
        GzipFile(path) if file_name.endswith(".gz") else \
        tarfile.open(path) if file_name.endswith(".tar") else \
        zipfile.ZipFile(path) if file_name.endswith(".zip") else \
        DummyExtractor()


def extract(path, purge):
    target = os.path.splitext(path)[0]
    extractor = find_extractor(path)
    try:
        extractor.extractall(target)
    except FileExistsError:
        pass
    result = [extract(p, purge) for p in list_dir(target) if is_archive(p)]
    extractor.close()
    if purge and os.path.isfile(path):
        os.remove(path)
    return target, result


def list_dir(path):
    return (os.path.join(p, n) for p, _, names in os.walk(path) for n in names)


def main():
    parser = OptionParser()
    parser.add_option("-d", "--delete", 
                      action="store_true", dest="delete", default=False,
                      help="Delete file after extracting")
    parser.add_option("-p", "--path", 
                      action="store", dest="path", default='.\\bcmc-logs .tar.gz',
                      help="The path of the file or folder to extract")
    (options, args) = parser.parse_args()
    if os.path.isdir(options.path):
        [extract(p, options.delete) for p in list_dir(options.path) if is_archive(p)]
    elif os.path.isfile(options.path):
        extract(options.path, options.delete)
    else:
        print('Path should be a folder or a file.')
        sys.exit(-1)

if __name__ == '__main__':
    main()
