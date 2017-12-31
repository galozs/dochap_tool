def parse_gtf(file_path):
    """
    Parse gtf file into transcripts dict by transcript id of exons
    """
    with open(file_path) as f:
        lines = f.readlines()    # dictionary of exons by transcript_id
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
            # increment relative start location
            if last_transcript_id == exon['transcript_id']:
                relative_start = relative_end + 1
            # reset relative start location
            else:
                if exon['transcript_id'] in transcripts:
                    # if the gtf file is not built correctly,
                    # try to group exons from the same transcript together
                    print('gtf file is not grouped correctly')
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
    def query_function(transcript_list):
        if len(transcript_list) > 0:
            return transcript_list[0]['gene_symbol'].lower() == gene_symbol.lower()
    transcripts_by_gene = {
            t_id: t_list for
            t_id, t_list in transcripts_dict.items() if
            query_function(t_list)
    }
    return transcripts_by_gene


def parser():
    return


if __name__ == '__main__':
    parser()
