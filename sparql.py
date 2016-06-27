#!/usr/bin/env python

import urllib
import requests
import sys
import os
import StringIO
import types

class URI(object):

    def __init__(self, uri):
        self.uri = uri

    def __str__(self):
        return self.uri

class Results(object):

    def __init__(self, variables, values):
        self.variables = variables
        self.values = values

    def __str__(self):
        out = StringIO.StringIO()
        pretty_print_results(out, self)
        return out.getvalue()

    def output(self, out, max_width=None, column_widths=None):
        pretty_print_results(out, self, max_width, column_widths)

    def column_width(self, var):
        width = len(var)
        for row in self.values:
            if row[var] == None:
                val = ""
            else:
                val = str(row[var])
            if len(val) > width:
                width = len(val)
        return width

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

    results = r.json()

    vars = results["head"]["vars"]

    objects = []
    for row in results["results"]["bindings"]:
        obj = {}
        for var in vars:
            val = None
            if row[var]["type"] == "uri":
                val = URI(row[var]["value"])
            elif row[var]["type"] == "literal":
                if row[var].has_key("datatype"):
                    dt = row[var]["datatype"]
                    if dt == "http://www.w3.org/2001/XMLSchema#integer":
                        val = int(row[var]["value"])
                    else:
                        val = row[var]["value"]
                else:
                    val = row[var]["value"]
            else:
                val = "unknown"
            obj[var] = val
        objects.append(obj)

    return Results(vars, objects)

def pretty_print_results(output, res, max_width=None, column_widths=None):

    vars = res.variables

    columns = {}

    for var in vars:
        if column_widths != None and column_widths.has_key(var):
    	    columns[var] = column_widths[var]
        else:
            columns[var] = res.column_width(var)

    if max_width != None:

        content = 0
        overheads = 1
        for var in vars:
            overheads = overheads + 3
            content = content + columns[var]

        if (overheads + content) > max_width:
            remain = max_width - overheads

        for var in vars:
            columns[var] = int(columns[var] * remain / content)

    for var in vars:
        output.write("+-");
        for i in range(columns[var]):
            output.write("-")
        output.write("-");
    output.write("+\n");

    for var in vars:
        output.write("| ");
        output.write(("%-" + str(columns[var]) + "s") % var[0:columns[var]])
        output.write(" ");
    output.write("|\n");

    for var in vars:
        output.write("+-");
        for i in range(columns[var]):
            output.write("-")
        output.write("-");
    output.write("+\n");

    for row in res.values:
        for var in vars:
            if row[var] != None:
                value = str(row[var])
            else:
                value = ""
            if len(value) > columns[var]:
                value = value[0:columns[var]]
            output.write("| ");
            output.write(("%-" + str(columns[var]) + "s") % value);
            output.write(" ");
        output.write("|\n");

    for var in vars:
        output.write("+-");
        for i in range(columns[var]):
            output.write("-")
        output.write("-");
    output.write("+\n");

def default_endpoint():
    ep = os.getenv("SPARQL_ENDPOINT")
    if ep == None:
        raise RuntimeError, "SPARQL_ENDPOINT does not define an endpoint"
    return ep

