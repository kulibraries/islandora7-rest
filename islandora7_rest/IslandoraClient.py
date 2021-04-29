# /islandora7_rest/islandora7_rest.py
# Copyright (c) 2019 The University of Kansas
# BSD 3-Clause - see LICENSE.txt
# http://www.ku.edu
#
# Islandora REST API at-a-glance
#
# Objects:
# GET       /islandora/rest/v1/object/{pid}                         GET existing object
# POST      /islandora/rest/v1/object                               UPDATE existing object
# PUT       /islandora/rest/v1/object/{pid}                         CREATE new object
# DELETE    /islandora/rest/v1/object/{pid}                         DELETE existing obj
#
# Relationships:
# GET       /islandora/rest/v1/object/{pid}/relationship?{params}   LIST existing relationships
# POST      /islandora/rest/v1/object/{pid}/relationship            ADD a new relationship
# DELETE    /islandora/rest/v1/object/{pid}/relationship            REMOVE an existing relationship
#
# Datastreams:
# GET       /islandora/rest/v1/object/{pid}/datastream/{dsid}       GET a datastream for an object
# POST      /islandora/rest/v1/object/{pid}/datastream/             CREATE a datastream on object
# PUT       /islandora/rest/v1/object/{pid}/datastream/{dsid}       UPDATE an existing datastream
# DELETE    /islandora/rest/v1/object/{pid}/datastream/{dsid}       DELETE an existing datastream
#
# GET       /islandora/rest/v1/solr/{query}                         SEARCH for objects.
#                                                                       {query} is solr query

import json
import requests
import os

from urllib.parse import quote_plus


