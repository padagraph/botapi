#-*- coding:utf-8 -*-

import requests
import json
from itertools import islice
import logging
import time
from cello.graphs import GraphBuilder 



log = logging.getLogger(__name__)


""" simple botapi to post graph """

class BotError(Exception):
    pass
    
class BotApiError(BotError):
    def __init__(self, url, data, response):
        """ Function doc
        :param : 
        """
        self.message ='Something is wrong, got response code %s' % response.status_code
        self.response = response
        self.url = url
        self.data = data
        #self.json = response.json()
        message = "\n".join( [self.message,  url, str(data)])
        error = response.text
        log.error( "!! ERROR !! %s", str(error) )
        print( error )
        Exception.__init__(self, message) 
        
class BotLoginError(BotError):
    def __init__(self, message, host):
        super(BotLoginError, self).__init__(message)
        self.host = host

def gen_slice(gen, chunksize):
    while True:    
        chunks = list(islice(iter(gen), chunksize))
        if chunks == []:
            break
        yield chunks

def http_retry(f):
    def _http_meth(*args, **kwargs):
        max_retry = 5
        wait  = 1 #seconds
        for i in range(max_retry+1):
            try:
                return f(*args, **kwargs)
            # Work around https://github.com/kennethreitz/requests/issues/2364
            except requests.exceptions.ConnectionError as e:
                if i == max_retry:
                    log.error("ERROR MAX_RETRY %s", str(e))
                    raise e
                log.warn("%s When requesting server; retrying... in %ss", str(e), wait)
                time.sleep(wait)
                
    return _http_meth
          

