from elasticsearch import Elasticsearch
import elasticsearch.client
import json
import argparse
import sys

def comma_list(string):
    return [e.strip() for e in string.split(',')]

parser = argparse.ArgumentParser(description='EQL Interface for Elasticsearch')

parser.add_argument('--index', default="logs*", help='Target index')
parser.add_argument('--size', default=10, type=int, help='Maximum number of responded documents')
parser.add_argument('--columns', default=[], type=comma_list, help='Filters the column names of the output')
parser.add_argument('--check', default=False, action="store_true", help='Target index')
parser.add_argument('--config', default="config.json", help='Path of the config file')
parser.add_argument('--csv-separator', default=",", help='Sets the separator for the csv output')


subparsers = parser.add_subparsers(dest="subparser", help='sub-command help')
parser_eql = subparsers.add_parser('eql', help='Parses EQL queries')
parser_eql.add_argument("eql", help="Takes the EQL query")

parser_kql = subparsers.add_parser('kql', help='Parses KQL queries')
parser_kql.add_argument("kql", help="Takes the KQL query")

args = parser.parse_args()


class KQL:

    def __init__(self, config):
        self.config = config
        self.es = Elasticsearch(config["elastic_url"], api_key=config["api_key"], ssl_assert_fingerprint=config["tls_fingerprint"])


    def search(self, index: str, kql: str, size: int = 10):
        query_body = {
             "query_string": {
                 "query": kql,
                 "default_field" : "*"
             }
        }

        results = self.es.search(index=index, query=query_body)

        return Results(results["hits"]["hits"])


class EQL:

    def __init__(self, config):
        self.es = Elasticsearch(config["elastic_url"], api_key=config["api_key"], ssl_assert_fingerprint=config["tls_fingerprint"])
        self.eql_client = elasticsearch.client.EqlClient(es)

    def search(self, index: str, eql_string: str, size: int = 10):
        results = self.eql_client.search(index=index, query=eql_string, size=size)

        return Results(results["hits"]["events"])


class Results:

    def __init__(self, results):
        self.data = results

    def print_csv(self):
        pass

    def keys(self, filter_paths: list):
        result = []

        for dat in self.data:
            row = []

            for filt in filter_paths:
                try:
                    res = dat["_source"]

                    for filt_part in filt.split("."):
                        res = res[filt_part]

                    row.append(res)
                except KeyError:
                    # print("Field not found")
                    continue
            result.append(row)

        return result

    def __str__(self):
        return json.dumps(self.data, indent=4)


config = {}
with open(args.config, "r") as f:
    config = json.load(f)

es = Elasticsearch(config["elastic_url"], api_key=config["api_key"], ssl_assert_fingerprint=config["tls_fingerprint"])

if args.check:
    print(es.info())
    sys.exit()


if args.subparser == "eql":
    eql = EQL(config)
    res = eql.search(args.index, args.eql, args.size)

elif args.subparser == "kql":
    kql = KQL(config)
    res = kql.search(args.index, args.kql, args.size)

else:
    args.print_help()


if args.columns:
    #print(res.data)
    for row in res.keys(args.columns):
        print(args.csv_separator.join(row))

else:
    print(res)
