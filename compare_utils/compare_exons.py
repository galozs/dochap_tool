import sys
sys.path.append('..')
from dochap_tools.common_utils import utils
import sqlite3 as lite
import re


expression = re.compile(r'(?<=\[)([0-9:]*)(?=\])')

def get_exons_from_transcript_id(root_dir,specie,transcript_id):
    # query the knownGene table
    with lite.connect(utils.get_specie_db_path(root_dir,specie)) as conn:
        conn.row_factory = lite.Row
        known_gene_transcript = get_known_gene_transcript(conn,transcript_id)
        exons = get_exons_from_transcript_dict(known_gene_transcript)
    return exons

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
        exon['relative_start'] = last_end + start_mod + 1
        exon['relative_end'] = exon['relative_start'] + exon['length']
        last_end = exon['relative_end']
    return exons


def get_domains_of_gene(root_dir,specie,gene_name):
    """
    reuturn list of lists of domains dictionaries, for every variant of the gene.
    """
    path = utils.get_specie_db_path(root_dir,specie)
    with lite.connect(path) as conn:
        conn.row_factory = lite.Row
        cursor = conn.cursor()
        query = "SELECT sites,regions from genbank WHERE symbol = ?"
        cursor.execute(query,(gene_name,))
        results = cursor.fetchall()
        domains_variants = []
        for gene_result in results:
            domains = combine_sites_and_regions(gene_result['sites'],gene_result['regions'])
            domains_variants.append(domains)
    return domains_variants


def combine_sites_and_regions(sites_string,regions_string):
    """
    reuturn list of domains dictionaries
    """
    sites = extract_domains_data(sites_string,'site')
    regions = extract_domains_data(regions_string,'region')
    domains = sites+regions
    return domains


def extract_domains_data(domains_string,dom_type):
    domain_strings_list = re.findall(expression,domains_string)
    domains_description = domains_string.split(r'],')
    domains = []
    for index,domain_string in enumerate(domain_strings_list):
        if ':' in domain_string:
            split = domain_string.split(':')
            if len(split) != 2:
                # sanity check
                continue
            start = (int(split[0])+1) * 3 - 2
            end = (int(split[1])+1) * 3
            description = domains_description[index]+']'
            domains.append({'type':dom_type,'start' : start,'end':end,'description':description})
    return domains


def get_transcript_id_of_gene(conn,gene_name):
    cursor = conn.cursor()
    query = 'SELECT * from alias WHERE gene_alias = ?'
    cursor.execute(query,gene_name)
    result = cursor.fetchone()
    return result['transcript_id']

def get_gene_aliases_of_transcript_id(conn,transcript_id):
    cursor = conn.cursor()
    query = 'SELECT * from alias WHERE transcript_id = ?'
    cursor.execute(query,(transcript_id,))
    result = cursor.fetchall()
    aliases = []
    for result in results:
        aliases.append(result['gene_alias'])
    return aliases

# TODO
def compare_intersections(intersection,candidates):
    for candidate in candidates:
        score = get_intersections_score(intersection,candidate)


def get_intersections_score(i1,i2):
    pass

def get_domains_intersections_in_exons(domains_list,exons_list):
    intersections = {}
    for exon_index,exon in enumerate(exons_list):
        intersections[str(exon_index)] = []
        for domain_index,domain in enumerate(domains_list):
            intersection = get_domain_location_in_exon(domain,exon)
            if intersection:
                # append the intersection
                intersection['domain_index'] = domain_index
                intersections[str(exon_index)].append(intersection)
            else:
                # no intersection, ignore.
                continue

    return intersections


def get_domain_location_in_exon(domain,exon):
    intersection = {'start':None,'end':None}
    e_start = exon['relative_start']
    e_end = exon['relative_end']
    d_start = domain['start']
    d_end = domain['end']
    if e_start <= d_start <= e_end:
        # domain starts in the exon
        intersection['start'] = d_start

    if e_start <= d_end <= e_end:
        # domain ends in the exon
        intersection['end'] = d_end

    if intersection['start'] and intersection['end']:
        return intersection
    return None