class Botagraph(object):
    headers={'Content-Type': 'application/json'}
        
    def __init__(self, host="http://localhost:5000", key=None, verbose=False):
        self.host = host
        self.verbose = verbose

        self.key = None if key == "" else key
        # try to connect  
        if self.key:
            url = "account/me"
            resp = self.get(url)
            
    def _send(self, method, url, payload={}):
    
        if self.key is None:
            raise BotLoginError("I miss a valid authentification token")

        url = "%s/%s" %(self.host, url)
        headers = {"Authorization" : self.key}

        if method == "GET":
            if self.verbose :
                print("\n == GET ==", url, "\n", headers)
            resp = requests.get(url, headers=headers)
        if method == "DELETE":
            if self.verbose :
                print("\n == DELETE ==", url, "\n", headers)
            resp = requests.delete(url, headers=headers)
        if method == "POST":
            headers['Content-Type'] = 'application/json'
            if self.verbose :
                print("\n == POST ==", url, "\n", headers, payload)
            resp = requests.post(url, json=payload, headers=headers)
        if method == "PUT":
            if self.verbose :
                print("\n == PUT ==", url, "\n", headers, payload)
            resp = requests.put(url, data=payload, headers=headers)

        if self.verbose :
            print( "\n == RESP ==", resp.status_code , "\n",resp.headers,"\n", resp.text)
        
        if 401 == resp.status_code:
            raise BotLoginError('Invalid credentials', self.host) 

        elif resp.status_code != 200:
            raise BotApiError(url, payload, resp)

        return resp

    @http_retry
    def post(self, url, payload={}):
        """ http POST request """
        return self._send("POST", url, payload)
        
    @http_retry
    def put(self, url, payload={}):
        """ http PUT request """
        return self._send("PUT", url, payload)
        
    @http_retry
    def get(self, url):
        """ http GET request """
        return self._send("GET", url)

    @http_retry
    def delete(self, url):
        """ http DELETE request """
        return self._send("DELETE", url)

    def _post_one(self, obj_type, gid, payload):
        url = "graphs/g/%s/%s" % (gid, obj_type)
        resp = self.post(url, payload)
        
        if self.verbose:
            print( "POST %s, %s " % (url,payload) )

        return resp.json()

    def _post_multi(self, obj_type, gid, objs ):
        url = "graphs/g/%s/%s" % (gid, obj_type)
        for chunks in gen_slice(objs, 100):
            payload = { "%s" % obj_type: chunks }
            #
            if self.verbose:
                print( "POST %s, %s " % (url,len(chunks)) )

            resp = self.post(url, payload)

            data = resp.json()
            results = { i:uuid for i, uuid in data['results'] }

            for i, obj in enumerate(chunks):
                yield obj, results.get(i, None) 
        
    def get_schema(self, gid):
        url = "graphs/g/%s/schema" % gid
        resp = self.post(url)
        return resp.json()
        
    def has_graph(self, gid):
        g = self.get_graph(gid)
        try : 
            return "properties" in g
        except:
            return False

        
    def get_graph(self, gid):
        """
        get graph infos
        :param gid: graph name
        """
        url = "graphs/g/%s" % (gid)
        try : 
            resp = self.get(url)
            g = resp.json()
            return g[gid]
        except  :
            return None

    def create_graph(self, gid, props):
        """ create a new graph
        :param gid: graph name
        :param props: graph properties
        
        supported properties are :
        
            properties = {
                'description': "your descripton",    
                'image': "http://example.com/yourimage.png",
                'tags' : ['add', 'some' , 'tags' ]
            }

        """

        url = "graphs/create"
        payload = { "name": gid,
                    "description": props.get('description', ""),
                    "tags": props.get('tags', []),
                    "image": props.get('image', ""),
                }
        resp = self.post(url, payload)
        return resp.json()


    def delete_graph(self, gid):
        url = "graphs/g/%s" % (gid)
        try : 
            resp = self.delete(url)
            return resp.json()
        except BotApiError as e:
            raise
        

    def get_node_by_id(self, gid, uuid):
        url = "graphs/g/%s/node/%s" % (gid, uuid)
        resp = self.get(url)
        return resp.json()

    def get_node_by_name(self, gid, uuid):
        url = "graphs/g/%s/node/%s/by_name" % (gid, uuid)
        resp = self.get(url)
        return resp.json()
        
    def create_nodetype(self, gid, name, desc,  properties):
        """
        creates an nodetype for a graph
        :param gid: graph uniq name
        :param name: nodetype name
        :param desc: nodetype description
        :param properties: nodetype properties
            from reliure.types import Text, Numeric 
            properties = {
                "label" : Text()
                "age"   : Numeric()
            }
            
        :returns : created nodetype uuid
         """
        return self.post_nodetype( gid, name, desc,  properties)
        

    def post_nodetype(self, gid, name, desc,  properties):
         
        payload = { 'name': name,
                    'description' : desc,
                    'properties': { k: v.as_dict() for k,v in properties.iteritems() }
                  }
        resp = self._post_one( "nodetype", gid, payload )

        return resp
        
    def create_nodetype(self, gid, name, desc,  properties):
        """
        creates an edgetype for a graph
        :param gid: graph uniq name
        :param name: edgetype name
        :param desc: edgetype description
        :param properties: edgetype properties

            from reliure.types import Text, Numeric 
            properties = {
                "label" : Text()
                "value" : Numeric()
            }
            
        :returns : created edgetype uuid
         """
        return self.post_edgetype( gid, name, desc,  properties)


    def post_edgetype(self, gid, name, desc,  properties):
        """
        creates an edgetype for a graph
        :param gid: graph uniq name
        :param name: edge type name
        :param name: edge type description
        :param name: edge type properties
        :returns : created edgetype uuid
        """
        payload = { 'name' : name,
                    'description': desc,
                    'properties': { k: v.as_dict() for k,v in properties.iteritems() }
                  }
                   
        resp = self._post_one( "edgetype", gid, payload )
        
        return resp
        
    def post_edge(self, gid, payload):
        """
        creates an edge in a graph
        :param gid: graph uniq name
        :param payload: edge data
          payload = {
            'edgetype': uuid , # edgetype uuid,
            'source': src , # node src uuid
            'target': tgt , # node target uuid
            'properties': {'any' : "prop" }
          }
        :returns : created edgetype uuid
        """
        return self._post_one( "edge", gid, payload )

    def post_edges(self, gid, edges ):
        """ bulk insert edges """
        for v in self._post_multi("edges", gid, edges ):
            yield v

    
    def delete_edge(self, gid, eid):
        """ delete a ede from a graph
        :param gid: graph gid
        :param eid: edge uuid
        """ 
        url = "graphs/g/%s/edge/%s" % (gid, eid)
        self.delete(url)
        

    def post_node(self, gid, payload):
        """
        create a node in a graph
        :param gid: graph gid
        :param payload: node payload
            payload = {
                'nodetype': uuid, # node type uuid 
                'properties': { 'label' : 'foo' , 'a' : 2 ... } node properties
             }
            Mind that only `label` properties are searchable and use in graph visualiation !!
        """
        return self._post_one( "node", gid, payload )
         

    def post_nodes(self, gid, nodes ):
        """ bulk nodes insertions """
        for v in self._post_multi("nodes", gid, nodes ):
            yield v
        
    def delete_node(self, gid, nid):
        """ delete a node from a graph
        :param gid: graph gid
        :param nid: node uuid
        """ 
        url = "graphs/g/%s/node/%s" % (gid, nid)
        self.delete(url)
      
    def star_nodes(self, gid, nodes_uuids ):
        """
        stars nodes , starred node with be first shown when visitor access a graph
        :param gid: graph name
        :param nodes_uuids: nodes uuids
        """
        url = "graphs/g/%s/nodes/star" % (gid)
        for chunks in gen_slice(iter(nodes_uuids), 100):
            payload = {
                "nodes": chunks
            }
            resp = self.post(url, payload)
    
    def unstar_nodes(self, gid, nodes_uuids ):
        """
        unstars nodes 
        :param gid: graph name
        :param nodes_uuids: nodes uuids to unstar
        """
        url = "graphs/g/%s/nodes/unstar" % (gid)
        payload = {
            "nodes": nodes_uuids
        }
        resp = self.post(url, payload)
        return resp.json()

    def find_nodes(self, gid, nodetype_uuid, properties, start=0, size=100):
        """ iterate nodes of one type , filters on properties matching '==' 
        :param graph: graph name
        :param nodetype_name: nodetype name
        :param properties: dict of key:value node should match
        :param start: pagination start
        :param size:  resultset size ( may be shorten by server )

             "nickname":"", 
        """
        url = "graphs/g/%s/nodes/find" % (gid)
        payload = {
                "start": start,
                "size" : size,
                "nodetype" : nodetype_uuid,
                "properties" : properties
        }
        resp = self.post(url, payload)
        data = resp.json()

        for v in data['nodes']:
            yield v
        
    def find_all_nodes(self, gid, nodetype_uuid, properties, start=0, size=100):
        """
        like find nodes makes a complete iteration of the nodes matching node_type and properties
            :see: find_nodes
        """
        start =   0 if size < 0 else start
        size  = 100 if size > 100 else size

        while True:
            nodes = list( self.find_nodes(gid, nodetype_uuid, properties, start, size))
            if not len(nodes) :
                break
            start += size
            for node in nodes:
                yield node

    def iter_neighbors(self, gid, nodeuuid, start=0, size=100):
        """ return neighbors of a node
        :param graph: graph name  
        :param node: node uuid  
        """
        start =   0 if size < 0 else start
        size  = 100 if size > 100 else size

        url = "graphs/g/%s/node/%s/neighbors" % (gid, nodeuuid)

        while True:
            payload = {
                "start": start,
                "size" : size,
            }

            resp = self.post(url, payload)
            neighbors = resp.json()['neighbors']

            for v in neighbors:
                yield v
            
            if not len(neighbors) :
                break

            start += size
            
        
    def count_neighbors(self, gid, node ):
        """ Function doc
        :param gid: graph gid
        :param node: node uuid 
        """
        url = "graphs/g/%s/node/%s/neighbors/count" % (gid, node)
        resp = self.post(url, {})
        return resp.json()['neighbors']

  
    def prox(self, graph, pzeros, weights=[], filter_edges=[], filter_nodes=[], step=3, limit=100):
        url = "graphs/g/%s/proxemie" % graph
        payload =  {
            'p0' : pzeros,
            'weights': weights, 
            'filter_nodes' : filter_nodes , 
            'filter_edges' : filter_edges , 
            'limit': limit, 
            'step':step, 
        }

        resp = self.post(url, payload)
        
        return resp.json()

    def get_subgraph(self, gid, nodes_uuids):
        """
        extract subgraph from node uuids
        :param gid: graph gid
        :param nodes_uuids: list of node uuids
        :returns : serialized graph in json
        """
        url = "graphs/g/%s/subgraph" % gid
        payload =  {
            'graph' : gid,
            'nodes': nodes_uuids,
        }
            
        resp = self.post(url, payload)
        return resp.json()


        

