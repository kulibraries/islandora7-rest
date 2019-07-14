# solr-generator-sample.py
# Islandora-py Samples
# Copyright (c) 2019 The University of Kansas
#
# This sample demonstrates how to use islandora7_rest for querying the Islandora Solr
# interface using the islandora7_rest.solr_generator() method.
#
# Usage:
# python solr-generator-sample.py <solr-query> [--d]
#   Options:
#       solr-query: TEXT to use for solr query. Default is *:*
#       --d:        Issue follow-up REST calls to retrieve document details

import sys
from islandora7_rest import IslandoraClient
from islandora7_rest.config import *

solr_query = "*:*"

for a in sys.argv[1:]:
    solr_query = a

ic = IslandoraClient(rest_url=ISLANDORA_REST)
ic.auth = (ISLANDORA_USER, ISLANDORA_TOKEN)

for result in ic.solr_generator(solr_query):
    print(result)
