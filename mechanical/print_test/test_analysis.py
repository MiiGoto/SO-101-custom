import unittest, importlib.util
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location('task4',Path(__file__).with_name('analyze_task4.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class TorqueValidation(unittest.TestCase):
 def test_gravity_matches_energy_gradient(self):
  B=a.bodies(a.read(a.M/'follower_revb/analysis/assembly.json'));q=np.array([[.1,.3,-.2,.15,-.1,.2]])
  G,_=a.evaluate(B,q,0)
  def energy(x):
   F,_,_=a.frames(x);return sum(b['mass']*9.80665*(np.einsum('nij,j->ni',F[b['link']][:,:3,:3],b['com'])+F[b['link']][:,:3,3]/1000)[0,2] for b in B)
  for k in range(6):
   plus=q.copy();minus=q.copy();plus[0,k]+=1e-6;minus[0,k]-=1e-6
   self.assertAlmostEqual(G[0,k],-(energy(plus)-energy(minus))/2e-6,places=6)
 def test_payload_linearity(self):
  B=a.bodies(a.read(a.M/'follower_revb/analysis/assembly.json'));q=np.zeros((1,6))
  g0,_=a.evaluate(B,q,0);g5,_=a.evaluate(B,q,.05);g10,_=a.evaluate(B,q,.1)
  np.testing.assert_allclose(g10-g0,2*(g5-g0),atol=1e-12)
 def test_two_joint_fixed_axes_zero(self):
  B=a.bodies(a.read(a.M/'two_joint_revc/analysis/assembly.json'));g,d=a.evaluate(B,np.zeros((1,6)),.05,True)
  np.testing.assert_equal(g[:,[0,3,4,5]],0);np.testing.assert_equal(d[[0,3,4,5]],0)
if __name__=='__main__':unittest.main()
