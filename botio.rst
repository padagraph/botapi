
BotIO / listen for events on graphs
===================================

1. Log into http://padagraph.io
2. Get you padagraph token from
   http://padagraph.io/account/me/generate\_auth\_token
3. Install requirements
    ``$ pip install -r requirements.txt``

Events
------

.. code:: python

    
    from botapi import Botio
    
    gid = "graphToListen"
    host="http://notifications.padagraph.io"
    port=80
    
    io = Botio(host, port)
    
    
    def wrap(e):
        def log(*args):
            print e, args
        return log
    
    
    
    io.listenTo(gid)
    for event in Botio.events:
        io.on(event, wrap(event) )
            
    print "botio is listening to %s @ %s:%s" % ( gid, host, port )
    
    io.socket.wait()



.. parsed-literal::

    connecting @ http://notifications.padagraph.io:80
    botio is listening to graphToListen @ http://notifications.padagraph.io:80
