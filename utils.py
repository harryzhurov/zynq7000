
import os


#-------------------------------------------------------------------------------
def read_file(fname):
    with open(fname, 'rb') as f:
        b = f.read()
    
    return b.decode()
    
#-------------------------------------------------------------------------------
def write_file(fname, data):
    with open(fname, 'wb') as f:
        f.write(data.encode('utf-8'))
        
#-------------------------------------------------------------------------------
def namegen(fullpath, ext):
    basename = os.path.basename(fullpath)
    name     = os.path.splitext(basename)[0]
    return name + os.path.extsep + ext
#-------------------------------------------------------------------------------
