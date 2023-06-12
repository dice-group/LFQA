#!/usr/bin/env python3
import unittest

import analysis

class AnalysisTestCase(unittest.TestCase):
    dbp_example = 'http://dbpedia.org/resource/Moscow'
    wd_localname = 'Q649'
    wd_example = 'http://www.wikidata.org/entity/' + wd_localname

    def test_dbp_to_wd(self):
        wd_uri = analysis.dbp_to_wd(self.dbp_example)
        self.assertEqual(wd_uri, self.wd_example)

    def test_resolve_dbp(self):
        wd_uri = analysis.resolve(self.dbp_example)
        self.assertEqual(wd_uri, self.wd_example)

    def test_resolve_wd_full(self):
        wd_uri = analysis.resolve(self.wd_example)
        self.assertEqual(wd_uri, self.wd_example)
