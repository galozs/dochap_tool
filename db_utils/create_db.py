import sys
sys.path.append("..")
import sqlite3 as lite
from dochap_tools.ucsc_utils import parser as ucsc_parser
from dochap_tools.ncbi_utils import parser as ncbi_parser
from dochap_tools.common_utils import utils
from dochap_tools.common_utils import conf

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
            Id INT, symbol TEXT, db_xref TEXT,\
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

def create_alias_table(root_dir,specie,conn):
    print("creating alias table")
    utils.drop_table(conn,'alias')
    conn.execute("CREATE TABLE alias(trascript_id TEXT, alias TEXT)")
    alias_dict = ucsc_parser.parse_kg_alias(root_dir,specie)
    values = []
    for name,aliases in alias_dict.items():
        for alias in aliases:
            values.append((name,alias))
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO alias VALUES(?,?)",values)

def create_known_gene_table(root_dir,specie,conn):
    print("creating knownGene table")
    utils.drop_table(conn,'knownGene')
    known_gene_dict= ucsc_parser.parse_known_gene_to_dict(root_dir,specie)
    conn.execute("CREATE TABLE knownGene(name TEXT,\
                     chrom TEXT,\
                     strand TEXT,\
                     tx_start TEXT,\
                     tx_end TEXT,\
                     cds_start TEXT,\
                     cds_end TEXT,\
                     exon_count TEXT,\
                     exon_starts TEXT,\
                     exon_ends TEXT,\
                     protein_id TEXT,\
                     align_id TEXT)"
    )
    cursor = conn.cursor()
    dicts = [known_gene_dict[gene] for gene in known_gene_dict]
    tuple_of_values = (tuple(dic.values()) for dic in dicts)
    cursor.executemany("INSERT INTO knownGene VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",tuple_of_values)


def create_db(root_dir,specie):
    # genbank table
    # alias table
    # known gene table
    print(f"creating database for {specie}")
    with lite.connect(f'{root_dir}/{specie}/{specie}.db') as conn:
        create_alias_table(root_dir,specie,conn)
        create_known_gene_table(root_dir,specie,conn)
        create_genbank_table(root_dir,specie,conn)