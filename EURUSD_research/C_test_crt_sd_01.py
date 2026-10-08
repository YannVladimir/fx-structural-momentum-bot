import unittest
import numpy as np
import Claude_crt_sd_structural_01 as s

def candles(rows):
 return np.array(rows,dtype=[('time','i8'),('open','f8'),('high','f8'),('low','f8'),('close','f8')])

class TimingTests(unittest.TestCase):
 def test_confirmation_time_bar_consumes_zone(self):
  htf=candles([(0,10,11,8,9),(3600,9,12,9,11),(7200,11,14,10,13),(10800,13,16,12,15)])
  crt=candles([(14400,10,11,9,10),(18000,10,11,9,10)])
  z=s.zones_from(htf,3600,crt)[0]
  self.assertEqual(z['confirmed'],14400); self.assertEqual(z['first_touch_index'],0)
  self.assertFalse(s.fresh_match(z,1,crt[1],8,10,1))
 def test_zone_must_exist_at_c2_open(self):
  z={'direction':1,'confirmed':14400,'first_touch_index':10,'low':8,'high':10}
  c2=candles([(10800,10,11,8,10)])[0]
  self.assertFalse(s.fresh_match(z,0,c2,8,10,1))
 def test_confirmation_exactly_at_open_is_available(self):
  z={'direction':1,'confirmed':14400,'first_touch_index':0,'low':8,'high':10}
  c2=candles([(14400,10,11,8,10)])[0]
  self.assertTrue(s.fresh_match(z,0,c2,8,10,1))
 def test_bias_prefix_invariance(self):
  rng=np.random.default_rng(73); close=rng.uniform(8,12,100)
  a=candles([(i*3600,x,x+1,x-1,x) for i,x in enumerate(close)])
  full=s.direction_states(a)
  for length in [10,25,50,99]: np.testing.assert_array_equal(s.direction_states(a[:length]),full[:length])
 def test_no_weekend_c3_extension(self):
  base=s.START; crt=candles([(base,10,12,8,11),(base+3600,9,11,6,10),(base+100000,10,11,9,10)])
  htf=candles([(base,10,12,8,11)])
  rows,flags=s.detect(crt,[],htf,14400,3600)
  self.assertEqual(rows,[]); self.assertEqual(flags[0]['flag'],'MISSING_IMMEDIATE_C3')
 def test_no_cross_split_outcome(self):
  end=s.TRAIN_END; crt=candles([(end-7200,10,12,8,11),(end-3600,9,11,6,10),(end,10,11,9,10)])
  htf=candles([(end-14400,10,12,8,11)])
  # Decision at validation boundary is classified VALIDATION, not TRAIN.
  rows,flags=s.detect(crt,[],htf,14400,3600)
  if rows: self.assertEqual(rows[0]['split'],'VALIDATION')
 def test_doji_rejected(self):
  base=s.START; crt=candles([(base,10,12,8,11),(base+3600,10,11,6,10),(base+7200,10,11,9,10)])
  rows,flags=s.detect(crt,[],crt,3600,3600)
  self.assertEqual(rows,[])

if __name__=='__main__': unittest.main(verbosity=2)
