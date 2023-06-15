# This class demonstrates how each component should look like
import logging
import threading
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pickle
from el_abs import GenEL
import sys
sys.path.insert(1, '/neamt/util/')
import threadsafe_resource_pool_util as trp_util


def get_rev_tuple(index, arr):
    det_ent = arr[index]
    ent_lang_pair = det_ent.split(" >> ")
    rev_tuple = tuple(reversed(ent_lang_pair))
    return rev_tuple


class MgenreEl(GenEL):

    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Entity Linking
        # Load Prefix Trie
        # with open("/neamt/data/mgenre_data/titles_lang_all105_marisa_trie_with_redirect.pkl", "rb") as f:
        #     trie = pickle.load(f)
        # Load language based title to wikidata id map
        with open("/neamt/data/mgenre_data/lang_title2wikidataID-normalized_with_redirect.pkl", "rb") as f:
            self.lang_title2wikidataID = pickle.load(f)
        # Load the tokenizer and model
        # self.el_tokenizer = AutoTokenizer.from_pretrained("facebook/mgenre-wiki")
        self.tokenizer_name = "facebook/mgenre-wiki"
        self.tokenizer_kwargs = {}
        self.el_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/mgenre-wiki").eval()

        logging.debug('%s component initialized.' % type(self).__name__)


    def prep_input_args(self, input):
        extra_args = {}
        # Setting knowledge base as Wikidata
        input['kb'] = 'wd'
        extra_args['mg_num_return_sequences'] = int(input.get('mg_num_return_sequences', 1))
        return extra_args

    def link_entities(self, query, lang, ent_indexes, extra_args):
        """
        Huggingface's tokenizers have an issue with parallel thread access (https://github.com/huggingface/tokenizers/issues/537).
        """
        # Get thread safe tokenizer
        el_tokenizer = trp_util.get_threadsafe_object(type(self).__name__, AutoTokenizer.from_pretrained, [self.tokenizer_name], self.tokenizer_kwargs)
        try:
            # Extract custom parameter
            num_return_sequences = extra_args.get('mg_num_return_sequences')

            # do not continue if no mentions are present
            if len(ent_indexes) == 0:
                logging.debug('No mentions found!')
                return ent_indexes
            sentences = []
            # Generate annotated sentence for each mention + placeholder
            for ent_mention in ent_indexes:
                cur_sent = query[:ent_mention['start']] + '[START] ' + query[ent_mention['start']:ent_mention[
                    'end']] + ' [END]' + query[ent_mention['end']:]
                sentences.append(cur_sent)
            print(sentences)
            # Step 2: Run Entity Linking on the annotated sentence(s)
            outputs = self.el_model.generate(
                **el_tokenizer(sentences, return_tensors="pt", padding=True),
                num_beams=5,
                num_return_sequences=num_return_sequences,
                # OPTIONAL: use constrained beam search
                # prefix_allowed_tokens_fn=lambda batch_id, sent: trie.get(sent.tolist())
            )

            res_arr = el_tokenizer.batch_decode(outputs, skip_special_tokens=True)
            logging.debug('model output: %s'%str(res_arr))
            mention_index = 0
            result_index = 0
            while result_index < len(res_arr):
                rev_tuple = get_rev_tuple(result_index, res_arr)
                if rev_tuple in self.lang_title2wikidataID:
                    temp_link = max(self.lang_title2wikidataID[rev_tuple])
                    logging.debug('link found %s for the tuple %s' % (temp_link, str(rev_tuple)))
                    ent_indexes[mention_index]['link'] = temp_link
                # Find all candidates
                ent_indexes[mention_index]['link_candidates'] = []
                j = result_index
                while j < result_index + num_return_sequences:
                    rev_tuple = get_rev_tuple(j, res_arr)
                    temp_link = ''
                    if rev_tuple in self.lang_title2wikidataID:
                        temp_link = max(self.lang_title2wikidataID[rev_tuple])
                        logging.debug('link found %s for the tuple %s' % (temp_link, str(rev_tuple)))
                    ent_indexes[mention_index]['link_candidates'].append((rev_tuple[1], rev_tuple[0], temp_link))
                    j += 1
                result_index += num_return_sequences
                mention_index += 1

            return ent_indexes
        finally:
            trp_util.release_threadsafe_object(type(self).__name__, el_tokenizer)
