import sys
import sqlite3 as lite
import re
import os
# add to path if need to
import_path = '/'.join(__file__.split('/')[:-1])
import_path = os.path.normpath(os.path.join(import_path,'../'))
if import_path not in sys.path:
    sys.path.append(os.path.join(import_path))
from dochap_tool.common_utils import utils

expression = re.compile(r'(?<=\[)([0-9:]*)(?=\])')


def get_exons_from_transcript_id(root_dir, specie, transcript_id):
    """
    @description Query the database and return list of dictionaries expressing exons data
    @param root_dir (string)
    @param specie (string)
    @param transcript_id (string)
    @return (list of dict)
    """
    # query the knownGene table
    conn = utils.get_connection_object(root_dir,specie)
    with conn:
        conn.row_factory = lite.Row
        known_gene_transcript = get_known_gene_transcript(conn, transcript_id)
        exons = get_exons_from_transcript_dict(known_gene_transcript)
    return exons


def get_exons_from_gene_symbol(root_dir, specie, gene_symbol):
    '''
    @description Query the database and return dictionary of exons by id of a given gene symbol
    @param root_dir (string)
    @param specie (string)
    @param gene_symbol (string)
    @return (dict)
    '''
    conn = utils.get_connection_object(root_dir,specie)
    with conn:
        transcript_ids = get_transcript_ids_of_gene_symbol(conn,gene_symbol)
        exons_by_transcript_ids = {}
        for transcript_id in transcript_ids:
            exons = get_exons_from_transcript_id(root_dir,specie,transcript_id)
            exons_by_transcript_ids[transcript_id] = exons
        return exons_by_transcript_ids


def get_known_gene_transcript(conn, transcript_id):
    '''
    @description Query the database and get data from the known_gene table
    @param conn (sqlite3.connect)
    @param transcript_id (string)
    @return (named tuple)
    '''
    cursor = conn.cursor()
    query = f'SELECT * from knownGene WHERE name = ?'
    cursor.execute(query, (transcript_id, ))
    result = cursor.fetchone()
    return result


def get_exons_from_transcript_dict(transcript_data):
    """
    @Description Extract exons from a given transcript dictionary
    @param transcript_data (dict)
    @return (list)
    """
    exons = []
    # calculate length of each exon
    cds_start = int(transcript_data['cds_start'])
    cds_end = int(transcript_data['cds_end'])
    starts = transcript_data['exon_starts'].split(',')
    ends = transcript_data['exon_ends'].split(',')
    for index in range(int(transcript_data['exon_count'])):
        start = int(starts[index])
        end = int(ends[index])
        length = abs(start-end)
        exons.append({
            'index':index,
            'length':length,
            'cds_start':cds_start,
            'cds_end': cds_end,
            'real_start':start,
            'real_end':end
        })
    set_relative_exons_position(exons)
    return exons


def set_relative_exons_position(exons, start_mod=0):
    """
    @description Squash exons together to be concussive
    @param exons (list)
    @param start_mod (int) - - (default=0)
    @return (list)
    """
    last_end = 0
    for exon in exons:
        exon['relative_start'] = last_end + start_mod + 1
        exon['relative_end'] = exon['relative_start'] + exon['length']
        last_end = exon['relative_end']
    return exons


def get_domains_of_gene_symbol(root_dir, specie, gene_symbol):
    """
    @description reuturn list of lists of domains dictionaries, for every variant of the gene.
    @param root_dir (string)
    @param specie (string)
    @param gene_symbol (string)
    @return (list of list of dict)
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
    @description reuturn list of domains dictionaries
    @param sites_string (string)
    @param regions_string (string)
    @return (list of dict)
    """
    sites = extract_domains_data(sites_string, 'site')
    regions = extract_domains_data(regions_string, 'region')
    domains = sites+regions
    return domains


def extract_domains_data(domains_string, dom_type):
    '''
    @description Extract information from the domain string using regex.
    @param domains_string (string)
    @param dom_type (string) - type of domain (region,site)
    @return (list of dict)
    '''
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
            domains.append({'type':dom_type,'index':index, 'start':start, 'end':end, 'description':description})
    return domains


