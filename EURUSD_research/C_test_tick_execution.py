import unittest
import numpy as np
from Claude_tick_execution import replay,ReplayError

def ticks(rows):
 return np.array(rows,dtype=[('time_msc','i8'),('bid','f8'),('ask','f8')])

class ExecutionTests(unittest.TestCase):
 def test_long_entry_ask_exit_bid_stop_gap(self):
  r=replay([ticks([(100,100,101),(200,96,97)])],100,500,1,99,105)
  self.assertEqual(r['entry'],101); self.assertEqual(r['exit'],96)
  self.assertEqual(r['R'],-2.5); self.assertEqual(r['stop_overshoot_price'],3)
 def test_short_entry_bid_exit_ask_stop_gap(self):
  r=replay([ticks([(100,100,101),(200,104,106)])],100,500,-1,102,96)
  self.assertEqual(r['entry'],100); self.assertEqual(r['exit'],106); self.assertEqual(r['R'],-3)
 def test_long_target_bid_trigger_limit_fill(self):
  r=replay([ticks([(100,100,101),(200,106,107)])],100,500,1,99,105)
  self.assertEqual(r['exit'],105); self.assertEqual(r['reason'],'target')
 def test_short_target_ask_trigger(self):
  r=replay([ticks([(100,100,101),(200,94,96),(300,92,94)])],100,500,-1,102,95)
  self.assertEqual(r['exit_time_msc'],300); self.assertEqual(r['exit'],95)
 def test_no_future_entry_and_timeout(self):
  r=replay([ticks([(90,50,51),(110,100,101),(500,102,103)])],100,500,1,99,105)
  self.assertEqual(r['entry_time_msc'],110); self.assertEqual(r['reason'],'time'); self.assertEqual(r['exit'],102)
 def test_slippage_costs_both_sides(self):
  r=replay([ticks([(100,100,101),(200,96,97)])],100,500,1,99,105,.5,.2)
  self.assertEqual(r['entry'],101.5); self.assertEqual(r['exit'],95.5)
  self.assertAlmostEqual(r['R'],-6.2/2.5)
 def test_missing_exit_is_not_invented(self):
  with self.assertRaises(ReplayError): replay([ticks([(100,100,101)])],100,500,1,99,105)
 def test_invalid_and_unordered_quotes_rejected(self):
  for q in [ticks([(100,100,99)]),ticks([(200,100,101),(100,100,101)])]:
   with self.assertRaises(ReplayError): replay([q],100,500,1,99,105)
 def test_cross_chunk_stop(self):
  r=replay([ticks([(100,100,101)]),ticks([(300,97,98)])],100,500,1,99,105)
  self.assertEqual(r['reason'],'stop'); self.assertEqual(r['exit_time_msc'],300)

if __name__=='__main__': unittest.main(verbosity=2)
