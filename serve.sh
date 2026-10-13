#!/bin/sh
# Run the local workshop server. Arguments are passed to serve.py.
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$script_dir/serve.py" "$@"
