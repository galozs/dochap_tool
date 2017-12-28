import sys
sys.path.append('..')
from dochap_tools.common_utils import utils
import sqlite3 as lite
import re


expression = re.compile(r'(?<=\[)([0-9:]*)(?=\])')


def get_exons_from_transcript_id(root_dir, specie, transcript_id):
    """
    Query the database and return list of dictionaries expressing exons data
    """
    # query the knownGene table
    conn = utils.get_connection_object(root_dir,specie)
    with conn:
        conn.row_factory = lite.Row
        known_gene_transcript = get_known_gene_transcript(conn, transcript_id)
        exons = get_exons_from_transcript_dict(known_gene_transcript)
    return exons


def get_exons_from_gene_symbol(root_dir, specie, gene_symbol):
    conn = utils.get_connection_object(root_dir,specie)
    with conn:
        transcript_ids = get_transcript_ids_of_gene_symbol(conn,gene_symbol)
        exons_by_transcript_ids = {}
        for transcript_id in transcript_ids:
            exons = get_exons_from_transcript_id(root_dir,specie,transcript_id)
            exons_by_transcript_ids[transcript_id] = exons
        return exons_by_transcript_ids


def get_known_gene_transcript(conn, transcript_id):
    cursor = conn.cursor()
    query = f'SELECT * from knownGene WHERE name = ?'
    cursor.execute(query, (transcript_id, ))
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
        exons.append({'index':index,'length':length, 'real_start':start, 'real_end':end})
    set_relative_exons_position(exons)
    return exons


def set_relative_exons_position(exons, start_mod=0):
    last_end = 0
    for exon in exons:
        exon['relative_start'] = last_end + start_mod + 1
        exon['relative_end'] = exon['relative_start'] + exon['length']
        last_end = exon['relative_end']
    return exons


def get_domains_of_gene_symbol(root_dir, specie, gene_symbol):
    """
    reuturn list of lists of domains dictionaries, for every variant of the gene.
    """
    conn = utils.get_connection_object(root_dir,specie)
    with conn:
        conn.row_factory = lite.Row
        cursor = conn.cursor()
        query = "SELECT sites, regions from genbank WHERE symbol = ?"
        cursor.execute(query, (gene_symbol, ))
        results = cursor.fetchall()
        domains_variants = []
        for gene_result in results:
            domains = combine_sites_and_regions(gene_result['sites'], gene_result['regions'])
            if domains:
                domains_variants.append(domains)
    return domains_variants


def combine_sites_and_regions(sites_string, regions_string):
    """
    reuturn list of domains dictionaries
    """
    sites = extract_domains_data(sites_string, 'site')
    regions = extract_domains_data(regions_string, 'region')
    domains = sites+regions
    return domains


def extract_domains_data(domains_string, dom_type):
    domain_strings_list = re.findall(expression, domains_string)
    domains_description = domains_string.split(r'],')
    domains = []
    for index, domain_string in enumerate(domain_strings_list):
        if ':' in domain_string:
            split = domain_string.split(':')
            if len(split) != 2:
                # sanity check
                continue
            start = (int(split[0])+1) * 3 - 2
            end = (int(split[1])+1) * 3
            description = domains_description[index]+']'
            domains.append({'type':dom_type,'index':index 'start':start, 'end':end, 'description':description})
    return domains


def get_transcript_ids_of_gene_symbol(conn, gene_symbol):
    """
    Return transcript_id list of given gene name
    """
    cursor = conn.cursor()
    query = 'SELECT * from alias WHERE alias = ?'
    cursor.execute(query, (gene_symbol, ))
    results = cursor.fetchall()
    ids = [result['transcript_id'] for result in results]
    return ids


def get_gene_aliases_of_transcript_id(conn, transcript_id):
    """
    return all known aliases of a given transcript id in a list
    return None if no aliases has been found
    """
    cursor = conn.cursor()
    query = 'SELECT * from alias WHERE transcript_id = ?'
    cursor.execute(query, (transcript_id, ))
    results = cursor.fetchall()
    if results:
        aliases = [result['gene_alias'] for result in results]
        return aliases
    return None


def get_ncbi_gene_symbol_of_transcript_id(conn,transcript_id):
    aliases = get_gene_aliases_of_transcript_id(conn, transcript_id)
    if not aliases:
        return None
    for alias in aliases:
        # check if the alias in the genbank table
        # if yes, this is the ncbi symbol relating to the given transcript id
        query = 'SELECT * from genbank WHERE symbol = ?'
        cursor = conn.cursor()
        cursor.execute(query, (alias, ))
        result = cursor.fetchone()
        if result:
            return alias
    return None



def get_domains_intersections_in_exons(domains_list, exons_list):
    """
    return all the intersections between a list of domains and a list of exons.
    the intersections dictionary contains keys of exon's index (str) and value of list of intersections

    {index:intersections[]}
    """
    intersections = {}
    for exon_index, exon in enumerate(exons_list):
        intersections[str(exon_index)] = []
        for domain_index, domain in enumerate(domains_list):
            intersection = get_domain_intersection_in_exon(domain, exon)
            if intersection:
                # append the intersection
                intersection['domain_index'] = domain_index
                intersections[str(exon_index)].append(intersection)
            else:
                # no intersection, ignore.
                continue

    return intersections


def get_domain_intersection_in_exon(domain, exon):
    """
    return intesection between domain and exon, or None if no intersection exists.
    """
    intersection = {'start':None, 'end':None}
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


def compare_intersections(intersection, candidates):
    """
    sort a list of intersection candidates in comparison to given intersection
    """
    for candidate in candidates:
        score = get_intersections_score(intersection, candidate)
        candidate['score'] = score
    candidates.sort(key=lambda i:i['score'])
    return candidates


def get_intersections_score(i1, i2):
    """
    compare two intersection and return the score
    """
    if i1['domain_index'] == i2['domain_index']:
        i1_length = abs(i1['start'] - i1['end'])
        i2_length = abs(i2['start'] - i2['end'])
        score = i1_length / i2_length
        if score == 0:
            return 0.0
        if score > 1.0:
            return 1.0/score
        else:
            return score
    else:
        return 0.0
