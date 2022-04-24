from elasticsearch import Elasticsearch
import elasticsearch.client
import json
import argparse
import sys

def comma_list(string):
    return [e.strip() for e in string.split(',')]

parser = argparse.ArgumentParser(description='EQL Interface for Elasticsearch')

parser.add_argument('--eql', help='EQL to search for')
parser.add_argument('--index', default="logs*", help='Target index')
parser.add_argument('--size', default=None, help='Maximum number of responded documents')
parser.add_argument('--columns', default=[], type=comma_list, help='Filters the column names of the output')
parser.add_argument('--check', default=False, action="store_true", help='Target index')
parser.add_argument('--config', default="config.json", help='Path of the config file')

args = parser.parse_args()

def to_csv(data: list):
    return ",".join(data)

def values_to_row(args):
    row = []

    for filt in args.columns:
        try:
            res = data

            for filt_part in filt.split("."):
                res = res[filt_part]

            row.append(res)
        except KeyError:
            # print("Field not found")
            continue

    return row

def search(eql_cli, args):
    if args.size != None:
        res = eql_cli.search(
            index=args.index,
            query=args.eql,
            size=args.size,
        )
    else:
        res = eql_cli.search(
            index=args.index,
            query=args.eql,
        )

    return res


config = {}
with open(args.config, "r") as f:
    config = json.load(f)

es = Elasticsearch(config["elastic_url"], api_key=config["api_key"], ssl_assert_fingerprint=config["tls_fingerprint"])

if args.check:
    print(es.info())
    sys.exit()

eql_cli = elasticsearch.client.EqlClient(es)

search_result = search(eql_cli, args)

if args.columns != []:
    print(to_csv(args.columns))

for entry in search_result["hits"]["events"]:
    data = entry["_source"]

    if args.columns != []:
        row = values_to_row(args)

        print(to_csv(row))
    else:
        print(json.dumps(data, indent=4))

