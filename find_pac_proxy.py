#!/usr/bin/python

import os, sys, pacparser, cache_pacfile

def find( site, pacfile, myip = "" ):
  pacparser.init()
  pac_file_cache = cache_pacfile.cache(pacfile)
  if not myip == "":
    pacparser.setmyip(myip)
  pacparser.parse_pac(pac_file_cache)

  return pacparser.find_proxy(site) 

if __name__ == '__main__':
  if len(sys.argv) > 3:
    print(find(sys.argv[1],sys.argv[2],sys.argv[3]))
  else:
    print(find(sys.argv[1],sys.argv[2]))

 
