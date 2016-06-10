
botapi for padagraph
====================

1. Log into http://padagraph.io
2. Get you padagraph token from
   http://padagraph.io/account/me/generate\_auth\_token
3. Install requirements
    ``$ pip install -r requirements.txt``

BotaGraph / simple bot api for padagraph
----------------------------------------

Bot connection
--------------

Using the token we will connect to the padagraph api

.. code:: python

    from botapi import Botagraph
    
    host = "http://padagraph.io"
    key  = "WyJwQHAuaW8iLCIkMmIkMTIkdC9FUHZkRTF2MVdKeXNWMFh1bjNWLjVwczlKNGNqL2plSWdjZnpramVlYnBOclhjUVRGMXUiXQ.Ch2UxA.L0Ii1JoVYfGoUN1SIi0Ye1MLaU0"
    
    bot = Botagraph(host, key)

Sample network
~~~~~~~~~~~~~~

We will create a simple network of people that know each other \* with
20 persons and ~100 relations

.. code:: python

    
    import random
    
    names = """Anaïs,Annabelle,Arianne,Audrey,Aurélie,Camille,Catherine,Charlotte,Coralie,Daphnée,
    Malik,Mathieu,Mathis,Michaël,Nicolas,Noah,Olivier,Philippe,Raphaël,Samuel""".split(",")
    people = [  {'name':n, 'gender': 'F' if i <10 else 'M', 'age': random.randint(16,54) } for i, n in enumerate(names) ]
    
    relations = []
    rels_keys = set()
    for i, k in enumerate(people):
        n_rels = random.randint(1,10)
        e = range(len(people))
        e.remove(i)
        for i in range(n_rels) :
            k = random.choice(e)
            # test if we dont already have this relation
            key = (i,k) if i < k  else (k,i)
            if key not in rels_keys:
                # relation is ( someone, other , year )
                relations.append( (people[i]['name'], people[k]['name'], random.choice(range(2000,2016))) )
                rels_keys.add(key)
    print len(people), len(relations)


create graphs
~~~~~~~~~~~~~

-  Graphs are identified by uniq name,
-  You can add a description and some tags , you cal also add an url to
   embed an image.

.. code:: python

    gid = "sample network6"
    g_attrs = {
        'description': "your descripton",    
        'image': "http://example.com/yourimage.png",
        'tags' : ['add', 'some' , 'tags' ]
    }
    
    if not bot.has_graph(gid) :
        bot.create_graph(gid, g_attrs)

Add a schema
~~~~~~~~~~~~

| Graphs are made of vertices (or nodes ) and edges.
| Each nodes and edges are typed with properties.
| These properties are defined using ``nodetypes`` and ``edgetypes`` and
each propertiy should be specified using basic types.

For any schema we will create a set of properties for each ``nodetype``
and and ``edgetype``

| In this example we will create a network of person that knows others.
| Persons will have some properties related to personnal informations.

.. code:: python

    from reliure.types import Numeric, Text
    
    person_props = {
          
          'name'  : Text(),
          'gender': Text(),
          'age'   : Numeric(),
          # properties used for visualisation
          'label' : Text(), # note you should always have a label for graph visualisation ! 
          'shape' : Text(default=u'square')    
        }
        
    bot.post_nodetype(gid, "Person",  "Basic informations ", person_props)
    
    rel_props = {
        'since' : Numeric(), # consider a year
    }
    bot.post_edgetype(gid, "Knows", "a person knows another" , rel_props )

Get the schema back from the server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    schema = bot.get_schema(gid)['schema']
    nodetypes = { n['name']:n for n in schema['nodetypes'] }
    edgetypes = { e['name']:e for e in schema['edgetypes'] }

Posting nodes & edges
~~~~~~~~~~~~~~~~~~~~~

| There is two ways to insert nodes.
| You can insert nodes one by one or bulk insert by 100 which is really
faster for big graphs.

-  One by one You need to provide the nodetype uuid and the node
   properties.
   In the result you'll get the ``uuid`` of the created node.

Nodes
^^^^^

.. code:: python

    # keep a node index (name, uuid) for relations
    idx = {} 
    
    
    for p in people:
        p['label'] = p['name'] # use names as label
        p['shape'] = 'circle' if p['gender'] == 'F' else 'square' # distinct node based on gender
        
        payload = {
            'nodetype': nodetypes['Person']['uuid'],
            'properties': p
        }
        node = bot.post_node(gid, payload)
        # we keep vids for futur use
        idx[p['name']] = node['uuid']

Edges
^^^^^

.. code:: python

    for r in relations:
        
        payload = {
            'edgetype': edgetypes['Knows']['uuid'],
            'source': idx[r[0]], # node src uuid
            'target': idx[r[1]], # node target uuid
            'properties': {'since' : r[2]}
        }
        
        uuid = bot.post_edge(gid, payload)

Starring
~~~~~~~~

Stars are used when opening a graph. The graph will show the starred
nodes first. Don't star more than 100 nodes for clarity and
performances.

.. code:: python

    bot.star_nodes(gid, idx.values())
