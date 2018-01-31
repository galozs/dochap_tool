import sys
import sqlite3 as lite
import re
import typing
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
    strand = transcript_data['strand']
    for index in range(int(transcript_data['exon_count'])):
        start = int(starts[index])
        end = int(ends[index])
        # we use half-open representation of start-end, which means we must add 1 to the length.
        length = abs(start-end) + 1
        exons.append({
            'index':index,
            'strand': strand,
            'length':length,
            'cds_start':cds_start,
            'cds_end': cds_end,
            'real_start':start,
            'real_end':end
        })
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
    """
    @description Extract information from the domain string using regex.
    @param domains_string (string)
    @param dom_type (string) - type of domain (region,site)
    @return (list of dict)
    """
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


def compare_user_db_transcripts(user_transcripts: dict, db_transcripts: dict) -> dict:
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
    If exons match in position and count, return True, otherwise return False

    :param user_exons:
    :type user_exons: list
    :param db_exons:
    :type db_exons: list
    :rtype: bool
    """
    if len(user_exons) != len(db_exons):
        return False

    for i in range(len(user_exons)):
        starts_match = user_exons[i]['real_start'] == db_exons[i]['real_start'] 
        ends_match =  user_exons[i]['real_end'] == db_exons[i]['real_end'] 
        if not (starts_match and ends_match):
            return False
    return True


def score_matches(user_transcript: list, other_transcripts: dict) -> dict:
    """Get dictionary of match scores of given user transcript and other transcripts to compare to.

    :param user_transcript:
    :type user_transcript: list
    :param other_transcripts:
    :type other_transcripts: dict
    :return: dict
    """
    matches = {}
    for key, other_transcript in other_transcripts.items():
        matches[key] = score_transcripts(user_transcript, other_transcript)
    return matches


def get_best_match(user_transcript: list, other_transcripts: dict) -> list:
    """Returns the best match for a given transcript from other transcripts.

    Note: Could be multiple results
    :param user_transcript:
    :type user_transcript: list
    :param other_transcripts:
    :type other_transcripts: dict
    :return: list
    """
    matches_scores = score_matches(user_transcript, other_transcripts)
    highest_score = max(matches_scores.values())
    result = [key for key in matches_scores if matches_scores[key] == highest_score]
    return result


def score_transcripts(user_transcript: list, other_transcript: list) -> float:
    """Score transcripts based on exons values

    The score moves between 0 and 1
    The score is 1 when they match perfectly, and 0 when they do not match at all.


    :param user_transcript:
    :type user_transcript: list
    :param other_transcript:
    :type other_transcript: list
    :return: float
    """
    matches = 0
    for user_exon in user_transcript:
        for db_exon in other_transcript:
            if user_exon['real_start'] == db_exon['real_start'] and user_exon['real_end'] == db_exon['real_end']:
                matches += 1
    score = matches / len(user_transcript)
    return score


def get_intersections_result(db_transcript: list, user_transcript: list, domains_variations: list) -> list:
    """Get intersections result between user transcript and domains variations.

    The intersection is in comparison to relevant database transcript, across all domains variation of the given gene.
    :param db_transcript:
    :type db_transcript: list
    :param user_transcript:
    :type user_transcript: list
    :param domains_variations:
    :type domains_variations: list
    :return: list
    """
    cds_start, cds_end = extract_cds_info(db_transcript)
    db_exons_in_cds = get_exons_in_cds(db_transcript, cds_start, cds_end)
    user_exons_in_cds = get_exons_in_cds(user_transcript, cds_start, cds_end)
    detect_frame_shift(db_exons_in_cds, user_exons_in_cds)
    set_relative_positions(db_exons_in_cds)
    set_relative_positions(user_exons_in_cds)
    detect_frame_shift(db_exons_in_cds, user_exons_in_cds)
    set_domains_exons_intersections(db_exons_in_cds, domains_variations)
    detect_junction_defects(db_exons_in_cds, user_exons_in_cds)
    result = extract_intersections_result(user_exons_in_cds)
    return result


def extract_intersections_result(user_exons_in_cds: list, wanted_keys: list=None) -> list:
    """Extracts the intersection result from each exon.

    :param user_exons_in_cds:
    :type user_exons_in_cds: list
    :param wanted_keys: None - values to extract. list of strings (defaults to None and given defaults keys)
    :type  wanted_keys: list
    :return: list
    """
    result = []
    if wanted_keys is None:
        wanted_keys = ['index', 'relative_start', 'relative_end', 'frame_shift', 'junction_defects']
    for exon in user_exons_in_cds:
        data = utils.get_partial_dictionary(exon, wanted_keys)
        result.append(data)
    return result


def extract_cds_info(db_transcript: list) -> typing.Union[tuple, None]:
    """Get cds info from database transcript

    :param db_transcript:
    :type db_transcript: list
    :return: typing.Union[tuple, None]
    """
    if len(db_transcript) == 0:
        return None
    cds_start = db_transcript[0]['cds_start']
    cds_end = db_transcript[0]['cds_end']
    return cds_start, cds_end


def get_exons_in_cds(transcript: list, cds_start: int, cds_end: int) -> list:
    """Get exons in cds of a given transcript

    :param transcript:
    :type transcript: dict
    :param cds_start:
    :type cds_start: int
    :param cds_end:
    :type cds_end: int
    :return: list
    """
    exons_in_cds = []
    for exon in transcript:
        if exon['real_end'] <= cds_start:
            continue
        if exon['real_start']>= cds_end:
            continue
        exon['in_cds_start'] = max(cds_start, exon['real_start'])
        exon['in_cds_end'] = min(cds_end, exon['real_end'])
        # add +1 to length because positions are stored as half-open
        exon['in_cds_length'] = exon['in_cds_end'] - exon['in_cds_start'] + 1
        exons_in_cds.append(exon)
    return exons_in_cds


def detect_frame_shift(db_transcript: list, user_transcript: list) -> None:
    """Detect frame shift occurances in user transcript

    :param db_transcript:
    :type db_transcript: list
    :param user_transcript:
    :type user_transcript: list
    :return: None
    """
    combine_list = zip(db_transcript, user_transcript)
    current_shift = 0
    for db_exon, user_exon in combine_list:
        start_offset = db_exon['in_cds_start'] - user_exon['in_cds_start']
        end_offset = db_exon['in_cds_end'] - user_exon['in_cds_end']
        current_shift = (start_offset + end_offset + current_shift) % 3
        user_exon['frame_shift'] = current_shift


def set_relative_positions(exons_in_cds: list) -> None:
    """Set relative positions for exons in cds

    :param exons_in_cds:
    :type exons_in_cds: list
    :return: None
    """
    last_exon_end = 0
    for exon in exons_in_cds:
        exon['relative_start'] = last_exon_end + 1
        exon['relative_end'] = exon['relative_start'] + exon['in_cds_length']
        last_exon_end = exon['relative_end']


def set_domains_exons_intersections(exons_in_cds: list, domains_variations: list) -> None:
    """Find for each exon what domains it intersects with

    :param exons_in_cds:
    :type exons_in_cds: list
    :param domains_variations: list of domains variations
    :type domains_variations: list
    :return: None
    """
    for exon in exons_in_cds:
        exon['overlap_domains'] = []
        for variation in domains_variations:
            overlaps = []
            for domain in variation:
                if exon['relative_start'] >= domain['end']:
                    # no overlap
                    continue
                if exon['relative_end'] <= domain['start']:
                    # no overlap
                    continue
                overlaps.append(domain)
            exon['overlap_domains'].append(overlaps)


def detect_junction_defects(db_transcript: list, user_transcript: list) -> None:
    """Find possible junctions defects in every exon/domain intersection

    :param db_transcript:
    :type db_transcript: list
    :param user_transcript:
    :type user_transcript: list
    :return: None
    """
    for db_exon, user_exon in zip(db_transcript, user_transcript):
        if user_exon['frame_shift'] == 0:
            user_exon['junction_defects'] = 'No possible junction defects'
        else:
            user_exon['junction_defects'] = {}
            # possible junction defect
            for index, domain_variation in enumerate(db_exon['overlap_domains']):
                defects = [domain for domain in domain_variation]
                if len(defects) == 0:
                    user_exon['junction_defects'][f'variation-{index}'] = 'No junction defects'
                else:
                    user_exon['junction_defects'][f'variation-{index}'] = defects
