# botapi for padagraph

1. Get you padagraph token from http://padagraph.io/users/me/generate_auth_token

## BotaGraph / simple bot api for padagraph

### Connect Bot


``` python
from botapi import Botagraph

host = "http://padagraph.io"
key  = "get your key"

bot = Botagraph(host, key)
```


### create graphs





### post nodes & edges 









## BotIO / listen for events on graphs 

### Events




``` python 

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
    
```