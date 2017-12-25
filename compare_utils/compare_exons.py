import sys
sys.path.append('..')
from dochap_tools.common_utils import utils
import sqlite3 as lite

def get_exons_from_transcript_id(root_dir,specie,transcript_id):
    # query the knownGene table
    with lite.connect(utils.get_specie_db_path(root_dir,specie)) as conn:
        conn.row_factory = lite.Row
        known_gene_transcript = get_known_gene_transcript(conn,transcript_id)
        exons = get_exons_from_transcript_dict(known_gene_transcript)
        print(exons)

def get_known_gene_transcript(conn,transcript_id):
    cursor = conn.cursor()
    query = f'SELECT * from knownGene WHERE name = ?'
    cursor.execute(query,(transcript_id,))
    result = cursor.fetchone()
    return result

def get_exons_from_transcript_dict(transcript_data):
    exons = []
    # calculate length of each exon
    starts = transcript_data['exon_starts'].split(',')
    ends = transcript_data['exon_ends'].split(',')
    for index in range(int(transcript_data['exon_count'])):
        start = int(starts[index])
        end = int(ends[index])
        length = abs(start-end)
        exons.append({'length':length,'real_start':start,'real_end':end})
    set_relative_exons_position(exons)
    return exons


def set_relative_exons_position(exons,start_mod=0):
    last_end = 0
    for exon in exons:
        exon['rel_start'] = last_end + start_mod + 1
        exon['rel_end'] = exon['rel_start'] + exon['length']
        last_end = exon['rel_end']
    return exons


def get_domains_of_gene(root_dir,specie,gene_name):
    path = utils.get_specie_db_path(root_dir,specie)
    with lite.connect(path) as conn:
        pass


def get_transcript_id_of_gene(conn,gene_name):
    cursor = conn.cursor()
    query = 'SELECT * from alias WHERE gene_alias = ?'
    cursor.execute(query,gene_name)
    result = cursor.fetchone()
    return result['transcript_id']

def get_gene_aliases_of_transcript_id(conn,transcript_id):
    cursor = conn.cursor()
    query = 'SELECT * from alias WHERE transcript_id = ?'
    cursor.execute(query,transcript_id)
    result = cursor.fetchall()
    aliases = []
    for result in results:
        aliases.append(result['gene_alias'])
    return aliases


