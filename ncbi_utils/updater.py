import sys
sys.path.append("..")
# package scripts
from dochap_tools.common_utils import conf
from dochap_tools.common_utils import utils
from dochap_tools.ncbi_utils import downloader
import os

def check_for_updates():
    # check if existing specie files need an update
    # go over all existing folders that have a readme in 'data' folder
    root_dir = 'data'
    sub_dirs = utils.get_immediate_subdirectories(root_dir)
    for sub_dir in sub_dirs:
        if os.path.isfile(os.path.join(root_dir,sub_dir,'readme')):
            if (check_up_to_date(sub_dir,root_dir)):
                print(f'{sub_dir} is up to date!')
            else:
                print(f'{sub_dir} needs an update!')


def check_up_to_date(specie,root_dir):
    print(f'Checking if {specie} is up to date...')
    ftp = utils.create_ftp_connection(conf.NCBI_FTP_ADDRESS)
    download_sub_folder = os.path.join(root_dir,specie)
    downloader.download_readme(ftp,specie,download_sub_folder,'readme_new')
    with open(os.path.join(download_sub_folder,'readme_new')) as f:
        new_readme_content = f.read()
    with open(os.path.join(download_sub_folder,'readme')) as f:
        old_readme_content = f.read()
    os.remove(os.path.join(download_sub_folder,'readme_new'))
    if new_readme_content == old_readme_content:
        return True
    return False



if __name__ == '__main__':
    check_for_updates()

