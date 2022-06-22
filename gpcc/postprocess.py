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

# Fix date_range based on frequency
# if monthly: 1941_1950_10
# if daily: 10_1941
df['year'] = df['date_range'].str.split("_")
df['date_range'] = df['date_range'].where(df['frequency'] == 'daily',
                   df['year'].map(lambda x: x[0] + "0101-" + x[1] + "1231"))
                   #df['year'].map(lambda x: x))
df['date_range'] = df['date_range'].where(df['frequency'] == 'monthly',
                   df['year'].map(lambda x: x[1] + "0101-" + x[1] + "1231"))

# add variable column
df['variable'] = 'precip'

# remove extra columns
df = df.drop('year', axis=1)

# Save updated catalogue.csv.xz
df.to_csv('catalogue.csv.xz', index=False)
