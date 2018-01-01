# outside packages
import sys
import os
import ftplib
# add to path if need to
import_path = '/'.join(__file__.split('/')[:-1])
import_path = os.path.normpath(os.path.join(import_path,'../'))
if import_path not in sys.path:
    sys.path.append(os.path.join(import_path))
# package scripts
from dochap_tool.common_utils import conf
from dochap_tool.common_utils import utils

def download_readme(ftp,specie,download_sub_folder,filename='readme'):
    print(f'downloading readme of {specie}...')
    ftp.sendcmd('TYPE i')
    readme_path = conf.get_readme_path(specie)
    readme_download_path = os.path.join(download_sub_folder, filename)
    readme_size = ftp.size(readme_path)
    readme_progress = utils.create_standard_progressbar(readme_size)
    with open(readme_download_path,'wb') as f:
        callback = utils.create_progressbar_callback_func(readme_progress,f)
        ftp.retrbinary(f"RETR {readme_path}",callback)
        readme_progress.finish()

def download_gbk(ftp,specie,download_sub_folder,filename='protein.gbk.gz'):
    print(f'downloading protein.gbk.gz of {specie}...')
    ftp.sendcmd('TYPE i')
    gbk_path = conf.get_protein_path(specie)
    gbk_download_path = os.path.join(download_sub_folder, filename)
    gbk_size = ftp.size(gbk_path)
    gbk_progress = utils.create_standard_progressbar(end=gbk_size)
    with open(gbk_download_path,'wb') as f:
        callback = utils.create_progressbar_callback_func(gbk_progress,f)
        ftp.retrbinary(f"RETR {gbk_path}",callback)
        gbk_progress.finish()
    # decompress the gbk
    print("decompress the file")
    utils.uncompress_file(gbk_download_path,gbk_download_path[:-3])
    print()


def download_species_from_ncbi(species_list,download_folder):
    # connect to ftp server
    ftp = utils.create_ftp_connection(conf.NCBI_FTP_ADDRESS)
    for specie in species_list:
        download_specie_from_ncbi(download_folder, specie, ftp)

def download_specie_from_ncbi(download_folder, specie, ftp = None):
    if not ftp:
        ftp = utils.create_ftp_connection(conf.NCBI_FTP_ADDRESS)
    print(f"Downloading {specie} files...")
    # create directories
    download_sub_folder = os.path.join(download_folder, specie)
    os.makedirs(download_sub_folder,exist_ok=True)
    # readme file download
    download_readme(ftp,specie,download_sub_folder)
    download_gbk(ftp,specie,download_sub_folder)
    print(f'{specie} files downloaded.')


def downloader(download_all = False):
    '''
    Download species into 'data' folder
    '''
    species_list = []
    if download_all:
        species_list = conf.SPECIES
    else:
        for name,formal_name in conf.SPECIES_DICT.items():
            if utils.yes_no_question(f"Download {formal_name} ({name})?",default=True):
                species_list.append(formal_name)
    download_species_from_ncbi(species_list,'data')


if __name__ == "__main__":
    downloader()
