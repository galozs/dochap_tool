import os
import threading
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio import SeqIO
from functools import partial
from dochap_tools.common_utils import utils
from dochap_tools.common_utils import conf

def parse(root_dir,specie):
    """
    get a list of seqIO objects
    """
    print(f'parsing protein.gbk of {specie}')
    filepath = f'{root_dir}/{specie}/protein.gbk.gz'
    return SeqIO.parse(filepath,"genbank"):

