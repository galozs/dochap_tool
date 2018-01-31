import sys
import os
# add to path if need to
import_path = '/'.join(__file__.split('/')[:-1])
import_path = os.path.normpath(os.path.join(import_path,'../'))
if import_path not in sys.path:
    sys.path.append(os.path.join(import_path))
from dochap_tool.common_utils import utils
from dochap_tool.compare_utils import compare_exons


def parse_gtf_file(file_path):
    """
    @description Parse gtf file into transcripts dict by transcript id of exons
    @param file_path (string)
    @return (dict) of the form {'id': [exons]}
    """
    with open(file_path) as f:
        lines = f.readlines()    # dictionary of exons by transcript_id
    return parse_gtf_data(lines)


def parse_gtf_data(lines):
    """
    @description Parse gtf data into transcripts dcit by transcript id of exons
    @param lines (string[])
    @return (dict) of the form {'id': [exons]}
    """
    transcripts = {}
    relative_end = 0
    last_transcript_id = None
    exons = []
    for line in lines:
        splitted = line.split("\t")
        # check if feature is exon
        if splitted[2] == 'exon':
            exon = {}
            exon['chr'] = splitted[0]
            exon_data = splitted[8].split('"')
            exon['gene_symbol'] = exon_data[1]
            exon['transcript_id'] = exon_data[3]
            # placeholder value incase no fpkm value
            exon['fpkm'] = -1
            for index, remain in enumerate(exon_data):
                if 'fpkm' in remain.lower() and (index+1) < len(exon_data):
                    exon['fpkm'] = float(exon_data[index+1])
            exon['real_start'] = int(splitted[3])
            exon['real_end'] = int(splitted[4])
            exon['strand'] = splitted[6]
            exon['index'] = int(splitted[8].split('"')[5]) - 1
            # half open - means we add 1 to the length
            exon['length'] = abs(exon['real_end'] - exon['real_start']) + 1
            # TODO add fpkm/rpkm/tpm
            # increment relative start location
            if last_transcript_id == exon['transcript_id']:
                relative_start = relative_end + 1
            # reset relative start location
            else:
                if exon['transcript_id'] in transcripts:
                    # if the gtf file is not built correctly,
                    # try to group exons from the same transcript together
                    exons = transcripts[exon['transcript_id']]
                    relative_start = exons[-1]['relative_start']
                else:
                    exons = []
                    relative_start = 1
            relative_end = relative_start + exon['length']
            exon['relative_start'] = relative_start
            exon['relative_end'] = relative_end
            last_transcript_id = exon['transcript_id']
            exons.append(exon)
            transcripts[exon['transcript_id']] = exons
    return transcripts


def get_gene_symbol_of_transcript_id(transcripts_dict, transcript_id):
    """
    @description get the gene_symbol of a given transcript_id from the user gtf data
    @param transcripts_dict (dict)
    @param transcript_id (string)
    @return (None|string)
    """
    if transcript_id in transcripts_dict:
        t_list = transcripts_dict[transcript_id]
        if len(t_list) > 0:
            return t_list[0]['gene_symbol'].lower()
    return None


def get_transcripts_like_id(transcripts_dict, transcript_id):
    """
    @description get all transcripts that have the same gene symbol as the given transcriptid
    @param transcripts_dict (dict)
    @param transcript_id (string)
    @return (dict)
    """
    symbol = get_gene_symbol_of_transcript_id(transcripts_dict, transcript_id)
    if not symbol:
        return None

    def query_function(transcript_list, symbol):
        if len(transcript_list) > 0:
            return transcript_list[0]['gene_symbol'].lower() == symbol

    transcripts_by_gene = {
            t_id: t_list for
            t_id, t_list in transcripts_dict.items() if
            query_function(t_list, symbol)
    }
    return transcripts_by_gene


