#!/usr/bin/env python3
'''
Wikidata
'''
import logging
import os
import time
import urllib
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
    while True:
        try:
            return wd_sparql.queryAndConvert()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                delay = int(e.headers['retry-after'])
                logging.warn('Too many requests. Retrying in %d seconds...', delay)
                time.sleep(delay)
            else:
                raise e

def wd_labels(uri, langs):
    if not isinstance(langs, list): langs = [langs]
    filters = ' || '.join('langMatches(lang(?label), "' + lang + '")' for lang in langs)
    res = wd_query('SELECT DISTINCT ?label {<' + uri + '> rdfs:label ?label. FILTER(' + filters + ')}')
    # FIXME return languages too
    return [binding['label']['value'] for binding in res['results']['bindings']]

def wd_classes(uri):
    res = wd_query('SELECT ?class (sample(?labels) as ?label) {{SELECT DISTINCT ?class ?labels {<' + uri + '> <http://www.wikidata.org/prop/direct/P31> ?class OPTIONAL {?class rdfs:label ?labels FILTER(langMatches(lang(?labels), "en"))}}}} GROUP BY ?class')
    return [{'class': b['class']['value'], 'label': b['label']['value'] if 'label' in b else None} for b in res['results']['bindings']]