class BotaIgraph(Botagraph):
    
    def __init__(self):

        super(BotaIgraph, self).__init__(key=None)
        self.builder = GraphBuilder()
        
    def delete_graph(self, gid):
        pass
    def star_nodes(self, gid , nodes):
        pass

    def has_graph(self, gid):
        return True

    def get_graph(self, gid):
        return self.get_schema(gid)
        
    def get_schema(self, gid):
        return {
            'graph' : gid,
            'schema' : { 'nodetypes' : [],
                         'edgetypes' : []
                       }
        }
        
    def create_graph(self, gid, props):
        attributes = {
            'graph' : gid,
            'gid' : gid,
            'nodetypes' : [] ,
            'edgetypes' : [] ,
            'properties': props
            }
        self.builder.set_gattrs( **attributes )
        
        for e in ["uuid","edgetype","properties"]:
            self.builder.declare_eattr(e)
        for e in ["uuid","nodetype","properties"]:
            self.builder.declare_vattr(e)

        self.builder.reset()
        
        return gid
    
    def post_nodetype(self, gid, name, desc,  properties):
        types = self.builder._graph_attrs['nodetypes']
        return self._post_type( types, gid, name, desc,  properties)
        
    def post_edgetype(self, gid, name, desc,  properties):
        types = self.builder._graph_attrs['edgetypes']
        return self._post_type( types, gid, name, desc,  properties)
        
    def _post_type(self, types, gid, name, desc,  properties):
        payload = {
            'uuid': "_%s_%s" %(gid, name),
            'uniq_key': "_%s_%s" %(gid, name),
            'name': name,
            'description' : desc,
            'properties': { k: v.as_dict() for k,v in properties.iteritems() }
        }
        types.append(payload)
        return payload
        
    def post_nodes(self, gid, nodes ):
        for node in nodes:
            #     !!!
            padid = node['properties'].get('id', node['properties']['label'])
            uuid = self.builder.add_get_vertex(padid)
            
            node['uuid'] = str(uuid)
            self.builder.set_vattr(uuid, 'uuid', node['uuid'])
            self.builder.set_vattr(uuid, 'nodetype', node['nodetype'])
            self.builder.set_vattr(uuid, 'properties', node['properties'])
            yield node, uuid
            
    def post_edges(self, gid, edges ):
        
        for edge in edges:
            uuid = self.builder.add_get_edge(edge['source'], edge['target'])
            edge['uuid'] = uuid
            self.builder.set_eattr(uuid, 'uuid', uuid)
            self.builder.set_eattr(uuid, 'edgetype', edge['edgetype'])
            self.builder.set_eattr(uuid, 'properties', edge['properties'])
            yield edge, uuid

    def get_igraph(self):
        graph = self.builder.create_graph()
        graph['meta'] = {
            'node_count': graph.vcount(),
            'edge_count': graph.ecount(),
            'owner': "-",
            'star_count': 0,
            'upvotes': 0,
            'votes': 0
        }
        return graph
