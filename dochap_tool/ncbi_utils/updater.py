import sys
import os
# add to path if need to
import_path = '/'.join(__file__.split('/')[:-1])
import_path = os.path.normpath(os.path.join(import_path,'../'))
if import_path not in sys.path:
    sys.path.append(os.path.join(import_path))
# package files
from dochap_tool.common_utils import conf
from dochap_tool.common_utils import utils
from dochap_tool.ncbi_utils import downloader

def check_for_updates(root_dir):
    # check if existing specie files need an update
    # go over all existing folders that have a readme in 'data' folder
    sub_dirs = utils.get_immediate_subdirectories(root_dir)
    need_to_update = []
    up_to_date = []
    for sub_dir in sub_dirs:
        if os.path.isfile(os.path.join(root_dir,sub_dir,'readme')):
            if (check_up_to_date(sub_dir,root_dir)):
                up_to_date.append(sub_dir)
            else:
                need_to_update.append(sub_dir)
    print('Summary:')
    for specie in up_to_date:
        print(f'--- {specie} ===> Up to date!')
    for specie in need_to_update:
        print(f'--- {specie} ===> Update required!')


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