class IslandoraClient(requests.Session):

    def __init__(self, rest_url=None, user=None, token=None):
        """

        :param rest_url: URL to Islandora Rest, not including the v1/
        :param user: Islandora user
        :param token: Token/Password
        """
        super(IslandoraClient, self).__init__()
        self.url_base = rest_url
        if self.url_base[-1] != "/":
            self.url_base = rest_url + "/"
        if user and token:
            self.auth = (user, token)

    def request(self, method, url, **kwargs):
        modified_url = self.url_base + 'v1/' + url
        return super(IslandoraClient, self).request(method, modified_url,
                                                    **kwargs)

    # Objects:
    # GET       /islandora/rest/v1/object/{pid}    GET existing object
    # POST      /islandora/rest/v1/object          UPDATE existing object
    # PUT       /islandora/rest/v1/object/{pid}    CREATE new object
    # DELETE    /islandora/rest/v1/object/{pid}    DELETE existing obj

    def get_object(self, pid):
        url = "object/{}".format(pid)
        response = self.get(url)
        response.raise_for_status()
        return response.json()

    def update_object(self, pid, **changed_object_as_kwargs):
        """

        :param pid:
        :param changed_object_as_kwargs: arguments likely to be label, owner, or state
        :return:
        """
        url = "object/{}".format(pid)
        response = self.put(url, json=changed_object_as_kwargs)
        response.raise_for_status()
        return response.json()

    def create_object(self, **new_object_as_kwargs):
        """

        :param new_object_as_kwargs: This is a passthrough dictionary to the POST data \
            meaning, you can say pid="namespace:5", namespace="namespace", label="Label", etc
        :return:
        """
        url = "object"
        response = self.post(url, data=new_object_as_kwargs)
        response.raise_for_status()
        return response.json()

    def delete_object(self, pid):
        if not pid:
            raise Exception("Missing PID")
        url = "object/{}".format(pid)
        response = self.delete(url)
        response.raise_for_status()
        return response

    # GET       /islandora/rest/v1/solr/{query}        SEARCH for objects.
    # Raw response document as a Python dictionary structure

    def solr_query(self, query="*:*", **params):
        url = "solr/{}".format(quote_plus(query))
        response = self.get(url, params=params)
        response.raise_for_status()
        return response.json()

    # Convenient yield generator for documents from a Solr query
    # 'fl' defaults to just the PID
    # Cursor logic - if you want 'start' to work, run a solr_query()

    def solr_generator(self, query="*:*", **params):
        """

        :param query:
        :param params:
        """
        if 'start' in params.keys():
            del params['start']
        if 'rows' not in params.keys():
            params['rows'] = 100
        if 'sort' not in params.keys():
            params['sort'] = "PID asc"
        if 'fl' not in params.keys():
            params['fl'] = "PID"
        params['cursorMark'] = '*'

        while True:
            results = self.solr_query(query, **params)
            nextCursorMark = results['nextCursorMark']
            for result in results['response']['docs']:
                yield result
            # We're done here
            if nextCursorMark == params['cursorMark']:
                break
            params['cursorMark'] = nextCursorMark

    # Relationships:
    # GET       /islandora/rest/v1/object/{pid}/relationship?{params}   LIST existing relationships
    # POST      /islandora/rest/v1/object/{pid}/relationship            ADD a new relationship
    # DELETE    /islandora/rest/v1/object/{pid}/relationship            REMOVE an existing relationship

    def get_relationships(self, pid, **kwargs):
        """
        :param pid:
        :param kwargs:
          This could include fields like predicate, uri (which in my mind should be called namespace, but it's uri here),
          object, and literal... these are passed as GET params
        :return: list of dictionary objects
        """
        if not pid:
            raise Exception("Missing PID")
        response = self.get("object/{}/relationship".format(pid), params=kwargs)
        response.raise_for_status()
        return response.json()

    def add_relationship(self, pid, ns, predicate, object, type='uri'):
        if not pid:
            raise Exception("Missing PID")
        response = self.post("object/{}/relationship".format(pid), {
            "uri": ns,
            "predicate": predicate,
            "object": object,
            "type": type
        })
        response.raise_for_status()
        return response

    def remove_relationship(self, pid, predicate, object=None, ns=None, literal=False):
        if not pid:
            raise Exception("Missing PID")
        json_data = {}
        if predicate: json_data["predicate"] = predicate
        if ns: json_data["uri"] = ns
        if object: json_data["object"] = object
        # 'literal' seems happier with the 1 or 0. Okay.
        json_data["literal"] = 1 if literal else 0

        response = self.delete("object/{}/relationship".format(pid), json=json_data)
        response.raise_for_status()
        return response

    def add_content_model(self, pid, cmodel, exclusive=False):
        """
        Convenience function for cModel relationships
        no useful return, will crash fine if you do it wrong

        :param pid:
        :param cmodel:
        """
        i_know = False
        current_rels = self.get_relationships(pid, predicate='hasModel', uri="info:fedora/fedora-system:def/model#")

        for model_rel in current_rels:
            if model_rel['object']['value'] == cmodel:
                #         We've already got it.
                i_know = True
            else:
                if exclusive:
                    self.remove_relationship(pid, predicate='hasModel', ns="info:fedora/fedora-system:def/model#",
                                             object=model_rel['object']['value'])
        if not i_know:
            self.add_relationship(pid,
                                  object=cmodel,
                                  predicate='hasModel',
                                  ns='info:fedora/fedora-system:def/model#')

    def add_collection_membership(self, pid, parent_pid):
        """
        Convenience function for isMemberOfCollection relationships
        no useful return

        :param pid:
        :param parent_pid:
        """
        i_know = False
        existing_collections = self.get_relationships(pid,
                                                      uri="info:fedora/fedora-system:def/relations-external#",
                                                      predicate='isMemberOfCollection')
        for collection in existing_collections:
            if collection['object']['value'] == parent_pid:
                i_know = True
        if not i_know:
            self.add_relationship(pid, object=parent_pid, predicate='isMemberOfCollection',
                                  ns='info:fedora/fedora-system:def/relations-external#')

    def remove_collection_membership(self, pid, parent_pid_to_remove):
        self.remove_relationship(pid, predicate='isMemberOfCollection',
                                 ns='info:fedora/fedora-system:def/relations-external#',
                                 object=parent_pid_to_remove)

    # Datastreams:
    # GET       /islandora/rest/v1/object/{pid}/datastream/{dsid}       GET a datastream for an object
    # POST      /islandora/rest/v1/object/{pid}/datastream/             CREATE a datastream on object
    # PUT       /islandora/rest/v1/object/{pid}/datastream/{dsid}       UPDATE an existing datastream
    # DELETE    /islandora/rest/v1/object/{pid}/datastream/{dsid}       DELETE an existing datastream

    def get_datastream(self, pid, dsid, version=None, streaming=False, streaming_size=4096):
        if not pid:
            raise Exception("Missing PID")
        if not dsid:
            raise Exception("Missing DSID")
        params = {
            "content": "true",
            "version": version
        }
        url = "object/{}/datastream/{}".format(pid, dsid)
        kwargs = {}
        if streaming:
            kwargs['stream'] = True
        response = self.get(url, params=params, **kwargs)
        response.raise_for_status()
        if not streaming:
            return response.content
        else:
            return response.iter_content(streaming_size)

    def get_datastream_info(self, pid, dsid, version=None):
        if not pid:
            raise Exception("Missing PID")
        if not dsid:
            raise Exception("Missing DSID")
        params = {
            "content": "false",
            "version": version
        }
        url = "object/{}/datastream/{}".format(pid, dsid)
        response = self.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def create_datastream(self, pid, dsid, *, file=None, string=None, versionable=True, **metadata_as_kwargs):
        """

        :return:
        :param pid:
        :param dsid:
        :param file:
        :param versionable: set with a Python boolean
        :param string:
        :param metadata_as_kwargs: Passthrough to the form data
            possible - label, state, mimeType, checksumType, controlGroup
        :return:
        """
        if not pid:
            raise Exception("Missing PID on create_datastream")
        if not dsid:
            raise Exception("Missing DSID on create_datastream")
        if file is None and string is None:
            raise Exception("Missing argument. Either file or string is required.")

        metadata_as_kwargs['dsid'] = dsid
        # versionable - really seems happiest with 0 or 1
        if versionable:
            metadata_as_kwargs['versionable'] = 1
        else:
            metadata_as_kwargs['versionable'] = 0
        if 'checksumType' not in metadata_as_kwargs:
            metadata_as_kwargs['checksumType'] = "MD5"

        url = "object/{}/datastream".format(pid)

        if file is not None:
            files = {
                "file": open(file, 'rb')
            }
        elif string is not None:
            files = {
                "file": ('{} data'.format(dsid), string)
            }
            # only do this for string pushes...
            if 'mimetype' not in metadata_as_kwargs:
                metadata_as_kwargs['mimeType'] = 'application/xml'
        else:
            files = None

        response = self.post(url, data=metadata_as_kwargs, files=files)
        response.raise_for_status()
        try:
            return response.json()
        except json.JSONDecodeError as json_error:
            # We find times where we upload a large file and we get a 201 Created but no JSON
            # Wish I knew where it was, but hack
            if response.status_code == 201:
                # Just send back an empty dict if we're okay otherwise
                return dict()
            else:
                raise json_error

    def update_datastream(self, pid, dsid, *, file=None, string=None, versionable=None, **metadata_as_kwargs):
        """

        :return:
        :param pid:
        :param dsid:
        :param versionable: Set with a Python boolean
        :param file: optional - String representation of a file to transmit
        :param string: optional - Direct string as a file (i.e., an XML dumps())
        :param metadata_as_kwargs: Passthrough to the form data
            possible - label, state, mimeType, checksumType (can't change the controlGroup)
        :return:
        """
        if not pid:
            raise Exception("Missing PID")
        if not dsid:
            raise Exception("Missing DSID")
        url = "object/{}/datastream/{}".format(pid, dsid)

        # versionable - really seems happiest with 0 or 1
        if versionable is not None:
            if versionable:
                metadata_as_kwargs['versionable'] = 1
            else:
                metadata_as_kwargs['versionable'] = 0
        if file is not None:
            files = {
                "file": open(file, 'rb')
            }
        elif string is not None:
            files = {
                "file": ('{} data'.format(dsid), string)
            }
            # only do this for string pushes...
            if 'mimeType' not in metadata_as_kwargs:
                metadata_as_kwargs['mimeType'] = 'application/xml'
        else:
            files = None

        # Because of issues PUTting a multi-part file upload
        # We POST and say we're PUTting.
        # https://github.com/discoverygarden/islandora_rest/blob/c7edb9afe578d0a1655aded874425a6330362387/tests/islandora_rest.test#L558
        metadata_as_kwargs['method'] = "PUT"
        response = self.post(url, data=metadata_as_kwargs, files=files)
        response.raise_for_status()
        return response

    def delete_datastream(self, pid, dsid):
        if not pid:
            raise Exception("Missing PID")
        if not dsid:
            raise Exception("Missing DSID")
        url = "object/{}/datastream/{}".format(pid, dsid)
        response = self.delete(url)
        response.raise_for_status()
        return response
