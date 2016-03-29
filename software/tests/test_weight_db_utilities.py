import unittest
import sys

if "DEBUG" in sys.argv:
    sys.path.insert(0, "..")
    sys.path.insert(0, "../../")
    sys.path.insert(0, ".")
    sys.argv.remove("DEBUG")

import metax.WeightDBUtilities as WeightDBUtilities


class TestWeightDBUtilities(unittest.TestCase):
    def testGeneEntry(self):
        entry = WeightDBUtilities.GeneEntry("a", "b", "c", "d")
        self.assertEqual(entry.gene, "a")
        self.assertEqual(entry.gene_name, "b")
        self.assertEqual(entry.R2, "c")
        self.assertEqual(entry.n_snp, "d")

    def testWeightDBEntry(self):
        entry = WeightDBUtilities.WeightDBEntry("a", "b", "c", "d", "e", "f", "g", "h")
        self.assertEqual(entry.rsid, "a")
        self.assertEqual(entry.gene, "b")
        self.assertEqual(entry.weight, "c")
        self.assertEqual(entry.ref_allele, "d")
        self.assertEqual(entry.eff_allele, "e")
        self.assertEqual(entry.pval, "f")
        self.assertEqual(entry.N, "g")
        self.assertEqual(entry.cis, "h")

    def testWeightDBInvalidPath(self):
        weight_db = WeightDBUtilities.WeightDB("tests/kk.db")

        with self.assertRaises(RuntimeError):
            weight_db.openDBIfNecessary()

    def testWeightDB(self):
        #test setup
        class DummyCallback():
            def __init__(self):
                self.entries = []

            def __call__(self, weight, extra):
                self.entries.append((weight, extra))

        expected_weights = expected_weights_results()
        expected_extra = expected_extra_results()

        weight_db = WeightDBUtilities.WeightDB("tests/_td/test.db")

        #load gene data
        extra = weight_db.loadExtraColumnData("A")
        self.assertExtra(extra, [expected_extra[0]])

        extra = weight_db.loadExtraColumnData("B")
        self.assertExtra(extra, [expected_extra[1]])

        extra = weight_db.loadExtraColumnData("C")
        self.assertExtra(extra, [expected_extra[2]])

        extra = weight_db.loadExtraColumnData("D")
        self.assertExtra(extra, [expected_extra[3]])

        extra = weight_db.loadExtraColumnData()
        self.assertExtra(extra, expected_extra)

        #load db
        callback = DummyCallback()
        weights = weight_db.loadFromDB(callback, "A")
        self.assertWeights(weights, [expected_weights[0], expected_weights[1], expected_weights[2]])
        self.assertEqual(len(callback.entries),3)
        callback_weights = [e[0] for e in callback.entries]
        self.assertEqual(callback_weights, weights)

        callback = DummyCallback()
        weights = weight_db.loadFromDB(callback, "B")
        self.assertWeights(weights, [expected_weights[3], expected_weights[4]])
        self.assertEqual(len(callback.entries),2)
        callback_weights = [e[0] for e in callback.entries]
        self.assertEqual(callback_weights, weights)

        callback = DummyCallback()
        weights = weight_db.loadFromDB(callback, "C")
        self.assertWeights(weights, [expected_weights[5]])
        self.assertEqual(len(callback.entries),1)
        callback_weights = [e[0] for e in callback.entries]
        self.assertEqual(callback_weights, weights)

        callback = DummyCallback()
        weights = weight_db.loadFromDB(callback, "D")
        self.assertWeights(weights, [expected_weights[6]])
        self.assertEqual(len(callback.entries),1)
        callback_weights = [e[0] for e in callback.entries]
        self.assertEqual(callback_weights, weights)

        callback = DummyCallback()
        weights = weight_db.loadFromDB(callback)
        self.assertWeights(weights, expected_weights)
        self.assertEqual(len(callback.entries),7)
        callback_weights = [e[0] for e in callback.entries]
        self.assertEqual(callback_weights, weights)

        #gene names
        gene_names = weight_db.loadGeneNamesFromDB()
        self.assertEqual(gene_names, ["A", "B", "C", "D"])

    def testWeightDBEntryLogic(self):
        weight_db_entry_logic = WeightDBUtilities.WeightDBEntryLogic("tests/_td/test.db")

        expected_weights = expected_weights_results()
        expected_extra = expected_extra_results()

        self.assertEqual(len(weight_db_entry_logic.weights_by_gene), len(expected_extra))
        self.assertEqual(len(weight_db_entry_logic.gene_data_for_gene), len(expected_extra))

        for e in expected_extra:
            self.assertTrue(e.gene in weight_db_entry_logic.weights_by_gene)
            self.assertTrue(e.gene in weight_db_entry_logic.gene_data_for_gene)

            actual_gene_data = weight_db_entry_logic.gene_data_for_gene[e.gene]
            self.assertExtra([actual_gene_data], [e])

            actual_weights = [w for k,w in weight_db_entry_logic.weights_by_gene[e.gene].iteritems()]
            e_w = [w for w in expected_weights if w.gene == e.gene]
            self.assertWeights(actual_weights, e_w)

        self.assertEqual(len(weight_db_entry_logic.genes_for_an_rsid), 6)
        for rsid, genes in weight_db_entry_logic.genes_for_an_rsid.iteritems():
            expected = [w.gene for w in expected_weights if w.rsid == rsid]
            self.assertEqual(expected, genes)

    def assertWeights(self, weights, expected):
        self.assertEqual(len(weights), len(expected))
        for i,actual in enumerate(weights):
            e = expected[i]
            self.assertEqual(actual.rsid, e.rsid)
            self.assertEqual(actual.gene, e.gene)
            self.assertEqual(actual.weight, e.weight)
            self.assertEqual(actual.ref_allele, e.ref_allele)
            self.assertEqual(actual.eff_allele, e.eff_allele)
            self.assertEqual(actual.pval, e.pval)
            self.assertEqual(actual.N, e.N)
            self.assertEqual(actual.cis, e.cis)

    def assertExtra(self, extra, expected):
        self.assertEqual(len(extra), len(expected))

        for i,actual in enumerate(extra):
            e = expected[i]
            self.assertEqual(e.gene, actual.gene)
            self.assertEqual(e.gene_name, actual.gene_name)
            self.assertEqual(e.R2, actual.R2)
            self.assertEqual(e.n_snp, actual.n_snp)

