#!/usr/bin/python
#
# Nagios2 HTTP proxy test
#
# usage: 
# check_http_proxy 
#     --url=site_url 
#     --expect=str_content 
#    [--auth=site_user:site_pass]
#    [--authtype=Basic|Digest|NTLM]
#    [--proxy=proxy:port]
#    [--pauth=proxy_user:proxy_pass]
#    [--timeout=10]
#    [--warntime=5]
#    [--debug]
#    [--help]
#
# Response codes: 0(OK), 1(WARNING), 2(CRITICAL), 3(UNKNOWN)
# Output: one line on stdout
#
# Copyright (C) 2011 Bradley Dean <bjdean@bjdean.id.au>
# Modified by Josh Qi (qipai7@gmail.com) to implement following feature:
#   -- proxy authentication
#   -- debug mode which prints full response from server
#   -- explicit Basic/Digest/NTLM authentication website authentication
#   -- HTTPS support
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import getopt
import time
import socket
import traceback
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
from requests_ntlm import HttpNtlmAuth
from ntlm import HTTPNtlmAuthHandler

# Parse command line options in C language manner
def get_cmdline_cfg():
  cfg = {}
  try:
    opts, args = getopt.getopt(
      sys.argv[1:],
      "",
      ["proxy=", "auth=", "pauth=","timeout=", "warntime=", \
      "expect=", "debug", "help", "url=", "authtype="])
    process_cfg(cfg, opts)
  except getopt.GetoptError, err:
    report_unknown(cfg, "SCRIPT CALLING ERROR: {0}".format(str(err)))

  #	Required options
  for req_param in ("url", "expect"):
    if req_param not in cfg:
      report_unknown(cfg, "Missing parameter: {0}".format(req_param))

  return cfg

def process_cfg(cfg, opts):
  for o, a in opts:
    if o == "--help":
      print_help()
      exit(0)
    elif o == "--proxy":
      cfg["proxy"] = a
    elif o == "--pauth":
      cfg["pauth"] = a
    elif o == "--timeout":
      cfg["timeout"] = float(a)
    elif o == "--warntime":
      cfg["warntime"] = float(a)
    elif o == "--expect":
      cfg["expect"] = a
    elif o == "--url":
      cfg["url"] = a
    elif o == "--auth":
      cfg["auth"] = a
    elif o == "--debug":
      cfg["debug"] = 1
    elif o == "--authtype":
      cfg["authtype"] = a
    else:
      print("Unrecognized option: ", o)
  if "warntime" not in cfg:
    cfg["warntime"] = 5
  if "timeout" not in cfg:
    cfg["timeout"] = 10

def test_proxy(cfg):
  try:
    start_time = time.time()
    proxies = {}
    auth = None
    # get authentication setting ready
    if "auth" in cfg and cfg["auth"] != '':
      username = cfg["auth"].split(':')[0]
      password = cfg["auth"].split(':')[1]
      if "authtype" in cfg:
        if cfg["authtype"] == "NTLM":
          auth = HttpNtlmAuth(username, password)
        elif cfg["authtype"] == "Digest":
          auth = HTTPDigestAuth(username, password)
        else:
          auth = HTTPBasicAuth(username, password)
    # get proxy setting ready
    if ("proxy" in cfg and cfg["proxy"] != ''):
      if "pauth" in cfg:
        proxies = {
          "http": "http://{pauth}@{proxy}".format(**cfg),
          "https":"http://{pauth}@{proxy}".format(**cfg)
          }
      else:
        proxies = {
          "http": "http://{proxy}".format(**cfg),
          "https":"http://{proxy}".format(**cfg)
          }
      request = requests.get(cfg["url"], proxies=proxies, \
        verify=False, auth=auth, timeout=cfg["timeout"])
    else:
      cfg["proxy"] = ''
      request = requests.get(cfg["url"], verify=False, \
        auth=auth, timeout=cfg["timeout"])
    responseValue = request.text
    # print full HTTP response when in debug mode
    if "debug" in cfg:
      print(responseValue)
    end_time = time.time()
    duration = end_time - start_time
  
   	# Check contet
    if "expect" in cfg:       
      if responseValue.find(cfg["expect"]) == -1:
        return report_critical(cfg)
 			
   	# Check warning time
    if "warntime" in cfg:
      if duration >= cfg["warntime"]:
        return report_warning(cfg, duration)

    return report_ok(cfg, duration) 
  except Exception as e:
    traceback.print_exc()
    return report_unknown(cfg, e)
  

# Print Nagios output
def report_ok(cfg, duration):
  print "{0} OK - {1} via {2}".format(conn_type(cfg["url"]), \
    "Request return in {0:.2f} seconds".format(duration), \
    proxy_msg(cfg["proxy"]))
  if __name__ == '__main__':
    sys.exit(0)
  return 0

def report_warning(cfg, duration):
  print "{0 }WARNING - {1} via {2}".format(conn_type(cfg["url"]), \
    "Over warning time ({0:.2f}s >= {warntime:.2f}s)".format(duration, **cfg), \
    proxy_msg(cfg["proxy"]))
  if __name__ == '__main__':
    sys.exit(1)
  return 1

def report_critical(cfg):
  print "{0} CRITICAL - {1} via {2}".format(conn_type(cfg["url"]), \
    "Failed content check", \
    proxy_msg(cfg["proxy"]))
  if __name__ == '__main__':
    sys.exit(2)
  return 2

def report_unknown(cfg, e):
  if "proxy" not in cfg:
    cfg["proxy"] = "N/A"
  if "url" not in cfg:
    cfg["url"] = "N/A"
  print "{0} UNKNWON - {1} via {2}".format(conn_type(cfg["url"]), \
    "Request failed: ({0})".format(`e`), \
    proxy_msg(cfg["proxy"]))
  if __name__ == '__main__':
    sys.exit(3)
  return 3

def conn_type(conn_string):
    return "HTTP"

def proxy_msg(proxy):
  if proxy == '':
    return "DIRECT"
  else:
    return proxy

def print_help():
  print(  
"""# usage:
 check_http_proxy
     --url=site_url
     --expect=str_content
    [--auth=site_user:site_pass]
    [--authtype=Basic|Digest|NTLM]
    [--proxy=proxy:port]
    [--pauth=proxy_user:proxy_pass]
    [--timeout=10]
    [--warntime=5]
    [--debug]
    [--help]""")



if __name__ == '__main__':
  cfg = get_cmdline_cfg()
  test_proxy(cfg)

 
