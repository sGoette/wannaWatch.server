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
fetch https://github.com/sGoette/wannaWatch.server/releases/download/v0.1.18/wannawatchserver-v0.1.18.tar.gz
tar -xzf wannawatchserver-v0.1.18.tar.gz
cd /usr/local/wannawatch.server/releases/v0.1.18
sh install.sh





ps auxww






/usr/sbin/daemon -p /usr/local/wannawatch.server/wannawatch.pid -o /usr/local/wannawatch.server/logs/wannawatch.log /usr/bin/su -m wannawatchserver -c "/usr/local/bin/python3 -m uvicorn app.main:app --app-dir /usr/local/wannawatch.server/current/backend --host 0.0.0.0 --port 4000"



/usr/local/bin/python3 -m uvicorn app.main:app --app-dir /usr/local/wannawatch.server/current/backend --host 0.0.0.0 --port 4000

su -m wannawatchserver -c "touch /usr/local/wannawatch.server/logs/test.log && echo ok >> /usr/local/wannawatch.server/logs/test.log"
su -m wannawatchserver -c "touch /usr/local/wannawatch.server/wannawatch.pid"


chown -R wannawatchserver /usr/local/wannawatch.server/logs
chown wannawatchserver /usr/local/wannawatch.server/wannawatch.pid 2>/dev/null || true
chmod 755 /usr/local/wannawatch.server
chmod 755 /usr/local/wannawatch.server/logs

/usr/bin/su -m wannawatchserver -c "/usr/local/bin/python3 -m uvicorn app.main:app --app-dir /usr/local/wannawatch.server/current/backend --host 0.0.0.0 --port 4000"

/usr/sbin/daemon -f -o /tmp/wannawatch.daemon.test.log /usr/bin/su -m wannawatchserver -c "/usr/local/bin/python3 -m uvicorn app.main:app --app-dir /usr/local/wannawatch.server/current/backend --host 0.0.0.0 --port 4000"


rm -f /usr/local/wannawatch.server/wannawatch.pid
