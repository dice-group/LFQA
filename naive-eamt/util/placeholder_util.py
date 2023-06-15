'''
This python encapsulates the functions to deal with placeholders in the annotated natural language text.
'''
import logging
from string import Template
import cache_util
from SPARQLWrapper import SPARQLWrapper, JSON

SPARQL_LANG_MAP = {
    'en': 'EN',
    'de': 'DE',
    'ru': 'RU',
    'fr': 'FR',
    'es': 'ES',
    'pt': 'PT',
    'it': 'IT'
}

sparql_wd = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql_wd.setReturnFormat(JSON)

sparql_db = SPARQLWrapper("https://dbpedia.org/sparql")
sparql_db.setReturnFormat(JSON)

sparql_swc = SPARQLWrapper("https://porque-dev.poolparty.biz/PoolParty/sparql/WaffenRecht")
sparql_swc.setReturnFormat(JSON)

WD_QUERY_STR = '''
    SELECT ?enlbl WHERE {
        
        OPTIONAL {
            wd:$link rdfs:label ?enlbl .
            FILTER (langMatches( lang(?enlbl), "$lang" ) )
        }
        OPTIONAL {
            wd:$link rdfs:label ?enlbl .
            FILTER (langMatches( lang(?enlbl), "EN" ) )
        }
    } 
    LIMIT 1
'''

'''
The reason behind the usage of owl:sameAs in the DBpedia is the MAG tool. 
Mag returns language specific DBpedia URIs.
'''

DBP_QUERY_STR = '''
    PREFIX owl:<http://www.w3.org/2002/07/owl#>
    SELECT ?enlbl WHERE {
    
        OPTIONAL {
            <$link> rdfs:label ?enlbl .
            FILTER (langMatches( lang(?enlbl), "$lang" ) )
        }
        OPTIONAL {
            <$link> rdfs:label ?enlbl .
            FILTER (langMatches( lang(?enlbl), "EN" ) )
        }
        OPTIONAL {
            ?sub rdfs:label ?enlbl .
            ?sub owl:sameAs <$link> .
            FILTER (langMatches( lang(?enlbl), "$lang" ) )
        }
        OPTIONAL {
            ?sub rdfs:label ?enlbl .
            ?sub owl:sameAs <$link> .
            FILTER (langMatches( lang(?enlbl), "EN" ) )
        }
    } 
    LIMIT 1
'''

SWC_QUERY_STR =  '''
    PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
    SELECT ?enlbl WHERE {
      
        OPTIONAL {
            <$link> skos:prefLabel ?enlbl .
            FILTER (langMatches( lang(?enlbl), "$lang" ) )
        }
        OPTIONAL {
            <$link> skos:prefLabel ?enlbl .
            FILTER (langMatches( lang(?enlbl), "EN" ) )
        }
    }
    LIMIT 1
'''

kb_info = {
    'wd': (sparql_wd, Template(WD_QUERY_STR)),
    'dbp': (sparql_db, Template(DBP_QUERY_STR)),
    'swc': (sparql_swc, Template(SWC_QUERY_STR))
}

