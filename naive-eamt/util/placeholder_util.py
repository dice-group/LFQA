'''
This python encapsulates the functions to deal with placeholders in the annotated natural language text.
'''
import logging

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
            SELECT ?enlbl WHERE {
                <%s> rdfs:label ?enlbl .
                FILTER (langMatches( lang(?enlbl), "EN" ) )
            } 
            LIMIT 1
            ''')
}


def put_placeholders(input):
    '''
    This method expects the input format as described for EL output here: https://github.com/dice-group/LFQA/tree/neamt/naive-eamt#EL
    :param input: input dictionary containing text and its entity annotations + links
    :param kb: knowledge-base that the entities are linked to. Can only handle Wikidata and DBpedia for now
    :return: input dictionary with append key-value pair mapping 'text_plc' to the text with placeholders.
    '''
    kb = input['kb']
    query = input['text']
    ent_links = input['ent_mentions']
    arr_ind = 1
    sparql = kb_info[kb][0]
    sparql_str = kb_info[kb][1]

    query_plc = ''
    last_ind = 0
    for link in ent_links:
        if 'link' not in link:
            continue
        sparql.setQuery(sparql_str % link['link'])
        ret = sparql.queryAndConvert()
        plchldr = '[plc%d]' % arr_ind
        link['placeholder'] = plchldr
        # forming the placeholder query
        query_plc += query[last_ind:link['start']] + plchldr
        arr_ind += 1
        # extracting English label
        for r in ret["results"]["bindings"]:
            link['en_label'] = r['enlbl']['value']
            break
    query_plc += query[last_ind:]
    input['text_plc'] = query_plc
    logging.debug('Injected placeholders', input)
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
        res_query = res_query.replace(link['placeholder'], link['en_label'])
    logging.debug('Query after replaced placeholder:', res_query)
    return res_query
