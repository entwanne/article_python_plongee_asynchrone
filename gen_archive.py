#!/usr/bin/env python

import json
import sys
import os.path
import re
from collections import OrderedDict
from zipfile import ZipFile

archive_name = sys.argv[1]
sections = sys.argv[2:]

manifest = {
    'introduction': sections.pop(0),
    'conclusion': sections.pop(-1),
    'object': 'container',
    'slug': 'plongee-au-coeur-de-lasynchrone-en-python',
    'title': "Plongée au cœur de l'asynchrone en Python",
    'version': 2.1,
    'description': 'Sans boire la tasse',
    'type': 'ARTICLE',
    'licence': 'CC BY-SA',
    'ready_to_publish': True,
    'children': [],
}

trans = str.maketrans('','','#*_`\n')

def reduce_title_level(line):
    if line.startswith('##'):
        return line[1:]
    return line

with ZipFile(archive_name, 'w') as archive:
    for section in (manifest['introduction'], manifest['conclusion']):
        with open(section, 'r') as f:
            next(f)
            archive.writestr(section, f.read())

    for section in sections:
        *_, sec_name = section.split('/')
        sec_name, _ = os.path.splitext(sec_name)
        with open(section, 'r') as f:
            title = next(f).translate(trans).strip()
            content = ''.join(reduce_title_level(line) for line in f)
            archive.writestr(section, content)
        manifest['children'].append({'object': 'extract', 'slug': sec_name, 'title': title, 'text': section})

    archive.writestr('manifest.json', json.dumps(manifest, indent=4))
