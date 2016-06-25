#!/usr/bin/env python

import urllib
import requests
import sys
import os

def execute_query(url, query):

    # Encode SPARQL query for URL
    params = urllib.urlencode({"query": query, "output": "json"})
 
    # Create URL
    url = url + "?" + params

    # HTTP request
    import requests
    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError, "SPARQL query failed"

    return r.json()

def pretty_print_results(res, max_column=999):

    vars = res["head"]["vars"]

    column_size = {}
    for var in vars:
        if len(var) > max_column:
            column_size[var] = max_column
        else:
    	    column_size[var] = len(var)
    	
    for row in res["results"]["bindings"]:
    	for var in vars:
            if  row[var].has_key("value") and not row[var]["value"] == None:
	        if len(row[var]["value"]) > column_size[var]:
	            column_size[var] = len(row[var]["value"])
                    if column_size[var] > max_column:
                        column_size[var] = max_column

    for var in vars:
        sys.stdout.write("+-");
        for i in range(column_size[var]):
            sys.stdout.write("-")
        sys.stdout.write("-");
    sys.stdout.write("+\n");

    for var in vars:
        sys.stdout.write("| ");
        sys.stdout.write(("%-" + str(column_size[var]) + "s") % var);
        sys.stdout.write(" ");
    sys.stdout.write("|\n");

    for var in vars:
        sys.stdout.write("+-");
        for i in range(column_size[var]):
            sys.stdout.write("-")
        sys.stdout.write("-");
    sys.stdout.write("+\n");

    for row in res["results"]["bindings"]:
        for var in vars:
            if row[var].has_key("value") and row[var]["value"] != None:
                value = row[var]["value"]
            else:
                value = ""
            if len(value) > max_column:
                value = value[0:max_column]
            sys.stdout.write("| ");
            sys.stdout.write(("%-" + str(column_size[var]) + "s") % value);
            sys.stdout.write(" ");
        sys.stdout.write("|\n");

    for var in vars:
        sys.stdout.write("+-");
        for i in range(column_size[var]):
            sys.stdout.write("-")
        sys.stdout.write("-");
    sys.stdout.write("+\n");

def default_endpoint():
    ep = os.getenv("SPARQL_ENDPOINT")
    if ep == None:
        raise RuntimeError, "SPARQL_ENDPOINT does not define an endpoint"
    return ep

