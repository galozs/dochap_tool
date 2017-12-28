import sys
sys.path.append("..")
# package scripts
from dochap_tools.common_utils import conf
from dochap_tools.common_utils import progressbar
import ftplib
import os
import shutil
import gzip
import sqlite3 as lite

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir) \
        if os.path.isdir(os.path.join(a_dir, name))]

def check_if_specie_downloaded(download_dir,specie):
    species = get_immediate_subdirectories(download_dir)
    if specie in download_dir:
        return True
    return False


def get_specie_db_path(root_dir,specie):
    path = os.path.join(root_dir,specie,f'{specie}.db')
    return path

def create_standard_progressbar(end):
    progress_bar = progressbar.AnimatedProgressBar(end=end,width = conf.PROGRESSBAR_WIDTH)
    return progress_bar

def create_progressbar_callback_func(progress_bar,file_object):
    def callback(chunk):
        file_object.write(chunk)
        progress_bar + len(chunk)
        progress_bar.show_progress()
    return callback

def drop_table(conn,table):
    conn.execute(conf.DROP_TABLE_TEMPLATE.format(table))



def create_ftp_connection(address,cert=None):
    ftp = ftplib.FTP(address)
    if cert != None:
        ftp.login(cert[0],cert[1])
    else:
        ftp.login()
    return ftp

def count_lines(file_object):
    """ count lines in file """
    lines = 0
    buf_size = 1024 * 1024
    read_f = file_object.read # loop optimization
    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)
    return lines

def count_lines_gzip(filename):
    with gzip.open(filename) as f:
        return count_lines(f)


def uncompress_file(compressed_file,uncompressed_target):
    with gzip.open(compressed_file, 'rb') as f_in, open(uncompressed_target, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def yes_no_question(question,default = True):
    """
    Description:
    Ask user for yes/no input.

    Arguments:
    question to ask

    Keyword argumets:
    default behaviour

    """
    if default:
        yes_no_string = '(Y/n)'
    else:
        yes_no_string = '(y/N)'
    final_string = f'{question} {yes_no_string}:'
    user_input = input(final_string)
    if user_input in ['y','Y']:
        return True
    if user_input in ['n','N']:
        return False
    if user_input == '':
        return default
    return yes_no_question(question,default)

def get_connection_object(root_dir,specie):
    path = get_specie_db_path(root_dir,specie)
    conn = lite.connect(path)
    conn.row_factory = lite.Row
    return conn
