import yaml
import argparse

parser = argparse.ArgumentParser(description="extract value for key from YAML")
parser.add_argument("-y", dest="yaml", required=True, help="input YAML file")
parser.add_argument(
    "-k", dest="key", required=True, help="key whose value is to be extracted"
)
args = parser.parse_args()
data = yaml.safe_load(open(args.yaml))
print(data[args.key])
