# create-object-sample.py
# islandora7_rest examples
# Copyright (c) 2019 The University of Kansas

import islandora7_rest
from islandora7_rest import config

ic = islandora7_rest.IslandoraClient(config.ISLANDORA_REST)
ic.auth = (config.ISLANDORA_USER, config.ISLANDORA_TOKEN)

new_object = ic.create_object(label="Sample Article 01", namespace="samples")
ic.add_content_model(new_object['pid'], 'islandora:sp_pdf')
print("NEW OBJECT: '{}'".format(new_object))

# Call create_datastream
new_datastream = ic.create_datastream(new_object['pid'], dsid='PDF',
                                      file="res/sample-article-1.pdf",
                                      label="Sample Content Datastream",
                                      state='A',
                                      mimeType='application/pdf',
                                      versionable=False)

print(new_datastream)

print(ic.get_datastream_info(new_object['pid'], 'PDF'))




