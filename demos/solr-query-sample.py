# solr-query-sample.py
# Islandora-py Samples
# Copyright (c) 2019 The University of Kansas
#
# This sample demonstrates how to use islandora7_rest for querying the Islandora Solr
# interface using the islandora7_rest.solr_query() method.
#
# Usage:
# python solr-query-sample.py <solr-query> [--d]
#   Options:
#       solr-query: TEXT to use for solr query. Default is *:*
#       --d:        Issue follow-up REST calls to retrieve document details

import sys
from islandora7_rest import IslandoraClient
from islandora7_rest.config import *

get_objects_flag = False
solr_query = "*:*"

for a in sys.argv[1:]:
    if a == '--d':
        get_objects_flag = True
    else:
        solr_query = a

islandora_client = IslandoraClient(ISLANDORA_REST, ISLANDORA_USER, ISLANDORA_TOKEN)

results = islandora_client.solr_query(solr_query, fl="PID")

print("solr.responseHeader.status .......... {}".format(results['responseHeader']['status']))
print("solr.responseHeader.QTime ........... {}".format(results['responseHeader']['QTime']))
print("solr.responseHeader.params .......... {}".format(results['responseHeader']['params']))
print("solr.response.numFound .............. {}".format(results['response']['numFound']))
print("solr.response.start ................. {}".format(results['response']['start']))

for d in results['response']['docs']:
    print(d)
    if get_objects_flag:
        print(islandora_client.get_object(d['PID']))

