#!/usr/bin/env bash
# Export the static site into the sibling GitHub Pages repository.
#
# Copies only browser assets from the selected committed tree. The destination
# folder is replaced wholesale so removed artwork is removed from the export.
# Nothing is committed or pushed in the Pages repository.
#
# Usage: ./export-site.sh [git-ref]      (default: HEAD)
#        PAGES_DIR=/path/to/pages ./export-site.sh

set -euo pipefail

cd "$(dirname "$0")"

ref="${1:-HEAD}"
pages_dir="${PAGES_DIR:-../pakfront.github.io}"
target="$pages_dir/paper-army-standees"
paths=(index.html src vendor artwork)

if [ ! -d "$pages_dir/.git" ]; then
    echo "Error: $pages_dir is not a git repository" >&2
    exit 1
fi

if [ "$ref" = HEAD ] && [ -n "$(git status --porcelain -- "${paths[@]}")" ]; then
    echo "Warning: uncommitted changes in site files are not exported" >&2
fi

sha="$(git rev-parse --short "$ref")"
staging="$(mktemp -d)"
trap 'rm -rf "$staging"' EXIT

git archive "$ref" -- "${paths[@]}" | tar -x -C "$staging"
echo "$ref $sha" > "$staging/version.txt"
# The Pages repository tracks PNGs with Git LFS globally. Static hosts serve
# LFS pointer text instead of image bytes, so opt this app folder out of LFS.
cat > "$staging/.gitattributes" <<'ATTRIBUTES'
*.png -filter -diff -merge
ATTRIBUTES

rm -rf "$target"
mkdir -p "$target"
cp -a "$staging"/. "$target"/

echo "Exported $ref ($sha) to $target"
echo "Review and publish with: git -C $pages_dir add paper-army-standees && git -C $pages_dir commit && git -C $pages_dir push"
