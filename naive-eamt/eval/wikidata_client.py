#!/usr/bin/env python3
'''
Wikidata
'''
import os
import SPARQLWrapper

wd_sparql = None
def wd_query(query):
    'Run the query and return results'
    global wd_sparql
    if wd_sparql is None:
        wd_sparql = SPARQLWrapper.SPARQLWrapper('https://query.wikidata.org/bigdata/namespace/wdq/sparql')
        wd_sparql.setReturnFormat(SPARQLWrapper.JSON)
        if ua := os.getenv('WD_USER_AGENT'):
            wd_sparql.agent = str({'User-Agent': ua})
    wd_sparql.setQuery(query)
    return wd_sparql.queryAndConvert()

def wd_labels(uri, langs):
    if not isinstance(langs, list): langs = [langs]
    filters = ' || '.join('langMatches(lang(?label), "' + lang + '")' for lang in langs)
    res = wd_query('SELECT DISTINCT ?label {<' + uri + '> rdfs:label ?label. FILTER(' + filters + ')}')
    # FIXME return languages too
    return [binding['label']['value'] for binding in res['results']['bindings']]
