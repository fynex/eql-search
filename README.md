# eql-search

Searches via EQL (Event Query Language) in an elasticsearch instance to find documents with an advanced syntax.

Elastic Syntax: https://www.elastic.co/guide/en/elasticsearch/reference/current/eql-syntax.html

Syntax: https://readthedocs.org/projects/eql/downloads/pdf/latest/

Definition of EQL
> EQL is a language that can match events, generate sequences, stack data, build aggregations, and perform analysis.
> EQL is schemaless and supports multiple database backends. It supports field lookups, boolean logic, comparisons,
> wildcard matching, and function calls. EQL also has a preprocessor that can perform parse and translation time
> evaluation, allowing for easily sharable components between queries.

# Prerequisites

```
pip install elasticsearch 
```

# Usage

```bash
python main.py --size 3 --columns 'process.name, process.command_line, process.parent.name, host.name' --eql '
process where process.name == "sh"
'
```

```
process.name,process.command_line,process.parent.name,host.name
sh,/bin/sh -c iptables -w -I f2b-sshd 1 -s 127.0.0.1 -j REJECT --reject-with icmp-port-unreachable,python3.8,localhost
sh,/bin/sh -c iptables -w -I f2b-sshd 1 -s 127.0.0.1 -j REJECT --reject-with icmp-port-unreachable,sh,localhost
sh,/bin/sh -c iptables -w -I f2b-sshd 1 -s 127.0.0.1 -j REJECT --reject-with icmp-port-unreachable,python3.8,localhost
```
