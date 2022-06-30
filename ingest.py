#!/usr/bin/env python3
# Copyright 2021 Scott Wales
# author: Scott Wales <scott.wales@unimelb.edu.au>
# modified by: Paola Petrelli <paola.petrelli@utas.edu.au>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This code build a catalogue.json and catalogue.csv.xz file list for each dataset
# Last modified:
#     2022/06/21 

import yaml
import subprocess
import tempfile
import re
import lzma
import csv
import shlex
import json
import jsonschema

# import dataset configuration from ingest.yaml
with open("ingest.yaml") as f:
    config = yaml.safe_load(f)

# define schema for catalogue.json file
schema = {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'title': {'type': 'string'},
        'description': {'type': 'string'},
        'find': {
            'type': 'object',
            'properties': {
                    'paths': {
                        'type': 'array',
                        'items': {'type': 'string'}
                        },
                    'options': {'type': 'string'}
                },
            'required': ['paths'],
            },
        'drs': {'type': 'string'},
        'catalogue_file': {'type': 'string'},
        'assets': {'type': 'object'},
        'aggregation_control': {'type': 'object'},
        'rename': {
            'type': 'object',
            'patternProperties': {
                    '.*': {
                        'type': 'object',
                        'patternProperties': {
                            '.*': {'type': 'string'}
                            },
                        },
                    },
            },
        'postprocess': {'type': 'object'},
        },
    'required': ['id','description','find','drs'],
}
# if catalogue.csv.xz already exists for dataset change find definition in schema
if 'catalog_file' in [k for k in config.keys()]:
    print('Existing catalogue_file for dataset')
    # Get the column names from the catalogue file
    with lzma.open(config['catalog_file'], mode='rt') as f:
        header = f.readline()
    columns = header.replace("\n","").split(",")
else:
    jsonschema.validate(config, schema)

    # compile the regex for DRS path
    drs_re = re.compile(config["drs"], re.VERBOSE)
    #print(f'drs_re: {drs_re}')

    # define find command to list all files based on options listed in dataset configuration
    find_command = [
        "/bin/find",
        *config["find"]["paths"],
        *shlex.split(config["find"].get("options", "")),
        ]
    print(shlex.join(find_command))

    # open catalogue.csv.xz file
    with tempfile.TemporaryFile('w+') as f, tempfile.TemporaryFile('w+') as s, lzma.open(
        "catalogue.csv.xz", mode="wt", newline=""
    ) as out, lzma.open('errors.xz', mode='wt') as e:

        # Find files
        print("Finding Files...")
        find = subprocess.run(find_command, stdout=f)
        find.check_returncode()
        f.seek(0)

        # Sort the results
        print("Sorting Files...")
        sort = subprocess.run(["/bin/sort"], stdin=f, stdout=s)
        sort.check_returncode()
        s.seek(0)

        # Get the column names
        columns = None
        for path in s:
            match = drs_re.match(path)
            if match is None:
                continue
            columns = list(match.groupdict().keys())
            break
        s.seek(0)

        # Write catalogue.csv.xz
        print("Writing Catalogue...")
        csv_w = csv.DictWriter(out, columns, dialect='unix')
        csv_w.writeheader()
        for path in s:
            match = drs_re.match(path)
            if match is None:
                print('ERROR',path.strip())
                e.write(path)
                continue
            record = match.groupdict()
            # rename columns if defined in config
            for col, renames in config.get('rename', {}).items():
                if record.get(col, None) in renames:
                    record[col] = renames[record[col]]

            csv_w.writerow(record)
    # Drop extra config items
    config.pop('find')
    config.pop('drs')
    config.pop('rename', None)
    config.pop('postprocess', None)

# Setup catalogue.json

config['esmcat_version'] = '0.1.0'
config['catalog_file'] = 'catalogue.csv.xz'
config['attributes'] = [{'column_name': c} for c in columns if c != config['assets']['column_name']]

# write catalogue.json file
with open('catalogue.json', 'w') as f:
    print("cat.json open")
    json.dump(config,f,indent=2)
print("")
