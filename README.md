
# botapi for padagraph

1. Log into http://padagraph.io
2. Get you padagraph token from http://padagraph.io/account/me/generate_auth_token
3. Install requirements  
  ```$ pip install -r requirements.txt ```

## BotaGraph / simple bot api for padagraph

## Bot connection

Using the token we will connect to the padagraph api


    from botapi import Botagraph
    
    host = "http://localhost:5000"
    key  = "WyJwQHAuaW8iLCIkMmIkMTIkdC9FUHZkRTF2MVdKeXNWMFh1bjNWLjVwczlKNGNqL2plSWdjZnpramVlYnBOclhjUVRGMXUiXQ.Ch2UxA.L0Ii1JoVYfGoUN1SIi0Ye1MLaU0"
    
    bot = Botagraph(host, key)

### Sample network

We will create a simple network of people that know each other
* with 20 person and ~100 relations


    
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


    20 73


### create graphs

* Graphs are identified by uniq name,
* You can add a description and some tags , you cal also add an url to embed an image.


    gid = "sample network6"
    g_attrs = {
        'description': "your descripton",    
        'image': "http://example.com/yourimage.png",
        'tags' : ['add', 'some' , 'tags' ]
    }
    
    if not bot.has_graph(gid) :
        bot.create_graph(gid, g_attrs)

### Add a schema

Graphs are made of vertices (or nodes ) and edges.  
Each nodes and edges are typed with properties.  
These properties are defined using `nodetypes` and `edgetypes`  and each propertiy should be specified using basic types.  

For any schema we will create a set of properties for each `nodetype` and and `edgetype`  

In this example we will create a network of person that knows others.  
Persons will have some properties related to personnal informations.  


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




    u'62232d58da4d4ee2aa0971ddd25f02b0'




### Get the schema back from the server




    schema = bot.get_schema(gid)['schema']
    nodetypes = { n['name']:n for n in schema['nodetypes'] }
    edgetypes = { e['name']:e for e in schema['edgetypes'] }

### Posting nodes & edges 

There is two ways to insert nodes.  
You can insert nodes one by one or bulk insert by 100 which is really faster for big graphs.

* One by one
You need to provide the nodetype uuid and the node properties.  
In the result you'll get the `uuid` of the created node.


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


    for r in relations:
        
        payload = {
            'edgetype': edgetypes['Knows']['uuid'],
            'source': idx[r[0]], # node src uuid
            'target': idx[r[1]], # node target uuid
            'properties': {'since' : r[2]}
        }
        
        uuid = bot.post_edge(gid, payload)

### Starring

Stars are used when opening a graph. The graph will show the starred nodes first. Don't star more than 100 nodes for clarity and performances.


    bot.star_nodes(gid, idx.values())




    {u'count': 20,
     u'graph': u'sample network6',
     u'nodes': [u'664ef6d5dc414796b9d4504a3041a773',
      u'4bf522bc9ed44e92bee1f179d0a3f9de',
      u'356e14a2d9b14d6c9c34c1d1c1369fdd',
      u'0bfa20982e654424938039e3ffd34420',
      u'060071d222e94540b334fb018327170b',
      u'e979bd424d3e4237802c85ac6a568300',
      u'bcf000d7c3ab4e768142fc9d5ffb3ce0',
      u'11824e35a91d49f7b977e2d5e67e2495',
      u'b312b4ea677343d0a0e96f49c2d135d1',
      u'2c3a2fb55e064e9cadb9015531bf0c56',
      u'8f6fdb503c6443afa2f99abe99da3d5c',
      u'3d5fae4b0e3b47ef95d69195ec2fa745',
      u'628af38d00db4dd2bcd2cd6dcc14bb43',
      u'5cea9daf5c454c79a4f47e981f21cb77',
      u'c9d8540485bc4dd38fff54fa00754e9d',
      u'0489bb0431ee4f79a56115af3c03e3c8',
      u'381d284283d745378128a5082009f504',
      u'4cb5d7d559774a1f9c0ec9b43a43974e',
      u'61345109d56e43a6947cee403597e8fc',
      u'3f7bbe5ecf364d8bafe15820507e47ba'],
     u'star': True}



## BotIO / listen for events on graphs 

### Events


    
    from botapi import Botio
    
    io = Botio(host=args.host, port=args.port)
    
    def wrap(e):
        def log(*args):
            print e, args
        return log
    
    
    io.listenTo(args.gid)
    for event in Botio.events:
        io.on(event, wrap(event) )
            
    print "botio is listening to %s @ %s:%s" % ( args.gid, args.host, args.port )
    
    io.socket.wait()



    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    <ipython-input-31-ec32013985c4> in <module>()
          2 from botapi import Botio
          3 
    ----> 4 io = Botio(host=args.host, port=args.port)
          5 
          6 def wrap(e):


    NameError: name 'args' is not defined

