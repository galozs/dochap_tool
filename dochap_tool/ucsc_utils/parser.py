import os
from dochap_tool.common_utils import utils

def parse_known_gene_to_dict(root_dir,specie):
    path = f'{root_dir}/{specie}/knownGene.txt'
    if not os.path.isfile(path):
        print(f'{specie} knownGene not downloaded')
        return
    with open(path,'r') as f:
        lines = f.readlines()
        names = {}
        for line in lines:
            line = line.replace('\n','').replace('\\n','')
            splitted_line = line.split('\\t')
            if len(splitted_line) <2:
                splitted_line = line.split('\t')
            data = {}
            data['name'] = splitted_line[0]
            data['chrom'] = splitted_line[1]
            data['strand'] = splitted_line[2]
            data['tx_start'] = splitted_line[3]
            data['tx_end'] = splitted_line[4]
            # user gtf are half-open - which means that the start of the exon is included,
            # so exon from 2 - 4 is of lenght 3, and not 2.
            data['cds_start'] = offset_starts(splitted_line[5])
            data['cds_end'] = splitted_line[6]
            data['exon_count'] = splitted_line[7]
            data['exon_starts'] = offset_starts(splitted_line[8])
            data['exon_ends'] = splitted_line[9]
            data['protein_id'] = splitted_line[10]
            data['align_id'] = splitted_line[11]
            names[data['name']] = data
        return names

def offset_starts(values_string):
    """
    Offset given positions by +1
    @param values_string {str} values seperated by commas
    @return {str} values offset by +1 seperated by commas
    """
    return ','.join([str(int(x)+1) for x in values_string.split(',') if x])


def parse_kg_alias(root_dir,specie):
    path = f'{root_dir}/{specie}/kgAlias.txt'
    if not os.path.isfile(path):
        print("{specie} have no kgAlias file!")
        return None
    with open(path,'r') as f:
        lines = f.readlines()
    alias_dict = {}
    for line in lines:
        values =line.replace('\n','').replace('\\n','').split('\t')
        if values[0] in alias_dict:
            alias_dict[values[0]].append(values[1])
        else:
            alias_dict[values[0]] = [values[1]]
    return alias_dict




def parser():
    return

if __name__ == '__main__':
    parser()

