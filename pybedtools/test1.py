#!/usr/bin/env python3

import pybedtools
a = pybedtools.BedTool('./CNA_region_raw_R.bed')
for row in a:
    print(row[3])
