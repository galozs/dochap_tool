import sys
import os
import sqlite3 as lite
# add to path if need to
import_path = '/'.join(__file__.split('/')[:-1])
import_path = os.path.normpath(os.path.join(import_path,'../'))
if import_path not in sys.path:
    sys.path.append(os.path.join(import_path))
from dochap_tool.ucsc_utils import parser as ucsc_parser
from dochap_tool.ncbi_utils import parser as ncbi_parser
from dochap_tool.common_utils import utils
from dochap_tool.common_utils import conf

def show_progress(index):
    sys.stdout.write('\r')
    sys.stdout.write(f'Inserted {index}')
    sys.stdout.flush()

def create_genbank_table(root_dir,specie,conn):
    # drop the table
    print("creating genbank table")
    utils.drop_table(conn,'genbank')
    conn.execute(
            "CREATE TABLE genbank(\
            Id INT, symbol TEXT collate nocase, db_xref TEXT,\
            coded_by TEXT, chromosome TEXT,strain TEXT,\
            cds TEXT, sites TEXT, regions TEXT)"
    )
    cursor = conn.cursor()
    # insert into database in an unoptimized way (execute instead of executemany)
    # because we cant know if the whole gbk sequence will fit in the machine memory.
    for index, record in enumerate(ncbi_parser.parse(root_dir,specie)):
        result = ncbi_parser.parse_seq(index,record)
        if result != None:
            cursor.execute("INSERT INTO genbank VALUES(?, ?, ?, ?, ?, ?,  ?, ?,?)",result)
            show_progress(index)
    print()
    print('genbank table created.')

def create_alias_table(root_dir,specie,conn):
    print("creating alias table")
    utils.drop_table(conn,'alias')
    conn.execute("CREATE TABLE alias(transcript_id TEXT collate nocase, alias TEXT collate nocase)")
    alias_dict = ucsc_parser.parse_kg_alias(root_dir,specie)
    values = []
    for name,aliases in alias_dict.items():
        for alias in aliases:
            values.append((name,alias))
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO alias VALUES(?,?)",values)
    print(f'alias table created.')

def create_known_gene_table(root_dir,specie,conn):
    print("creating knownGene table")
    utils.drop_table(conn,'knownGene')
    known_gene_dict= ucsc_parser.parse_known_gene_to_dict(root_dir,specie)
    conn.execute("CREATE TABLE knownGene(name TEXT collate nocase,\
                     chrom TEXT,\
                     strand TEXT,\
                     tx_start TEXT,\
                     tx_end TEXT,\
                     cds_start TEXT,\
                     cds_end TEXT,\
                     exon_count TEXT,\
                     exon_starts TEXT,\
                     exon_ends TEXT,\
                     protein_id TEXT ,\
                     align_id TEXT)"
    )
    cursor = conn.cursor()
    dicts = [known_gene_dict[gene] for gene in known_gene_dict]
    tuple_of_values = (tuple(dic.values()) for dic in dicts)
    cursor.executemany("INSERT INTO knownGene VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",tuple_of_values)
    print(f'known_gene table created.')


def create_db(root_dir: str,specie: str, tables: list = None):
    """create_db

    :param root_dir:
    :type root_dir: str
    :param specie:
    :type specie: str
    :param tables:
    :type tables: list
    """
    if tables is None:
        tables = ['known_gene', 'alias', 'genbank']
    # print(f"creating database for {specie}")
    with lite.connect(f'{root_dir}/{specie}/{specie}.db') as conn:
        if 'alias' in tables:
            create_alias_table(root_dir,specie,conn)
        if 'known_gene' in tables:
            create_known_gene_table(root_dir,specie,conn)
        if 'genbank' in tables:
            create_genbank_table(root_dir,specie,conn)
