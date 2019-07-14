# delete-object-sample.py
# islandora7_rest examples
# Copyright (c) 2019 The University of Kansas

import islandora7_rest
import islandora7_rest.config as config
import sys

ic = islandora7_rest.IslandoraClient(config.ISLANDORA_REST)
ic.auth = (config.ISLANDORA_USER, config.ISLANDORA_TOKEN)

if len(sys.argv) > 1:
    pid = sys.argv[1]
    try:
        ic.delete_object(pid)
        print("Object {pid} Deleted".format(pid=pid))
    except:
        pass
else:
    print("ERROR: No PID specified.")
    print("Usage: python demos/delete-object-sample.py <PID>")
