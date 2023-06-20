#!/usr/bin/env python3
import unittest

from analysis import dbp_to_wd, entitiesfound, resolve
from wikidata_client import wd_labels, wd_classes

class AnalysisTestCase(unittest.TestCase):
    dbp_example = 'http://dbpedia.org/resource/Moscow'
    dbp_lang_examples = [
        'http://de.dbpedia.org/resource/Moskau',
        'http://es.dbpedia.org/resource/Moscú',
        'http://fr.dbpedia.org/resource/Moscou',
        'http://ru.dbpedia.org/resource/Москва',
    ]
    wd_localname = 'Q649'
    wd_example = 'http://www.wikidata.org/entity/' + wd_localname

    def test_dbp_to_wd(self):
        self.assertEqual(dbp_to_wd(self.dbp_example), self.wd_example)

        for dbp_uri in self.dbp_lang_examples:
            wd_uri = dbp_to_wd(dbp_uri)
            self.assertEqual(wd_uri, self.wd_example, dbp_uri)

        self.assertEqual(dbp_to_wd('http://de.dbpedia.org/resource/Facebook_Inc.'), 'http://www.wikidata.org/entity/Q380')

    def test_resolve_dbp(self):
        wd_uri = resolve(self.dbp_example)
        self.assertEqual(wd_uri, self.wd_example)

    def test_resolve_wd_full(self):
        wd_uri = resolve(self.wd_example)
        self.assertEqual(wd_uri, self.wd_example)

    def test_wd_labels_with_one_lang(self):
        labels = wd_labels(self.wd_example, 'en')
        self.assertIsInstance(labels, list)
        self.assertIn('Moscow', labels)
        self.assertNotIn('Москва', labels)
        self.assertNotIn('Moskau', labels)

    def test_wd_labels_with_lang_list(self):
        labels = wd_labels(self.wd_example, ['en', 'ru'])
        self.assertIsInstance(labels, list)
        self.assertIn('Moscow', labels)
        self.assertIn('Москва', labels)
        self.assertNotIn('Moskau', labels)

    def test_wd_classes(self):
        classes = wd_classes(self.wd_example)
        self.assertIn({'class': 'http://www.wikidata.org/entity/Q7930989', 'label': 'city or town'}, classes)

    def test_entitiesfound(self):
        def e(s): return {'ent_mentions': [{'canonical_uri': x} for x in s]}
        self.assertEqual(entitiesfound(e({1, 2}), e({1, 2})), 1)
        self.assertEqual(entitiesfound(e({1, 2, 3, 4}), e({1, 2})), 1)
        self.assertEqual(entitiesfound(e({1, 2}), e({1, 2, 3, 4})), 0.5)
        self.assertEqual(entitiesfound(e({1, 2}), e({3, 4})), 0)
        self.assertEqual(entitiesfound(e({1, 2}), e(set())), 1)