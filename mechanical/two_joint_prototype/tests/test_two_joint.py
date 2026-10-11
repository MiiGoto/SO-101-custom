import math
import unittest
from dataclasses import replace
from joint_config import JOINTS,JointState
from kinematics import forward,inverse,trajectory

class PrototypeTests(unittest.TestCase):
    def test_straight(self): self.assertEqual(forward((0,0)),(.19,0))
    def test_ik_round_trip(self):
        for a in (5,25,50,70):
            for b in (5,40,90,115):
                q=tuple(map(math.radians,(a,b)));p=forward(q);r=inverse(*p)
                for x,y in zip(q,r):self.assertAlmostEqual(x,y,places=10)
    def test_unreachable_and_limits(self):
        for p in ((1,0),(0,-.15),(float('nan'),0)):
            with self.assertRaises(ValueError):inverse(*p)
        for q in ((-.01,0),(0,3),(float('nan'),0)):
            with self.assertRaises(ValueError):forward(q)
    def test_encoder_wrap_and_sign(self):
        cfg=replace(JOINTS[0],encoder_zero=4090,direction=-1)
        self.assertAlmostEqual(cfg.measured_angle(4),-10*2*math.pi/4096)
        with self.assertRaises(ValueError):cfg.measured_angle(4096)
    def test_uncommissioned_pulse(self):
        with self.assertRaises(RuntimeError):JOINTS[0].command_pulse(.1)
    def test_trajectory_endpoints_and_rate(self):
        rows=list(trajectory((0,0),(.2,.3),8));self.assertEqual(rows[0][1],(0,0));self.assertAlmostEqual(rows[-1][1][1],.3)
        for (t,p),(u,q) in zip(rows,rows[1:]):
            self.assertLessEqual(max(abs(b-a)/(u-t) for a,b in zip(p,q)),.1)
        with self.assertRaises(ValueError):list(trajectory((0,0),(.2,.3),.1))
    def test_logging_does_not_invent_observations(self):
        state=JointState(0,(0,0),None,'UNVALIDATED','none',False)
        self.assertIsNone(state.to_record()['measured_rad'])
        with self.assertRaises(ValueError):replace(state,valid=True).to_record()

if __name__=='__main__':unittest.main()