def put_placeholders(query, plc_token, replace_before, target_lang, kb, ent_links, cur_stats):
    '''
    This method expects the input format as stated in the README for EL output

    :param cur_stats: object with placeholder statistics for the current query
    :param query: natural language query to put placeholders into
    :param plc_token: placeholder prefix to use
    :param replace_before: whether to replace the placeholders with their labels before translation
    :param target_lang: target language ISO code
    :param ent_links: entity annotations and links for the query
    :param kb: knowledge-base that the entities are linked to. Can only handle Wikidata and DBpedia for now
    :return: text with placeholders.
    '''

    ret_tuple = (query, ent_links, cur_stats)
    # Maintain translated placeholder count
    plc_count = cur_stats['placeholder_count']
    en_count = cur_stats['english_label_count']

    if target_lang in SPARQL_LANG_MAP:
        target_lang = SPARQL_LANG_MAP[target_lang]
    else:
        target_lang = "EN"
    if not kb:
        logging.debug('No KB information found in the input.')
        return ret_tuple
    arr_ind = 1

    query_plc = ''
    last_ind = 0
    for mention_item in ent_links:
        if 'link' not in mention_item:
            continue
        # sleep the thread to avoid spamming SPARQL endpoint
        # time.sleep(2)
        # ret = compose_execute_sparql(kb, mention_item['link'], target_lang)
        ret = cache_util.call(compose_execute_sparql, 'compose_execute_sparql', kb, mention_item['link'], target_lang)
        logging.debug('SPARQL results:\n %s' % str(ret))
        # Check if no results are retrieved
        # Empty results can look like this: {'head': {'vars': ['enlbl']}, 'results': {'bindings': [{}]}}
        if len(ret["results"]["bindings"]) == 0 or (len(ret["results"]["bindings"]) == 1 and len(ret["results"]["bindings"][0]) == 0):
            ret["results"]["bindings"] = []
            en_count['not_found'] += 1
        # extracting English label
        eng_label = None
        for r in ret["results"]["bindings"]:
            mention_item['en_label'] = r['enlbl']['value']
            eng_label = mention_item['en_label']
            en_count['total_found'] += 1
            break
        if replace_before:
            plchldr = eng_label
        else:
            plchldr = '[%s%d]' % (plc_token, arr_ind)
            mention_item['placeholder'] = plchldr
            # incrementing global placeholder count
            plc_count['total'] += 1
        # forming the placeholder query
        if plchldr:
            query_plc += query[last_ind:mention_item['start']] + plchldr
            arr_ind += 1
            last_ind = mention_item['end']
    query_plc += query[last_ind:]
    # Do not change the return logic, a single object is required for caching
    ret_tuple = (query_plc, ent_links, cur_stats)
    return ret_tuple

def compose_execute_sparql(kb, link, target_lang):
    sparql = kb_info[kb][0]
    sparql_str = kb_info[kb][1]
    f_sparql = sparql_str.substitute(link=link, lang=target_lang)
    sparql.setQuery(f_sparql)
    logging.debug('Formed SPARQL:\n %s' % f_sparql)
    return sparql.queryAndConvert()



def replace_placeholders(trans_text, replace_before, ent_links, cur_stats):
    '''
    This function replaces the placeholders in the translated text with their corresponding English labels.

    :param cur_stats: object with placeholder statistics for the current query
    :param trans_text: translated English text with placeholders
    :param replace_before: flag with the value for replace placeholder before translation option
    :param ent_links: all the entity mentions in the query
    :return: translated string with replaced placeholders
    '''
    # Maintain translated placeholder count
    plc_count = cur_stats['placeholder_count']
    en_count = cur_stats['english_label_count']

    res_query = trans_text
    for link in ent_links:
        if 'link' not in link:
            continue
        label = link['surface_form']
        if 'en_label' in link:
            label = link['en_label']
            # record label stats if replaced before
            if replace_before and (label.casefold() in trans_text.casefold()):
                en_count['trans_copied'] += 1
        # check the number of properly translated placeholders
        if (not replace_before) and (link['placeholder'] in res_query):
            plc_count['translated'] += 1
            res_query = res_query.replace(link['placeholder'], label)
    logging.debug('Query after replaced placeholder: %s' % res_query)
    return res_query, cur_stats

def fetch_placeholder_str(query, plc_token, ent_links):
    arr_ind = 1
    query_plc = ''
    last_ind = 0
    for link in ent_links:
        if 'link' not in link:
            continue
        plchldr = '[%s%d]' % (plc_token, arr_ind)
        link['placeholder'] = plchldr
        # forming the placeholder query
        if plchldr:
            query_plc += query[last_ind:link['start']] + plchldr
            arr_ind += 1
            last_ind = link['end']
    query_plc += query[last_ind:]
    return query_plc
