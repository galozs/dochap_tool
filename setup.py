from setuptools import setup

with open('./requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='dochap_tool',
    version='1.0',
    description='Tool for handling genetic transcripts',
    author='Nitzan Elbaz',
    author_email='elbazni@post.bgu.ac.il',
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
    install_requires = requirements,
)
