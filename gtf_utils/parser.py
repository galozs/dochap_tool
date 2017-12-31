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
            exon['gene_id'] = splitted[8].split('"')[1]
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
                exons = []
                relative_start = 1
            relative_end = relative_start + exon['length']
            exon['relative_start'] = relative_start
            exon['relative_end'] = relative_end
            last_transcript_id = exon['transcript_id']
            exons.append(exon)
            transcripts[exon['transcript_id']] = {'exons': exons}
    return transcripts


def parser():
    return


if __name__ == '__main__':
    parser()
