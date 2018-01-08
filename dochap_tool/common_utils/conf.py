PROT_PATH_TEMPLATE = 'genomes/{}/protein/protein.gbk.gz'
README_PATH_TEMPLATE = 'genomes/{}/README_CURRENT_RELEASE'
UCSC_TEMPLATE = 'goldenPath/{}/database/{}'
NCBI_FTP_ADDRESS = 'ftp.ncbi.nlm.nih.gov'
UCSC_FTP_ADDRESS = 'hgdownload.soe.ucsc.edu'

SPECIES = ['Mus_musculus','Homo_sapiens']

SPECIES_DICT = {
        'mouse':'Mus_musculus',
        'human':'Homo_sapiens',
}
UCSC_DICT = {
        'human':'hg38',
        'Homo_sapiens':'hg38',
        'mouse':'mm10',
        'Mus_musculus':'mm10',
}
PROGRESSBAR_WIDTH = 10

DROP_TABLE_TEMPLATE = "drop table if exists {}"
def get_protein_path(specie):
    '''
    @param specie (string) - specie name
    '''
    return PROT_PATH_TEMPLATE.format(specie)
def get_readme_path(specie):
    '''
    @param specie (string) - specie name
    '''
    return README_PATH_TEMPLATE.format(specie)
def get_ucsc_file_path(specie,filename):
    '''
    @param specie (string) - specie name
    @param filename (string) - name of file
    '''
    version_prefix = UCSC_DICT[specie]
    return UCSC_TEMPLATE.format(version_prefix,filename)




