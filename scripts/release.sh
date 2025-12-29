#!/bin/sh
set -e

VERSION="$1"

if [ -z "$VERSION" ]; then
  echo "Usage: ./scripts/release.sh v0.1.0"
  exit 1
fi

echo "🚀 Building release $VERSION"

BUILD_DIR="build"
RELEASE_DIR="wannawatchserver-$VERSION"
ARCHIVE_NAME="$RELEASE_DIR.tar.gz"


rm -rf "$BUILD_DIR" "$RELEASE_DIR"
mkdir -p "$BUILD_DIR"
mkdir -p "$RELEASE_DIR"

npm run build

mkdir -p "$RELEASE_DIR/backend"
rsync -a \
  --exclude ".venv" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude ".pytest_cache" \
  --exclude ".mypy_cache" \
  --exclude ".ruff_cache" \
  --exclude ".DS_Store" \
  backend/ "$RELEASE_DIR/backend/"

mkdir -p "$RELEASE_DIR/frontend"
rsync -a \
  --exclude "node_modules" \
  --exclude ".DS_Store" \
  dist/frontend/ "$RELEASE_DIR/frontend/"

if [ ! -f "$RELEASE_DIR/frontend/index.html" ]; then
  echo "❌ frontend/index.html not found in release output."
  echo "   Adjust your frontend build output path or update the rsync source."
  exit 1
fi

tar -czf $BUILD_DIR/"$ARCHIVE_NAME" "$RELEASE_DIR"

rm -rf "$RELEASE_DIR"

echo "✅ Created $BUILD_DIR/$ARCHIVE_NAME"