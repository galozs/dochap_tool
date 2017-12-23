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
    filepath = f'{root_dir}/{specie}/protein.gbk'
    return SeqIO.parse(filepath,"genbank")

def parse_seq(index,record):
    """
    Parse a seqIO object and return tuple of data
    """
    sites=[]
    regions=[]
    cds = []
    location = ""
    name =""
    db_xref=""
    coded_by =""
    chromosome =""
    strain = ""
    for feature in record.features:
        if feature.type == 'source':
            if 'strain' in feature.qualifiers:
                strain = feature.qualifiers['strain'][0]
            if 'chromosome' in feature.qualifiers:
                chromosome = feature.qualifiers['chromosome'][0]
        if feature.type == 'CDS':
            cds.append(str(feature))
            if 'gene' in feature.qualifiers:
                name = feature.qualifiers['gene'][0]
            if 'coded_by' in feature.qualifiers:
                coded_by = feature.qualifiers['coded_by'][0]
            if 'db_xref' in feature.qualifiers:
                db_xref = feature.qualifiers['db_xref'][0]
                location = str(feature.location)
        if feature.type == 'Site':
            sites.append(feature.qualifiers['site_type'][0]+str(feature.location))
        if feature.type == 'Region':
            regions.append(feature.qualifiers['region_name'][0]+str(feature.location))
    sites_comb = ','.join(sites)
    region_comb = ','.join(regions)
    cds_comb = ','.join(cds)
    if sites_comb == '' and region_comb == '' and cds_comb == '':
        return None
    return (index,name,db_xref,coded_by,chromosome,strain,cds_comb,sites_comb,region_comb)
