#!/bin/bash
rm -rf vendored
rm -rf ../es.zip
mkdir -p vendored
pip install -r vendored_requirements.txt -t ./vendored
zip -X -r ../es.zip ./
