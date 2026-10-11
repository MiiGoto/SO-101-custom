import math,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'software'),str(ROOT/'simulation')]
from joint_contract import JOINTS,JointSample,OfflineJointContract
from torque_envelope import model,fk,gravity,distances,G

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.c=OfflineJointContract(); self.c.connect()
        self.c.set_simulated_observation(JointSample(dict.fromkeys(JOINTS,0.),10.,True,'mock','simulated'))
    def test_command_does_not_become_observation(self):
        target=dict.fromkeys(JOINTS,.1);self.c.write_joint_targets(target,10.01)
        self.assertEqual(self.c.read_joint_positions(10.01).actual_rad,dict.fromkeys(JOINTS,0.))
    def test_stale_disconnect_and_invalid_fail_closed(self):
        with self.assertRaises(RuntimeError): self.c.read_joint_positions(10.1)
        with self.assertRaises(RuntimeError): self.c.read_joint_positions(9.9)
        self.c.set_simulated_observation(JointSample(dict.fromkeys(JOINTS,0.),10.,False,'mock','simulated'))
        with self.assertRaises(RuntimeError): self.c.write_joint_targets(dict.fromkeys(JOINTS,0.),10.)
        self.c.disconnect()
        with self.assertRaises(ConnectionError): self.c.read_joint_positions(10.)
    def test_invalid_write_is_atomic(self):
        for bad in [math.nan,math.inf,99.]:
            target=dict.fromkeys(JOINTS,.1);target['elbow_flex']=bad
            with self.assertRaises(ValueError):self.c.write_joint_targets(target,10.)
            self.assertEqual(self.c.targets,dict.fromkeys(JOINTS,0.))
    def test_no_synthetic_missing_axis(self):
        with self.assertRaises(ValueError):self.c.set_simulated_observation(JointSample({'gripper':0.},10.,True,'mock','simulated'))

class MechanicsTests(unittest.TestCase):
    def test_gravity_matches_potential_energy_gradient(self):
        links,joints=model('official');q=np.array([[.2,.3,-.4,.5,.1,.6]])
        def energy(x):
            p,r,_,_=fk(x,joints);value=0.
            for j in joints.values():
                if j['limits'] is None:continue
                l=links[j['child']]; com=p[j['child']][0]+r[j['child']][0]@l['com'];value+=G*l['mass']*com[2]
            j=joints['gripper_frame_joint'];pp=p[j['parent']][0]+r[j['parent']][0]@j['xyz'];return value+.05*G*pp[2]
        actual=gravity(q,links,joints,.05)[0]
        for k in range(6):
            plus=q.copy();minus=q.copy();plus[0,k]+=1e-6;minus[0,k]-=1e-6
            self.assertAlmostEqual(actual[k],-(energy(plus)-energy(minus))/2e-6,places=7)
    def test_sampled_gravity_within_radius_envelope(self):
        for variant in ['official','A','B80','B85','B90','C','D']:
            links,joints=model(variant);rng=np.random.default_rng(7);lim=np.array([joints[n]['limits'] for n in JOINTS]);q=rng.uniform(lim[:,0],lim[:,1],(1000,6))
            R,_=distances(links,joints);m=np.array([links[joints[n]['child']]['mass'] for n in JOINTS]+[.1]);bound=(R*m).sum(axis=1)*G
            self.assertTrue(np.all(np.abs(gravity(q,links,joints,.1))<=bound+1e-9))
    def test_gravity_zero_without_masses(self):
        links,joints=model('A')
        for l in links.values():l['mass']=0.
        self.assertTrue(np.allclose(gravity(np.zeros((1,6)),links,joints,0),0))
    def test_torque_units(self): self.assertAlmostEqual(9.2*.0980665,.9022118)

if __name__=='__main__':unittest.main()
