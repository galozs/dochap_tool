from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements('./requirements.txt')
reqs = [str(ir.req) for ir in install_reqs]

setup(
   name='dochap_tool',
   version='1.0',
   description='Tool for handling genetic transcripts',
   author='Nitzan Elbaz',
   author_email='elbazni@post.bgu.ac.il',
   packages=['dochap_tool'],
   install_requires = reqs,
)
