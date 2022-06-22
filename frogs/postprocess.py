#!/usr/bin/env python
# Copyright 2022 Paola Petrelli 
# author: Paola Petrelli <paola.petrelli@utas.edu.au>
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

import pandas

# Read current csv and fixed variables catalogue
df = pandas.read_csv("catalogue.csv.xz")

# Extract date_range base don dset 
# reanalysis have date range at end of file
# all other have only year at end of file
# except COSCH and ARC2 that have <year>.IDD.nc
reanalysis = ['CFSR','JRA-55','ERA5','ERAi','MERRA1','MERRA2']
df['bits'] = df['else'].str.split(".")
df['year'] = df.bits.map(lambda x: x[-1] if x[-1] != '1DD' else x[-2])
df['date_range'] = df.year.where(df.dset.isin(reanalysis),
                   df.year.map(lambda x: x + "0101-" + x + "1231"))

# add variable and frequency columns
df['variable'] = 'rain'
df['frequency'] = 'day'

# remove extra columns
df = df.drop('else', axis=1)
df = df.drop('bits', axis=1)
df = df.drop('year', axis=1)

# Save updated catalogue.csv.xz
df.to_csv('catalogue.csv.xz', index=False)
