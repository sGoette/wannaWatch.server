#!/bin/sh

VERSION="$1"

if [ -z "$VERSION" ]; then
  echo "Usage: update.sh v0.1.0"
  exit 1
fi

cd /usr/local/wannawatch.server/releases
fetch https://github.com/sGoette/wannaWatch.server/releases/download/$VERSION/wannawatchserver-$VERSION.tar.gz
tar -xzf wannawatchserver-$VERSION.tar.gz
cd /usr/local/wannawatch.server/releases/$VERSION
sh install.sh