def expected_weights_results():
    class DummyWeight(object):
        pass

    weights = []
    expected_data = [
        ["rs1", "A", 0.2, "C", "T", 0.1, 3, 1],
        ["rs2", "A", 0.1, "A", "G", 0.2, 3, 2],
        ["rs3", "A", 0.05, "G", "A", 0.3, 3, 3],
        ["rs4", "B", 0.4, "T", "C", 0.4, 2, 4],
        ["rs5", "B", 0.3, "C", "T", 0.5, 2, 5],
        ["rs6", "C", 0.5, "T", "C", 0.6, 1, 6],
        ["rs1", "D", 0.6, "T", "C", 0.7, 1, 7]
    ]

    for e in expected_data:
        w = DummyWeight()
        w.rsid, w.gene, w.weight, w.ref_allele, w.eff_allele, w.pval, w.N, w.cis  = e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7]
        weights.append(w)

    return weights

def expected_extra_results():
    class DummyExtra(object):
        pass

    extra = []

    expected_data = [
        ["A", "gene1", 0.9, 3],
        ["B", "gene2", 0.8, 2],
        ["C", "gene3", 0.7, 1],
        ["D", "gene4", 0.6, 1]
    ]

    for e in expected_data:
        entry = DummyExtra()
        entry.gene, entry.gene_name, entry.R2, entry.n_snp = e[0], e[1], e[2], e[3]
        extra.append(entry)

    return extra