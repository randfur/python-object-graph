from __future__ import print_function

import sys

# Recursively following the attributes of these types results in infinite recursion.
dontFollowTypes = set([
  type(None.__init__),
  type(None.__sizeof__),
])

def getAttribute(obj, attribute):
  try:
    value = None.__class__.__getattribute__(obj, attribute)
  except AttributeError:
    if obj == type and attribute == '__abstractmethods__':
      return None, True
    raise
  return value, False

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
  idToName = {}
  def getId(obj):
    name = objectName(obj)
    if name not in nameToId:
      id = len(nameToId)
      nameToId[name] = id
      idToName[id] = name
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
  return graph, idToName

def printGraph(graph, idToName):
  print('digraph {')
  for id in graph:
    name = idToName[id]
    print('  %s [label=%s];' % (id, doubleQuote(name)))
    for attribute, nextId in graph[id].items():
      print('  %s -> %s [label=%s];' % (id, nextId, doubleQuote(attribute)))
    print()
  print('}')

if __name__ == '__main__':
  root = None
  if len(sys.argv) > 1:
    root = eval(sys.argv[1])
  graph, idToName = graphObjectAttributes(root)
  printGraph(graph, idToName)
