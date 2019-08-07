## Getting started

#### On the Islandora side:

Install [DGI's Islandora REST](https://github.com/discoverygarden/islandora_rest) and, in Drupal, enable it and the "Islandora REST API Authentication" 
module that comes with it.  Set a user API token (in your user profile page).  We tend to just generate a new one on any given project and not store it long term.

### On the Python side

```bash
$ pip install islandora7-rest
```

```python
from islandora7_rest import IslandoraClient

client = IslandoraClient("https://mysite/islandora/rest",
    user="admin",
    token="auth_token")
```

* we use *token* for the keyword because [normal passwords don't work well with REST as implemented](https://github.com/discoverygarden/islandora_rest#authorization),
and our sites log in via single-sign-on anyway.

There is an optional configurator module which will look for passwords in environment variables or a .env file.

```python
from islandora7_rest import config   # sets config.ISLANDORA_REST, etc from .env or the environment
```

## Query from Solr

Most of our workflows start with a Solr query.

### solr_generator

solr_generator is an Iterator that yields items from a Solr query 
(this is memory-friendly, you may be iterating over thousands of items).

By default, only PID is retrieved.  You can pass an ```fl=``` argument with a comma-separated
list of fields. Most parameters here eventually make their way down to the Solr GET request.

Results are in a Python dictionary reflecting the Solr document

```python
for item in client.solr_generator("PID:* AND fedora_datastreams_ms:JPG", fl="PID,fgs_label_s"):
    print(item['PID'], item['fgs_label_s'])
```

### solr_query

The more low-level Solr query, useful if you want facet info or counts.
Again, most parameters here eventually make their way down to the Solr GET request.

Returns a raw Response from Requests.

```python
result = client.solr_query("*:*", rows=0)
print(result['response']['numFound'])
```

Facets are a bit harder. Because `facet.field` has a dot, and also
might be called more than once.  This example works:

```python
arguments = {
    "facet": "true",
    "facet.field": ["fedora_datastreams_ms", "RELS_EXT_hasModel_uri_ms"]
}
result = client.solr_query("*:*", rows=0, **arguments)
for dsid, count in result['facet_counts']['facet_fields']['fedora_datastreams_ms'].items():
    print(dsid, count)
```


## Objects

### get_object 

Gets object info as a Python dictionary structure.

```python
object_info = client.get_object("islandora:21")
print("Created:", object_info['created'])
for datastream in object_info['datastreams']:
    print(datastream['dsid'])
```

### create_object

Note: this gives you no CModel, no parent collection, no MODS, just
an object in space.  However, see below (under Relationship Shortcuts) for easy ways to
set those.

```python
new_object = client.create_object(namespace="islandora", label="New Islandora Object")
print(new_object['pid'])

new_object2 = client.create_object(pid="islandora:70", label="Specified PID")
```

### update_object

```python
client.update_object("islandora:21", label="New Object Label", state="Active")
```

### delete_object

```python
client.delete_object("islandora:21")
```


## Datastreams

### get_datastream

Actually retrieves the datastream.

*streaming=True* returns it in a memory friendly iterator of byte segments

```python
raw_mods = client.get_datastream('islandora:21', 'MODS')
# now you can do eTree or whatnot with the DC

file_stream = client.get_datastream('islandora:21', 'OBJ', streaming=True)
with open(output_filename, "wb") as fileHandle:
        for block in file_stream:
            fileHandle.write(block)
        fileHandle.flush() # Not always needed... but sometimes if you are doing work
                           # within the with: block... like using a tempfile.TemporaryFile.
```

### get_datastream_info

Gets the information about a datastream. Returns a Python dictionary.
```python
ds_info = client.get_datastream_info("islandora:3", "OBJ")
checksum = ds_info['checksum']
```

### create_datastream

Can create from a file name or from a string. Can set `label=`, `state=`... but
`checksumType` gets overridden if you have a repository default set.

```python
client.create_datastream("islandora:21", "MODS", string=my_mods_etree.tostring())

client.create_datastream("islandora:21", "OBJ", file="/path/to/bigFile.tif", label="bigFile TIFF")
```

### update_datastream

Basically just like the above.  Can just set a datastream's state or label, or can push in a file/string.

```python
client.update_datastream("islandora:10", "OBJ", state="Active", versionable=False)
```

### delete_datastream

```python
client.delete_datastream("islandora:21", "TN")
```

## Relationships (RELS-EXT)

### get_relationships

```
rels=client.get_relationships('islandora:21')
for rel in rels:
    print(rel['predicate']['value'], rel['object']['value'])
```

### add_relationship

Note, this is not advanced and does not check 
to prevent you from duplicating relationships.

Also, RDF 'string' [does not validate](https://github.com/fcrepo3/fcrepo/blob/9c41b09a21a3a2615791fa4c614095a14512940f/fcrepo-server/src/main/java/org/fcrepo/server/validation/RelsValidator.java#L518)
so use type='none' (lowercase string *none*) if you want a literal string. 
int/float/dateTime are useable, if not typically used.  

Basically, if you want an internal URI (rdf:resource is in info:fedora/), use `type="uri"` (which is the default).  If you are setting a literal, you 
probably want `type="none"`.  Even most of the things that *could* be an RDF typed int/float (like `islandora:isPageNumber`)
don't typically do so in Islandora and just use bare `type="none"` style literals. 

```python
client.add_relationship('islandora:10', 
                        ns="http://islandora.ca/ontology/relsext#",
                        predicate="isPageOf",
                        object="islandora:5")

client.add_relationship('islandora:3', ns="http://customschema.my.edu#",
                        predicate="localCallNumber",
                        object="ZZ9 Plural Z Alpha",
                        type="none")
```

### remove_relationship

Can be tricky. PID and Predicate required. You don't need the `ns=` (uri namespace prefix)
unless you need to disambiguate between identically-named predicates. If object is specified and is a literal,
you *need* to say `literal=True` (a Python boolean True).

```python
client.remove_relationship('islandora:2', # removes all localCallNumber RELS 
                            predicate="localCallNumber") 
client.remove_relationship('islandora:3', # removes one specifically
                            predicate="localCallNumber", 
                            object="ZZ9 Plural Z Alpha", literal=True)
```

## Relationship Shortcuts

These convenience functions wrap the basic relationship functions above for
the most common use cases.

### add_content_model

Sets a CModel. Checks and won't create duplicates. 
The `exclusive` flag will remove all other CModels in passing. 

```python
client.add_content_model("islandora:21", "islandora:sp_basic_image", exclusive=True)
```

### add_collection_membership
### remove_collection_membership

add_collection(): Checks and won't create duplicates.

```python
client.add_collection_membership("islandora:21", "islandora:fancy_collection")
client.remove_collection_membership("islandora:21", "islandora:audio_collection")
```
