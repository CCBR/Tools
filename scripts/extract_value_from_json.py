#!/usr/bin/env python
import json
import argparse

parser = argparse.ArgumentParser(description="extract value for key from JSON")
parser.add_argument("-j", dest="json", required=True, help="input JSON file")
parser.add_argument(
    "-k", dest="key", required=True, help="key whose value is to be extracted"
)
args = parser.parse_args()
data = json.load(open(args.json))
print(data[args.key])
