# This class demonstrates how each component should look like
import logging

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pickle


class MgenreEl:

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
        self.el_tokenizer = AutoTokenizer.from_pretrained("facebook/mgenre-wiki")
        self.el_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/mgenre-wiki").eval()
        logging.debug('MgenreEl component initialized.')

    def process_input(self, input):
        '''
        Function to link the entities from an annotated text.

        :param input:  formatted dictionary as stated in the README for NER output
        :return:  formatted dictionary as stated in the README for EL output
        '''
        logging.debug('Input received: %s'%input)
        # Setting knowledge base as Wikidata
        input['kb'] = 'wd'
        ent_indexes = input['ent_mentions']
        query = input['text']
        sentences = []
        # Generate annotated sentence for each mention + placeholder
        for ent_mention in ent_indexes:
            cur_sent = query[:ent_mention['start']] + '[START] ' + query[ent_mention['start']:ent_mention[
                'end']] + ' [END]' + query[ent_mention['end']:]
            sentences.append(cur_sent)
        print(sentences)
        # Step 2: Run Entity Linking on the annotated sentence(s)
        outputs = self.el_model.generate(
            **self.el_tokenizer(sentences, return_tensors="pt", padding=True),
            num_beams=5,
            num_return_sequences=1,
            # OPTIONAL: use constrained beam search
            # prefix_allowed_tokens_fn=lambda batch_id, sent: trie.get(sent.tolist())
        )

        res_arr = self.el_tokenizer.batch_decode(outputs, skip_special_tokens=True)
        print(res_arr)
        i = 0
        for x in res_arr:
            sp_arr = x.split(" >> ")
            rev_tuple = tuple(reversed(sp_arr))
            if rev_tuple in self.lang_title2wikidataID:
                ent_indexes[i]['link'] = max(self.lang_title2wikidataID[rev_tuple])
            i += 1
        logging.debug('Output: %s'%input)
        return input
