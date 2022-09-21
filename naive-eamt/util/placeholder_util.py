'''
This python encapsulates the functions to deal with placeholders in the annotated natural language text.
'''
import logging
import time

from SPARQLWrapper import SPARQLWrapper, JSON

sparql_wd = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql_wd.setReturnFormat(JSON)

sparql_db = SPARQLWrapper("https://dbpedia.org/sparql")
sparql_db.setReturnFormat(JSON)

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
            ''')
}

# Maintain translated placeholder count
plc_count = {
    'total': 0,
    'translated': 0
}


def put_placeholders(input):
    '''
    This method expects the input format as stated in the README for EL output

    :param input: input dictionary containing text and its entity annotations + links
    :param kb: knowledge-base that the entities are linked to. Can only handle Wikidata and DBpedia for now
    :return: input dictionary with append key-value pair mapping 'text_plc' to the text with placeholders.
    '''

    query = input['text']
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
        logging.debug('Formed SPARQL:\n %s'%f_sparql)
        ret = sparql.queryAndConvert()
        plchldr = '[00%d]' % arr_ind
        # plchldr = '[plc%d]' % arr_ind
        link['placeholder'] = plchldr
        # incrementing global placeholder count
        plc_count['total'] += 1
        # forming the placeholder query
        query_plc += query[last_ind:link['start']] + plchldr
        arr_ind += 1
        last_ind = link['end']
        # extracting English label
        for r in ret["results"]["bindings"]:
            link['en_label'] = r['enlbl']['value']
            break
    query_plc += query[last_ind:]
    input['text_plc'] = query_plc
    logging.debug('Injected placeholders: %s'%input)
    return input


def replace_placeholders(trans_text, input):
    '''
    This function replaces the placeholders in the translated text with their corresponding English labels.

    :param trans_text: translated English text with placeholders
    :param input: input dictionary with details about mentions and placeholders + links
    :return: translated string with replaced placeholders
    '''
    res_query = trans_text
    ent_links = input['ent_mentions']
    for link in ent_links:
        if 'link' not in link:
            continue
        label = link['surface_form']
        if 'en_label' in link:
            label = link['en_label']
        # check the number of properly translated placeholders
        if link['placeholder'] in res_query:
            plc_count['translated'] += 1
        res_query = res_query.replace(link['placeholder'], label)
    logging.debug('Query after replaced placeholder: %s'%res_query)
    logging.debug('Correctly translated placeholders: %d / %d' % (plc_count['translated'], plc_count['total']))
    return res_query
