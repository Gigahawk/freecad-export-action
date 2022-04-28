#!/bin/bash

# Using argparse with FreeCADCmd seems to cause issues, store inputs as
# environment variables instead
export FREECAD_INPUT_PATHS=$1
export FREECAD_OUTPUT_PATH=$2
export FREECAD_EXPORT_TYPES=$3

echo "Running export script"
xvfb-run FreeCADCmd /export.py