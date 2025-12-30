#Create jail. Do via UI if possible
iocage create \
  -n wmserver \
  -r 13.2-RELEASE \
  ip4.addr="vnet0|192.168.1.50/24" \
  defaultrouter="192.168.1.1" \
  boot=on

#Base package inside the jail
pkg update

#make directories
cd /usr/local
mkdir -p wannawatch.server/{releases,data,logs}
mkdir -p wannawatch.server/data/{db,thumbnails}

#create user
pw useradd wannawatchserver -m -s /usr/sbin/nologin
chown -R wannawatchserver:wannawatchserver wannawatch.server

#Download version from github
cd /usr/local/wannawatch.server/releases
fetch https://github.com/sGoette/wannaWatch.server/releases/download/v0.1.0/wannawatchserver-v0.1.0.tar.gz
tar -xzf wannawatchserver-v0.1.0.tar.gz

#Activate release
ln -sfn /usr/local/wannawatch.server/releases/v0.1.0 /usr/local/wannawatch.server/current
chown -h wannawatchserver:wannawatchserver /usr/local/wannawatch.server/current

#run by hand
cd /usr/local/wannawatch.server/current
su -m wannawatchserver -c "node /usr/local/wannawatch.server/current/backend/server.js"

#set port forwarding in host
sysrc pf_enable=YES
nano /etc/pf.conf
rdr pass on igc0 proto tcp from any to 192.168.1.181 port 80 -> 192.168.1.181 port 4000 #wird ins file pf.conf geschrieben
pfctl -f /etc/pf.conf
service pf start

#update
cd /usr/local/wannawatch.server/releases
fetch https://github.com/sGoette/wannaWatch.server/releases/download/v0.1.11/wannawatchserver-v0.1.11.tar.gz
tar -xzf wannawatchserver-v0.1.11.tar.gz
ln -sfn /usr/local/wannawatch.server/releases/v0.1.11 /usr/local/wannawatch.server/current
chown -h wannawatchserver:wannawatchserver /usr/local/wannawatch.server/current




# PYTHON Version of install.....
cd /usr/local/wannawatch.server/releases
fetch https://github.com/sGoette/wannaWatch.server/releases/download/v0.1.17/wannawatchserver-v0.1.17.tar.gz
tar -xzf wannawatchserver-v0.1.17.tar.gz
cd /usr/local/wannawatch.server/releases/v0.1.17
sh install.sh