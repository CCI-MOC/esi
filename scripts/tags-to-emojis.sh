#!/bin/sh

sed '
s/\[s]/😀/g
s/\[u]/🙂/g
s/\[r]/🤔/g
s/\[f]/😬/g
' "$@"
