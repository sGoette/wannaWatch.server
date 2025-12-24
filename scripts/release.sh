#!/bin/sh
set -e

VERSION="$1"

if [ -z "$VERSION" ]; then
  echo "Usage: ./scripts/release.sh v0.1.0"
  exit 1
fi

echo "🚀 Building release $VERSION"

rm -rf dist
npm run build

RELEASE_DIR="$VERSION"
ARCHIVE_NAME="wannawatchserver-$VERSION.tar.gz"

rm -rf "$RELEASE_DIR"
mkdir "$RELEASE_DIR"

cp -r dist/* "$RELEASE_DIR/"

tar -czf "$ARCHIVE_NAME" "$RELEASE_DIR"

rm -rf "$RELEASE_DIR"

echo "✅ Created $ARCHIVE_NAME"
