
import itertools

def map_reduce(i,mapear,reducir):
  intermediate = []
  for (key,value) in i.items():
    intermediate.extend(mapear(key,value))
  groups = {}
  for key, group in itertools.groupby(sorted(intermediate), 
                                      lambda x: x[0]):
    groups[key] = list([y for x, y in group])
  return [reducir(intermediate_key,groups[intermediate_key])
          for intermediate_key in groups] 