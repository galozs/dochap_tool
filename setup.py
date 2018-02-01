from setuptools import setup

import sys
if sys.version_info < (3,6):
    sys.exit('Sorry, Python < 3.6 is not supported')

setup(
    name='dochap_tool',
    version='1.2.0',
    description='Tool for handling genetic transcripts',
    author='Nitzan Elbaz',
    author_email='elbazni@post.bgu.ac.il',
    url	= 'https://github.com/nitzanel/dochap_tool',
    packages=[
        'dochap_tool',
        'dochap_tool.common_utils',
        'dochap_tool.ncbi_utils',
        'dochap_tool.ucsc_utils',
        'dochap_tool.db_utils',
        'dochap_tool.gtf_utils',
        'dochap_tool.draw_utils',
        'dochap_tool.compare_utils',
    ],
    install_requires = [
        'biopython',
        'svgwrite',
    ],
)
