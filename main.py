from __future__ import print_function

import sys

# Recursively following the attributes of these types results in infinite recursion.
dontFollowTypes = set([
  type(None.__init__),
  type(None.__sizeof__),
])

def getAttribute(obj, attribute):
  try:
    # For some reason this is a static version of the __getattribute__ method and should work on
    # objects that don't have __getattribute__.
    value = None.__class__.__getattribute__(obj, attribute)
  except AttributeError as error:
    # For some reason there are listed attributes that can't be accessed.
    if obj == type and attribute == '__abstractmethods__':
      return None, error
    if obj == bool:
      return None, error
    print(repr(obj), attribute)
    raise
  return value, None

def doubleQuote(string):
  return '"%s"' % string.replace('"', '\\"')

def objectName(obj):
  name = repr(obj)
  if type(obj) in dontFollowTypes:
    # Cut out the memory address part:
    # This "<method-wrapper '__init__' of NoneType object at 0x91a870>"
    # becomes this "<method-wrapper '__init__' of NoneType object>"
    name = name[:-13] + name[-1:]
  return name

def graphObjectAttributes(rootObject):
  unprocessed = [rootObject]
  nameToId = {}
  idToObject = {}
  def getId(obj):
    name = objectName(obj)
    if name not in nameToId:
      id = len(nameToId)
      nameToId[name] = id
      idToObject[id] = obj
    return nameToId[name]
  graph = {}
  while unprocessed:
    obj = unprocessed.pop()
    edges = {}
    graph[getId(obj)] = edges
    for attribute in dir(obj):
      nextObj, err = getAttribute(obj, attribute)
      if err:
        continue
      nextId = getId(nextObj)
      edges[attribute] = nextId
      if type(nextObj) not in dontFollowTypes and nextId not in graph:
        unprocessed.append(nextObj)
  return graph, idToObject

def printDotGraph(graph, idToObject):
  print('digraph {')
  for id in graph:
    name = objectName(idToObject[id])
    print('  %s [label=%s];' % (id, doubleQuote(name)))
    for attribute, nextId in graph[id].items():
      print('  %s -> %s [label=%s];' % (id, nextId, doubleQuote(attribute)))
    print()
  print('}')

def printJsonGraph(graph, idToObject):
  print('{')
  print('  "nodes": {')
  for id in graph:
    group = str(type(idToObject[id]))
    print('    "id": %s, "group": %s},' % (id, doubleQuote(group)))
  print('  }')
  print('  "links": {')
  for id in graph:
    for attribute, nextId in graph[id].items():
      print('    "source": %s, "target": %s},' % (id, nextId))
  print('  }')
  print('}')

if __name__ == '__main__':
  root = None
  if len(sys.argv) > 1:
    root = eval(sys.argv[1])
  graph, idToObject = graphObjectAttributes(root)
  printJsonGraph(graph, idToObject)
