#! /bin/bash

FILE="$1"

if [ -z "$FILE" ] ; then

    root -l PMT_scan.C\(0\)
else

    root -l PMT_scan.C\(\"$FILE\"\)
fi
