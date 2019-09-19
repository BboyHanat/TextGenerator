import os
from ruamel import yaml

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')

with open(os.path.join(basedir, "config.yml"), 'r') as f:
    conf = yaml.load(f.read(), Loader=yaml.Loader)
