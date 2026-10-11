import json,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))

class AnalysisEvidenceTests(unittest.TestCase):
    def test_payload_virtual_work(self):
        cases=read('torque_analysis.json')['cases']
        zero=cases[0]['poses'][0]['gravity_Nm'];loaded=cases[2]['poses'][0]['gravity_Nm']
        self.assertAlmostEqual(loaded[0]-zero[0],.05*9.80665*.19,places=10)
        self.assertAlmostEqual(loaded[1]-zero[1],.05*9.80665*.10,places=10)
    def test_motion_bounds_and_payload_sensitivity(self):
        previous=[0,0]
        for case in read('torque_analysis.json')['cases']:
            for static,bound,prev in zip(case['max_static_Nm'],case['max_motion_bound_Nm'],previous):
                self.assertGreaterEqual(bound,static);self.assertGreater(static,prev)
            previous=case['max_static_Nm']
            for pose in case['poses']:
                for gravity,bound in zip(pose['gravity_Nm'],pose['motion_bound_Nm']):self.assertGreaterEqual(bound,abs(gravity))
    def test_spring_law(self):
        s=read('gravity_compensation.json')
        for p in s['poses']:
            force=max(0,s['effective_spring_k_N_m']*(p['length_mm']-s['equivalent_zero_force_length_mm'])/1000)
            self.assertAlmostEqual(force,p['force_N'],places=10)
    def test_native_reference_consistency(self):
        a=read('analysis/kinematic_audit.json')
        self.assertTrue(a['reopened']);self.assertFalse(a['missing_references'])
        self.assertEqual(len(a['reference_geometry_checks']),32)
        self.assertTrue(all(r['matches_saved_part'] for r in a['reference_geometry_checks']))
        self.assertTrue(all(c['health']=='11778' and not c['suppressed'] for c in a['final_constraints']))
        self.assertTrue(all(p['update_ok'] and not p['interferences'] for p in a['pose_audit']))
    def test_closed_meshes_and_coupon_envelope(self):
        meshes=read('analysis/stl_validation.json')
        self.assertEqual(len(meshes),31)
        for m in meshes:
            self.assertEqual(m['non_two_sided_edges'],0);self.assertTrue(m['within_220_cube_when_reoriented'])

if __name__=='__main__':unittest.main()
