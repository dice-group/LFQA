'''
This python encapsulates the functions to deal with placeholders in the annotated natural language text.
'''
import logging
import time
import stats_util

from SPARQLWrapper import SPARQLWrapper, JSON

sparql_wd = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql_wd.setReturnFormat(JSON)

sparql_db = SPARQLWrapper("https://dbpedia.org/sparql")
sparql_db.setReturnFormat(JSON)

sparql_swc = SPARQLWrapper("https://porque-dev.poolparty.biz/PoolParty/sparql/WaffenRecht")
sparql_swc.setReturnFormat(JSON)

kb_info = {
    'wd': (sparql_wd,
           '''
            SELECT ?enlbl WHERE {
                wd:%s rdfs:label ?enlbl .
                FILTER (langMatches( lang(?enlbl), "EN" ) )
            } 
            LIMIT 1
            '''),
    'dbp': (sparql_db,
            '''
            PREFIX owl:<http://www.w3.org/2002/07/owl#>
            SELECT ?enlbl WHERE {
                ?sub rdfs:label ?enlbl .
                ?sub owl:sameAs <%s> .
                FILTER (langMatches( lang(?enlbl), "EN" ) )
            } 
            LIMIT 1
            '''),
    'swc': (sparql_swc,
            '''
            PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
            SELECT ?enlbl WHERE {
              <%s> skos:prefLabel ?enlbl .
              FILTER (langMatches ( lang(?enlbl), "EN"))
            }
            LIMIT 1
            ''')
}


def put_placeholders(input):
    '''
    This method expects the input format as stated in the README for EL output

    :param input: input dictionary containing text and its entity annotations + links
    :param kb: knowledge-base that the entities are linked to. Can only handle Wikidata and DBpedia for now
    :return: input dictionary with append key-value pair mapping 'text_plc' to the text with placeholders.
    '''
    # Maintain translated placeholder count
    stats_lock = stats_util.lock
    plc_count = stats_util.stats['placeholder_count']
    en_count = stats_util.stats['english_label_count']
    query = input['text']
    plc_token = input['placeholder']
    replace_before = input['replace_before']
    if 'kb' not in input:
        logging.debug('No KB information found in the input.')
        input['text_plc'] = query
        return input
    kb = input['kb']
    ent_links = input['ent_mentions']
    arr_ind = 1
    sparql = kb_info[kb][0]
    sparql_str = kb_info[kb][1]

    query_plc = ''
    last_ind = 0
    for link in ent_links:
        if 'link' not in link:
            continue
        # sleep the thread to avoid spamming SPARQL endpoint
        # time.sleep(2)
        f_sparql = sparql_str % link['link']
        sparql.setQuery(f_sparql)
        logging.debug('Formed SPARQL:\n %s' % f_sparql)
        ret = sparql.queryAndConvert()
        # Check if no results are retrieved
        if len(ret["results"]["bindings"]) == 0:
            stats_lock.acquire()
            en_count['not_found'] += 1
            stats_lock.release()
        # extracting English label
        eng_label = None
        for r in ret["results"]["bindings"]:
            link['en_label'] = r['enlbl']['value']
            eng_label = link['en_label']
            stats_lock.acquire()
            en_count['total_found'] += 1
            stats_lock.release()
            break
        if replace_before:
            plchldr = eng_label
        else:
            plchldr = '[%s%d]' % (plc_token, arr_ind)
            link['placeholder'] = plchldr
            # incrementing global placeholder count
            stats_lock.acquire()
            plc_count['total'] += 1
            stats_lock.release()
        # forming the placeholder query
        if plchldr:
            query_plc += query[last_ind:link['start']] + plchldr
            arr_ind += 1
            last_ind = link['end']
    query_plc += query[last_ind:]
    input['text_plc'] = query_plc
    logging.debug('Injected placeholders: %s' % input)
    return input


def replace_placeholders(trans_text, input):
    '''
    This function replaces the placeholders in the translated text with their corresponding English labels.

    :param trans_text: translated English text with placeholders
    :param input: input dictionary with details about mentions and placeholders + links
    :return: translated string with replaced placeholders
    '''
    # Maintain translated placeholder count
    stats_lock = stats_util.lock
    plc_count = stats_util.stats['placeholder_count']
    en_count = stats_util.stats['english_label_count']
    replace_before = input['replace_before']

    res_query = trans_text
    ent_links = input['ent_mentions']
    for link in ent_links:
        if 'link' not in link:
            continue
        label = link['surface_form']
        if 'en_label' in link:
            label = link['en_label']
            # record label stats if replaced before
            if replace_before and (label.casefold() in trans_text.casefold()):
                stats_lock.acquire()
                en_count['trans_copied'] += 1
                stats_lock.release()
        # check the number of properly translated placeholders
        if (not replace_before) and (link['placeholder'] in res_query):
            stats_lock.acquire()
            plc_count['translated'] += 1
            stats_lock.release()
            res_query = res_query.replace(link['placeholder'], label)
    logging.debug('Query after replaced placeholder: %s' % res_query)
    logging.debug('Stats: %s' % stats_util.stats)
    return res_query
