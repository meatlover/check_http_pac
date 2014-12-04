#!/usr/bin/python

import time, sys, os, tempfile, httplib, re, hashlib, string

pacfile_check_interval=60

# cache pac file from web site to local temp folder via HTTP request
def cache( pac_address ):
  os.system("2>/dev/null")
  tempdir = tempfile.gettempdir() + '/get_pacfile_cache'
  site_pattern = r"(?<=http(s)://)[^/]+(?=/)"
  site = ""
  path = ""

# split site and relative url in pac file address
  if not re.search(site_pattern, pac_address) == None:
    site = re.search(site_pattern, pac_address).group(0)
    e = string.split(pac_address, site)
    path = e[-1]
# delete temp file which should be folder
  if os.path.exists(tempdir) and not os.path.isdir(tempdir):
    os.system("rm -f %s" % tempdir)
# create temp folder if not exist
  if not os.path.isdir(tempdir):
    os.system("mkdir %s " % tempdir)
  
# check if the stamp file does not exist for this pac file or 
# it is too ancient, download the pacfile and renew stamp
  file_prefix = tempdir + '/' + hashlib.md5(pac_address).hexdigest()

  hash_file = file_prefix + ".stamp"
  pac_file = file_prefix + ".pac"
  debug_file = file_prefix + ".debug"

  if not os.path.exists(hash_file) or (
      os.path.getmtime(hash_file) + pacfile_check_interval < \
      time.mktime(time.localtime())):
    os.system("wget %s -q -O %s" % (pac_address, pac_file))
    os.system("wget %s -q --spider --server-response 2>%s" % (pac_address, debug_file))
    os.system("touch %s" % hash_file)
 
# Pac file is ready at this point
  return pac_file

# Check to see if the URL is accessable
def page_accessble(site, path):
  conn = httplib.HTTPConnection(site)
  conn.request('HEAD', path)
  response = conn.getresponse()
  conn.close()
  return response.status == 200

if __name__ == '__main__':
  print("Pac file cached to: %s" % cache(sys.argv[1]))

