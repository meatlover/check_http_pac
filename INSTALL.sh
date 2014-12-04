#!/bin/bash
#
# Prerequisite: Python 2.7+ 
#

my_pwd=$(pwd)

# Step 1: Install linux enterprise repository
yum install epel-release
if [[ $(yum repolist) == *metalink* ]];
  then
    echo "-- Warning: epel repository might not be accessible."
    echo "   Please consider run the following command to fix if you know what it means:"
    echo "   sudo sed -i \"s/mirrorlist=https/mirrorlist=http/\" /etc/yum.repos.d/epel.repo"
    read -p "-- Please continue after fix this issue. Continue? [y/n]" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
fi

# Step 2: Install pip package management tool
yum install python-pip

# Step 3: Install python requests module
pip install requests

# Step 4: Install python Requests-NTLM module
pip install requests-ntlm

# Step 5: Install python pacparser module
tar -zxf pacparser*.tar.gz
cd pacparser*
make -C src pymod
sudo make -C src install-pymod
cd ..

# Step 6: Create soft link from check_http_ script files to Nagios libexec folder
if ! [ -e /etc/init.d/nagios ]; then
  echo "-- Error: Cannot find Nagios init script. "
  echo "   Please consider make check_http_* scripts available to Nagios manually."
  exit
fi


nagiosPath=$(cat /etc/init.d/nagios | grep ^prefix=)
nagiosPath=${nagiosPath/prefix=/}/libexec/
pacScriptPath=$nagiosPath"check_http_pac"
proxyScriptPath=$nagiosPath"check_http_proxy"
if [ -h $pacScriptPath ]; then
  echo $pacScriptPath "already exists."
else
  ln -sv $(pwd)/check_http_pac.py $pacScriptPath
fi

if [ -h $proxyScriptPath ]; then
  echo $proxyScriptPath "already exists."
else
  ln -sv $(pwd)/check_http_proxy.py $proxyScriptPath
fi

echo "Script installation completed."

