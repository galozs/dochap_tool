import sys
import os
# add to path if need to
import_path = '/'.join(__file__.split('/')[:-1])
import_path = os.path.normpath(os.path.join(import_path, '../'))
if import_path not in sys.path:
    sys.path.append(os.path.join(import_path))
# package scripts
from dochap_tool.common_utils import conf
from dochap_tool.common_utils import utils


def download_specie_file(ftp, specie, download_sub_folder, filename):
    print(f'downloading {filename} of {specie}...')
    ftp.sendcmd('TYPE i')
    file_path = conf.get_ucsc_file_path(specie, filename)
    file_save_path= os.path.join(download_sub_folder, filename)
    file_size= ftp.size(file_path)
    file_progress = utils.create_standard_progressbar(end=file_size)
    with open(file_save_path,'wb') as f:
        callback = utils.create_progressbar_callback_func(file_progress,f)
        ftp.retrbinary(f"RETR {file_path}",callback)
        file_progress.finish()
    print("decompress the file")
    utils.uncompress_file(file_save_path,file_save_path[:-3])


def download_from_ucsc(species_list,download_folder):
    # connect to ftp server
    ftp = utils.create_ftp_connection(conf.UCSC_FTP_ADDRESS,("anonymous","me@bgu.ac.il"))
    for specie in species_list:
        download_specie_from_ucsc(specie,download_folder)


def download_specie_from_ucsc(download_folder,specie,ftp = None):
    if not ftp:
        ftp = utils.create_ftp_connection(conf.UCSC_FTP_ADDRESS,("anonymous","me@bgu.ac.il"))
    print(f"Downloading {specie} files...")
    # create directories
    download_sub_folder = os.path.join(download_folder,specie)
    os.makedirs(download_sub_folder,exist_ok=True)
    # readme file download
    download_specie_file(ftp,specie,download_sub_folder,'kgAlias.txt.gz')
    download_specie_file(ftp,specie,download_sub_folder,'knownGene.txt.gz')
    print(f'{specie} files downloaded.')



def downloader(download_all=False):
    species_list =[]
    if download_all:
        species_list = conf.SPECIES
    else:
        for name,formal_name in conf.SPECIES_DICT.items():
            if utils.yes_no_question(f"Download {formal_name} ({name})?",default=True):
                species_list.append(formal_name)
    download_from_ucsc(species_list,'data')
    return

if __name__ == '__main__':
    downloader()