def get_transcript_ids_of_gene_symbol(conn, gene_symbol):
    """
    @description Return transcript_id list of given gene name
    @param conn (sqlite3.connect)
    @param gene_symbol (string)
    @return (list of string)
    """
    cursor = conn.cursor()
    query = 'SELECT * from alias WHERE alias = ?'
    cursor.execute(query, (gene_symbol, ))
    results = cursor.fetchall()
    ids = [result['transcript_id'] for result in results]
    return ids


def get_gene_aliases_of_gene_symbol(conn, symbol):
    """
    @description return all aliases of a given gene symbol
    @param conn {sqlite3.connect}
    @param symbol {string}
    @return {None| list of string}
    """
    cursor = conn.cursor()
    query = 'SELECT * from alias WHERE alias = ?'
    cursor.execute(query, (symbol, ))
    results = cursor.fetchall()
    if results:
        unique_aliases = set()
        unique_transcripts_ids = list({result['transcript_id'] for result in results})
        for t_id in unique_transcripts_ids:
            aliases = get_gene_aliases_of_transcript_id(conn, t_id)
            unique_aliases.update(aliases)
        return list(unique_aliases)
    return None

def get_gene_aliases_of_transcript_id(conn, transcript_id):
    """
    @description return all known aliases of a given transcript id in a list
    return None if no aliases has been found
    @param conn (sqlite3.connect)
    @param transcript_id (string)
    @return (None|list of string)
    """
    cursor = conn.cursor()
    query = 'SELECT * from alias WHERE transcript_id = ?'
    cursor.execute(query, (transcript_id, ))
    results = cursor.fetchall()
    if results:
        aliases = [result['alias'] for result in results]
        return aliases
    return None


def get_ncbi_gene_symbol_of_transcript_id(conn,transcript_id):
    """
    Get the ncbi gene symbol of the given transcript id in the given database.
    Return None if there isnt one.
    """
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

def check_if_transcript_id_in_db(conn, transcript_id):
    """Checks if a given transcript id exist in the given database"""
    aliases = get_gene_aliases_of_transcript_id(conn, transcript_id)
    if aliases:
        return True
    else:
        return False


def get_domains_intersections_in_exons(domains_list, exons_list):
    """
    return all the intersections between a list of domains and a list of exons.
    the intersections dictionary contains keys of exon's index (str) and value of list of intersections

    {index:intersections[]}
    """
    intersections = {}
    for exon_index, exon in enumerate(exons_list):
        intersections[str(exon_index)] = []
        for domain in domains_list:
            intersection = get_domain_intersection_in_exon(domain, exon)
            if intersection:
                # append the intersection
                intersection['domain'] = domain
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

    if intersection['start'] or intersection['end']:
        return intersection
    return None


def compare_user_db_transcripts(user_transcripts:dict, db_transcripts:dict) -> dict:
    """compare_user_db_transcripts
    Get dict of the form {user_t_id : matching_db_t_id}

    :param user_transcripts:
    :type user_transcripts: dict
    :param db_transcripts:
    :type db_transcripts: dict
    :rtype: dict
    """
    matching_dict = {}
    for t_id, user_exons in user_transcripts.items():
        for db_t_id, db_exons ,in db_transcripts.items():
            if compare_every_exon(user_exons, db_exons):
                matching_dict[t_id] = db_t_id
                break
    return matching_dict

def compare_every_exon(user_exons: list, db_exons: list) -> bool:
    """compare_every_exon
    If exons match in length and count, return Treu, otherwise return False

    :param user_exons:
    :type user_exons: list
    :param db_exons:
    :type db_exons: list
    :rtype: bool
    """
    if len(user_exons) != len(db_exons):
        return False

    for i in range(len(user_exons)):
        if user_exons[i]['length'] - db_exons[i]['length'] > 1:
            return False
    return True



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
    if i1['domain'] == i2['domain']:
        score = 0
        i1_length,i2_length = None,None
        if i1['start'] and i1['end']:
            i1_length = abs(i1['start'] - i1['end'])
        if i2['start'] and i2['end']:
            i2_length = abs(i2['start'] - i2['end'])
        if i1_length and i2_length:
            score = i1_length / i2_length
        if score == 0:
            return 0.0
        if score > 1.0:
            return 1.0/score
        else:
            return score
    else:
        return 0.0
