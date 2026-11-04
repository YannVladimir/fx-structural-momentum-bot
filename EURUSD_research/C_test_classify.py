"""Unit tests for the pure statistics/classification helpers in
C_crt_sd_structural_01.py (describe, bucket, control, classify).

These do not touch live market data, MetaTrader5, or any entry/exit
calculation -- only the sample-size/significance gating used to label a
structural comparison as PROMISING / NEGATIVE / INCONCLUSIVE.
"""
import unittest
import C_crt_sd_structural_01 as s


def row(direction, outcome, ratio=1.0, scale=1.0):
    return {'direction': direction, 'outcome': outcome, 'ratio': ratio, 'scale': scale,
            'target_distance': 1.0, 'invalidation_distance': 1.0, 'target_normalized': 1.0,
            'MFE_price': 0.0, 'MAE_price': 0.0, 'C3_close_in_C1_range_location': 0.0}


class DescribeTests(unittest.TestCase):
    def test_empty_rows(self):
        self.assertEqual(s.describe([]), {'N': 0, 'bull': 0, 'bear': 0})

    def test_counts_and_rates(self):
        rows = [row(1, 'TARGET_FIRST'), row(1, 'INVALID_FIRST'), row(-1, 'NEITHER')]
        out = s.describe(rows)
        self.assertEqual(out['N'], 3)
        self.assertEqual(out['bull'], 2)
        self.assertEqual(out['bear'], 1)
        self.assertAlmostEqual(out['TARGET_FIRST_rate'], 1 / 3)
        self.assertAlmostEqual(out['NEITHER_rate'], 1 / 3)


class BucketTests(unittest.TestCase):
    def test_assigns_bucket_key_per_row(self):
        rows = [row(1, 'TARGET_FIRST', ratio=r, scale=r) for r in [0.5, 1.0, 1.5, 2.0, 2.5]]
        s.bucket(rows)
        for r in rows:
            self.assertIn('bucket', r)
            self.assertEqual(r['bucket'][0], 1)

    def test_degenerate_geometry_raises(self):
        rows = [row(1, 'TARGET_FIRST'), row(1, 'TARGET_FIRST')]
        rows[0]['ratio'] = None
        with self.assertRaises(RuntimeError):
            s.bucket(rows)


class ControlTests(unittest.TestCase):
    def test_empty_subset_returns_none(self):
        self.assertIsNone(s.control([row(1, 'TARGET_FIRST')], []))

    def test_missing_or_ambiguous_ticks_blocks(self):
        parent = [row(1, 'NO_TICKS')]
        out = s.control(parent, parent)
        self.assertEqual(out, {'blocked': 'Missing ticks or ambiguous ordering'})

    def test_structural_output_bounds(self):
        parent = [row(1, 'TARGET_FIRST', ratio=r, scale=r) for r in [0.1] * 15 + [1.0] * 15]
        parent += [row(1, 'NEITHER', ratio=r, scale=r) for r in [0.1] * 15 + [1.0] * 15]
        s.bucket(parent)
        subset = [r for r in parent if r['outcome'] == 'TARGET_FIRST'][:5]
        out = s.control(parent, subset)
        self.assertEqual(out['N'], 5)
        self.assertTrue(0.0 <= out['p_value'] <= 1.0)
        self.assertTrue(0.0 <= out['real_rate'] <= 1.0)
        self.assertTrue(0.0 <= out['matched_null_rate'] <= 1.0)
        self.assertEqual(out['sparse_strata'], {})


class ClassifyTests(unittest.TestCase):
    def test_below_minimum_sample_is_inconclusive(self):
        self.assertEqual(s.classify({'p_value': 0.0001, 'effect_absolute': 1}, {'p_value': 0.0001, 'effect_absolute': 1}, 10, 50),
                          'INCONCLUSIVE (sample/coverage)')
        self.assertEqual(s.classify({'p_value': 0.0001, 'effect_absolute': 1}, None, 150, 50),
                          'INCONCLUSIVE (sample/coverage)')

    def test_blocked_split_is_inconclusive(self):
        blocked = {'blocked': 'Missing ticks or ambiguous ordering'}
        self.assertEqual(s.classify(blocked, {'p_value': 0.0001, 'effect_absolute': 1}, 150, 50),
                          'INCONCLUSIVE (sample/coverage)')

    def test_promising_requires_both_splits_significant_positive_and_train_n_100(self):
        train = {'p_value': 0.001, 'effect_absolute': 5.0}
        val = {'p_value': 0.001, 'effect_absolute': 3.0}
        self.assertEqual(s.classify(train, val, 100, 30), 'PROMISING incremental information')
        # Same effect/p-values but train N below 100 must NOT qualify as promising.
        self.assertNotEqual(s.classify(train, val, 99, 30), 'PROMISING incremental information')

    def test_negative_requires_both_splits_significant_negative(self):
        train = {'p_value': 0.001, 'effect_absolute': -5.0}
        val = {'p_value': 0.001, 'effect_absolute': -3.0}
        self.assertEqual(s.classify(train, val, 150, 50), 'NEGATIVE incremental information')

    def test_no_confirmed_value_when_neither_split_significant(self):
        train = {'p_value': 0.5, 'effect_absolute': 5.0}
        val = {'p_value': 0.5, 'effect_absolute': -3.0}
        self.assertEqual(s.classify(train, val, 150, 50), 'NO CONFIRMED INCREMENTAL VALUE')

    def test_mixed_significance_is_inconclusive(self):
        train = {'p_value': 0.0001, 'effect_absolute': 5.0}
        val = {'p_value': 0.5, 'effect_absolute': 3.0}
        self.assertEqual(s.classify(train, val, 150, 50), 'INCONCLUSIVE (no replicated corrected effect)')


if __name__ == '__main__':
    unittest.main(verbosity=2)
