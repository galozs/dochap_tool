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
            exon['gene_symbol'] = splitted[8].split('"')[1]
            exon['transcript_id'] = splitted[8].split('"')[3]
            exon['real_start'] = int(splitted[3])
            exon['real_end'] = int(splitted[4])
            exon['index'] = int(splitted[8].split('"')[5]) - 1
            exon['length'] = abs(exon['real_end'] - exon['real_start'])
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


def get_transcripts_by_gene_symbol(transcripts_dict, gene_symbol):
    """
    @description Get transcripts of the given gene symbol
    @param transcripts_dict (dict of list)
    @param gene_symbol (string)
    @return (dict) of the form {transcript_id : [exons]}
    """
    def query_function(transcript_list):
        if len(transcript_list) > 0:
            return transcript_list[0]['gene_symbol'].lower() == gene_symbol.lower()

    transcripts_by_gene = {
            t_id: t_list for
            t_id, t_list in transcripts_dict.items() if
            query_function(t_list)
    }
    return transcripts_by_gene


def get_all_genes_symbols(transcripts_dict):
    """
    @description Get a list of all the unique gene symbols
    @param transcripts_dict (dict of list)
    @return (string[])
    """
    genes = {
            t_list[0]['gene_symbol'].lower()
            for t_list in transcripts_dict.values()
    }
    genes = list(genes)
    return genes


def get_all_transcript_ids(transcripts_dict):
    """
    @description Get a list of all the unique transcripts ids
    @param transcripts_dict (string[])
    @retrun (string[])
    """
    ids = list(set(transcripts_dict.keys()))
    return ids


def get_dictionary_of_ids_and_genes(transcripts_dict):
    """
    @description Get a dictionary of {genes:[t_id1,t_id2,...]}
    @param transcripts_dict (dict)
    @return (dict) of the form {symbol: [t_id]}
    """
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
    print('no cli yet!')
    return


if __name__ == '__main__':
    parser()