def get_transcripts_like_ids(transcripts_dict, transcript_id_list):
    """
    @description get all transcripts that have the same gene symbol as atleast one of the given transcript_ids in the list
    @param transcripts_dict (dict)
    @param transcript_id (list of string)
    @return (dict)
    """
    def wrapper(t_id):
        return get_gene_symbol_of_transcript_id(transcripts_dict, t_id)

    unique_symbols = list(set(map(wrapper, transcript_id_list)))
    if not unique_symbols:
        return None

    def query_function(transcript_list, symbols):
        if len(transcript_list) > 0:
            return transcript_list[0]['gene_symbol'].lower() in symbols or transcript_list[0]['transcript_id'].lower() in symbols

    transcripts_by_gene = {
            t_id: t_list for
            t_id, t_list in transcripts_dict.items() if
            query_function(t_list, unique_symbols)
    }
    return transcripts_by_gene


def get_transcripts_by_gene_symbol(root_dir, specie, transcripts_dict, gene_symbol):
    """
    @description Get transcripts of the given gene symbol
    @param root_dir (string)
    @param specie (string)
    @param transcripts_dict (dict of list)
    @param gene_symbol (string)
    @return (dict) of the form {transcript_id : [exons]}
    """
    conn = utils.get_connection_object(root_dir, specie)
    with conn:
        aliases = compare_exons.get_gene_aliases_of_gene_symbol(conn, gene_symbol)
    if aliases:
        aliases = list(map(str.lower, aliases))
    else:
        aliases = [gene_symbol.lower()]

    def query_function(transcript_list, aliases):
        if len(transcript_list) > 0:
            return transcript_list[0]['gene_symbol'].lower() in aliases or transcript_list[0]['transcript_id'].lower() in aliases

    transcripts_by_gene = {
            t_id: t_list for
            t_id, t_list in transcripts_dict.items() if
            query_function(t_list, aliases)
    }
    return transcripts_by_gene


def get_all_genes_symbols(transcripts_dict):
    """Get a list of all the unique gene symbols

    :param transcripts_dict
    :type transcripts_dict: dict
    :return list
    """
    genes = {
            t_list[0]['gene_symbol'].lower()
            for t_list in transcripts_dict.values()
    }
    genes = list(genes)
    return genes


def get_all_transcript_ids(transcripts_dict: dict) -> list:
    """Get a list of all the unique transcripts ids

    :param transcripts_dict
    :type transcripts_dict: dict
    :rtype list
    """
    ids = list(set(transcripts_dict.keys()))
    return ids


def get_dictionary_of_ids_and_genes(transcripts_dict: dict, genes: list=None):
    """Get a dictionary of {genes:[t_id1,t_id2,...]}

    :param transcripts_dict
    :type transcripts_dict: dict
    :param genes: None
    :type genes: list
    :return (dict) of the form {symbol: [t_id]}
    """
    if genes is None:
        final_dict = {}
        for t_id ,t_list in transcripts_dict.items():
            if not len(t_list) > 0:
                continue
            symbol = t_list[0]['gene_symbol']
            if symbol in final_dict:
                final_dict[symbol].append(t_id)
            else:
                final_dict[symbol] = [t_id]
        return final_dict
    else:
        final_dict = {}
        for t_id ,t_list in transcripts_dict.items():
            if not len(t_list) > 0:
                continue
            symbol = t_list[0]['gene_symbol']
            if symbol in final_dict:
                final_dict[symbol].append(t_id)
            else:
                if symbol in genes:
                    final_dict[symbol] = [t_id]
        return final_dict


def get_dictionary_of_exons_and_genes(transcripts_dict):
    """
    @description Get a dictionary of {genes:[{t_id1:t_list1}]}
    @param transcripts_dict (dict)
    @return (dict) of the form {symbol : [{t_id:t_list}]
    """
    final_dict = {}
    for t_id ,t_list in transcripts_dict.items():
        if not len(t_list) > 0:
            continue
        symbol = t_list[0]['gene_symbol']
        if symbol in final_dict:
            final_dict[symbol].append({t_id:t_list})
        else:
            final_dict[symbol] = [{t_id:t_list}]
    return final_dict


def parser():
    print('Read the file documentation to know how to work with it.')
    return


if __name__ == '__main__':
    parser()
