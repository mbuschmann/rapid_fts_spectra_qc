#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script checks the files in the output folder against the files contained in the spectra folder 
and creates white- and blacklists accordingly.

@author: Matthias Buschmann
"""

import os, yaml

# load config file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

site = config['selected_site']

#ifglist = list(os.listdir(config[site]['ifgfolder']))
#ifglist.sort()
spclist = list(os.listdir(config[site]['spcfolder']))
spclist.sort()
piclist = []
piclist = [l.strip('.jpg') for l in os.listdir(config[site]['outfolder'])]
piclist.sort()

wl, bl = [], [] 
for s in spclist:
    if s in piclist:
        wl.append(s)
    else:
        bl.append(s)

with open(config['ny']['whitelist_fname'], 'w', encoding='utf8') as f:
    for s in wl:
        f.write(s+'\n')

with open(config['ny']['blacklist_fname'], 'w', encoding='utf8') as f:
    for s in bl:
        f.write(s+'\n')

print('Done.')
