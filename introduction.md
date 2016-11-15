botapi for padagraph

#  Introduction

## Graph creation

Graphs contains `nodes` and `edges`.

###  Typed nodes and edges
    
For any graph we will create a set ``nodetype`` and ``edgetype``

    * Nodetype and edgetypes contains properties
      Each property has a name, is  typed and contains a value.  
      A `type` is not limited in properties.

      Currrently ``Text`` and ``Numeric`` types are available.

    * Edges and nodes are extended form a `type`,
      and contains a value for each property defined by it's type.

### Node properties

      ** a `label` property should be set for each `Node`
         This property is used as label for node in visualisation
         and is also searchable. 
         ex:  a property `label ` is of type `Text` and has a value `The Little Prince`
         
      ** `shape` is used in visualisation to render a node with a shape.
         it can have one value of `circle`, `square`, `triangle`.
         property `shape ` of type `Text`  value `circle`
            
      ** `image` is used in cards and visualisation to render a node with an image.
         the value of the property image should be a valir `url` to an image
         property `image ` of type `Text`  value `image url`

### Edge properties

      ** a `label` property can be set an `edge`
         This property is used as label for edge in visualisation
         If none is set the edgetype label will be used.
         ex:  a property `label ` is of type `Text` and has a value `friend`


## Exploration