#!/usr/bin/python
# Nagios2 HTTP pacfile test
#
# usage:
# check_http_pac
#     --url=url
#     --pac=pac_file
#     --expect=content
#     --myip=test_ip_address
#    [--auth=site_user:site_pass]
#    [--authtype=Basic|Digest|NTLM]
#    [--pauth=proxy_user:proxy_pass]
#    [--timeout=10]
#    [--warntime=5]
#    [--debug]
#    [--help]
#
# Response codes: 0(OK), 1(WARNING), 2(CRITICAL), 3(UNKNOWN)
# Output: one line on stdout
#
# ref: https://code.google.com/p/python-ntlm/
# ref: pacparser https://code.google.com/p/pacparser/
# ref: check_http_proxyi http://bjdean.id.au/wiki/Programming_Notes/Nagios_HTTP_Proxy_Plugin
#
# Copyright (C) 2014 Josh Qi <qipai7@gmail.com>
# Modified by Josh Qi (qipai7@gmail.com) to implement following feature:
#   -- proxy authentication
#   -- debug mode which prints full response from server
#   -- explicit Basic/Digest/NTLM authentication website authentication
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

import find_pac_proxy
import os, string, sys
import getopt
import check_http_proxy
import traceback

def check(cfg):
  find_result = find_pac_proxy.find(cfg["url"], cfg["pac"], cfg["myip"])
  if find_result.startswith("DIRECT"):
    cfg["proxy"] = ""
  else:
    cfg["proxy"] = find_result[6:]
  if "warntime" in cfg:
    cfg["warntime"] = float(cfg["warntime"])
  if "timeout" in cfg:
    cfg["timeout"] = float(cfg["timeout"])
  return check_http_proxy.test_proxy(cfg)

def print_help():
    print("""
Usage:
 check_http_pac
     --url=url
     --pac=pac_file
     --expect=content
    [--auth=site_user:site_pass]
    [--authtype=Basic|Digest|NTLM]
    [--pauth=proxy_user:proxy_pass]
    [--timeout=10]
    [--warntime=5]
    [--debug]
   
Example:   
check_http_pac --url="http://www.google.com" --pac="http://proxybj.websense.com/wbsn.pac" --myip=10.32.23.95 --expect="Google Search.*I'm Feeling Lucky" --timeout=20 --warntime=5 --debug
-- Check access of http://www.google.com via pac file http://proxybj.websense.com/wbsn.pac 
   with the source ip address: 10.32.23.95 to see if the response contains the string 
   "I'm Feeling Lucky". This test returns warning after 5 seconds the request is sent 
   and times out after 20 seconds. Full response is printed in debug mode.""")  

if __name__ == '__main__':
    opts, args = getopt.getopt(
      sys.argv[1:],
      "v",
      ["url=", "pac=", "expect=", "warntime=", "timeout=", "myip=", \
       "auth=", "pauth=", "debug", "authtype=", "help"])
    cfg = {}
    for o, a in opts:
      if o == "--help":
        print_help()
        exit(0)
      elif o == "--url":
        cfg["url"] = a
      elif o == "--authtype":
        cfg["authtype"] = a
      elif o == "--pac":
        cfg["pac"] = a
      elif o == "--expect":
        cfg["expect"] = a
      elif o == "--warntime":
        cfg["warntime"] = a
      elif o == "--timeout":
        cfg["timeout"] = a
      elif o == "--myip":
        cfg["myip"] = a
      elif o == "--auth":
        cfg["auth"] = a
      elif o == "--pauth":
        cfg["pauth"] = a
      elif o == "--debug":
        cfg["debug"] = 1
    for req_param in ("url", "pac", "expect"):
      if req_param not in cfg:
        raise Exception("Missing Parameter" + req_param)
    status = check(cfg)
    sys.exit(status)


