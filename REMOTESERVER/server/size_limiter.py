import os
import glob

# Not sure if this is a good idea since deleted footaged might be synced again

FOOTAGE_DIRECTORY = '/home/goosealert/goosealert-footage/*'

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def check_capacity():

    print('Checking capacity')

    MAX_DIR_SIZE = 40

    while get_size(FOOTAGE_DIRECTORY) / 1000000000 > MAX_DIR_SIZE:

        print('Dir is larger than limit!!!!')

        target_file = sorted(glob.glob(FOOTAGE_DIRECTORY))[0]

        print('Deleting', target_file)

        os.remove(target_file)


