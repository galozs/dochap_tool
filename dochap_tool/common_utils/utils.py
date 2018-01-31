import sys
import os
import ftplib
import shutil
import gzip
import sqlite3
import typing
from pygments import highlight, lexers, formatters
import json
# add to path if need to
import_path = '/'.join(__file__.split('/')[:-1])
import_path = os.path.normpath(os.path.join(import_path, '../'))
if import_path not in sys.path:
    sys.path.append(os.path.join(import_path))
# package scripts
from dochap_tool.common_utils import conf
from dochap_tool.common_utils import progressbar


def get_immediate_subdirectories(a_dir: str) -> list:
    """get_immediate_subdirectories

    :param a_dir:
    :type a_dir: str
    :rtype: list
    """
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def check_if_specie_downloaded(download_dir: str, specie: str) -> bool:
    """check_if_specie_downloaded

    :param download_dir:
    :type download_dir: str
    :param specie:
    :type specie: str
    :rtype: bool
    """
    species = get_immediate_subdirectories(download_dir)
    if specie in species:
        return True
    return False


def get_specie_db_path(root_dir: str, specie: str) -> str:
    """get_specie_db_path

    :param root_dir:
    :type root_dir: str
    :param specie:
    :type specie: str
    :rtype: str
    """
    path = os.path.join(root_dir, specie, f'{specie}.db')
    return path


def create_standard_progressbar(end: int) -> progressbar.AnimatedProgressBar:
    """create_standard_progressbar

    :param end:
    :type end: int
    :rtype: progressbar.AnimatedProgressBar
    """
    progress_bar = progressbar.AnimatedProgressBar(end=end, width=conf.PROGRESSBAR_WIDTH)
    return progress_bar


def create_progressbar_callback_func(
        progress_bar: progressbar.AnimatedProgressBar,
        file_object: typing.IO
        ) -> typing.Callable:
    """create_progressbar_callback_func

    :param progress_bar:
    :type progress_bar: progressbar.AnimatedProgressBar
    :param file_object:
    :type file_object: typing.IO
    :rtype: typing.Callable
    """
    def callback(chunk):
        file_object.write(chunk)
        progress_bar + len(chunk)
        progress_bar.show_progress()
    return callback


def drop_table(conn: sqlite3.Connection, table: str) -> None:
    """drop_table

    :param conn:
    :type conn: sqlite3.Connection
    :param table:
    :type table: str
    :rtype: None
    """
    conn.execute(conf.DROP_TABLE_TEMPLATE.format(table))


def create_ftp_connection(address: str, cert: tuple = None) -> ftplib.FTP:
    """create_ftp_connection

    :param address:
    :type address: str
    :param cert: tuple of username and password
    :type cert: tuple
    :rtype: ftplib.FTP
    """
    ftp = ftplib.FTP(address)
    if cert is not None:
        ftp.login(cert[0], cert[1])
    else:
        ftp.login()
    return ftp


def count_lines(file_object: typing.IO) -> int:
    """count_lines

    :param file_object:
    :type file_object: typing.IO
    :rtype: int
    """
    lines = 0
    buf_size = 1024 * 1024
    read_f = file_object.read  # loop optimization
    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)
    return lines


def count_lines_gzip(filename: str) -> int:
    """count_lines_gzip

    :param filename:
    :type filename: str
    :rtype: int
    """
    with gzip.open(filename) as f:
        return count_lines(f)


def uncompress_file(compressed_file: str, uncompressed_target: str) -> None:
    """uncompress_file

    :param compressed_file:
    :type compressed_file: str
    :param uncompressed_target:
    :type uncompressed_target: str
    :rtype: None
    """
    with gzip.open(compressed_file, 'rb') as f_in, open(uncompressed_target, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def yes_no_question(question: str, default: bool = True):
    """yes_no_question

    :param question:
    :type question: str
    :param default:
    :type default: bool
    """
    if default:
        yes_no_string = '(Y/n)'
    else:
        yes_no_string = '(y/N)'
    final_string = f'{question} {yes_no_string}:'
    user_input = input(final_string)
    if user_input in ['y', 'Y']:
        return True
    if user_input in ['n', 'N']:
        return False
    if user_input == '':
        return default
    return yes_no_question(question, default)


def get_connection_object(root_dir: str, specie: str) -> sqlite3.Connection:
    """get_connection_object

    :param root_dir:
    :type root_dir: str
    :param specie:
    :type specie: str
    :rtype: sqlite3.Connection
    """
    path = get_specie_db_path(root_dir, specie)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def clamp_value(value, min_value, max_value):
    """
    clamp value between min and max
    return value from 0 to 1
    """
    used_value = min(value, max_value)
    used_value = max(used_value, min_value)
    return (used_value - min_value) / (max_value - min_value)


def format_and_color(param: any) -> str:
    """format_and_color
    return a colorful string properly indented of the object as json

    :param param:
    :type param: any
    :rtype: str
    """
    formatted_json = json.dumps(param, indent=4)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    return colorful_json


def get_exon_cds_intersection(exon: dict) -> typing.Union[None, tuple]:
    """get_exon_cds_intersection

    :param exon:
    :type exon: dict
    :rtype: tuple
    """
    if 'cds_start' in exon and 'cds_end' in exon:
        cds_start = exon['cds_start']
        cds_end = exon['cds_end']
        real_start = exon['real_start']
        real_end = exon['real_end']
        if real_start > cds_end or real_end < cds_start:
            # no intersection
            return None
        else:
            # intersection
            intersection_start = max(real_start, cds_start)
            intersection_end = min(real_end, cds_end)
            return intersection_start, intersection_end
    else:
        return None


def get_partial_dictionary(old_dict: dict, keys: list, default_value: any=None) -> dict:
    """Extracts a part of a given dictionary with a list of keys.

    extract keys and values from a given dictionary, if the dictionary doesn't contain a key,
    the value will be default_value (defaults to None)
    :param old_dict:
    :type old_dict: dict
    :param keys:
    :type keys: list
    :param default_value: None
    :type: default_value: any
    :return: dict
    """
    new_dict = {}
    for key in keys:
        new_dict[key] = old_dict.get(key, default_value)
    return new_dict
