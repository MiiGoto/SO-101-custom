"""Offline-only shared six-joint API contract. No serial or real motor driver."""
from dataclasses import dataclass
import math
from typing import Mapping

JOINTS=('shoulder_pan','shoulder_lift','elbow_flex','wrist_flex','wrist_roll','gripper')

@dataclass(frozen=True)
class JointSample:
    actual_rad: Mapping[str,float]
    timestamp_s: float
    valid: bool
    calibration_id: str
    source: str  # measured hardware, or explicitly simulated

class OfflineJointContract:
    def __init__(self):
        self.connected=False
        self.sample=None
        self.targets={n:0. for n in JOINTS}
        self.limits={n:(-math.radians(80),math.radians(80)) for n in JOINTS[:4]}
        self.limits.update(wrist_roll=(-math.pi/2,math.pi/2),gripper=(0,math.pi/3))

    def connect(self): self.connected=True
    def disconnect(self): self.connected=False
    def set_simulated_observation(self,sample):
        if sample.source!='simulated': raise ValueError('This mock accepts only explicitly simulated observations')
        if set(sample.actual_rad)!=set(JOINTS): raise ValueError('Six measured joints required')
        if not all(math.isfinite(x) for x in sample.actual_rad.values()): raise ValueError('Non-finite observation')
        if not math.isfinite(sample.timestamp_s): raise ValueError('Non-finite time')
        self.sample=JointSample(dict(sample.actual_rad),sample.timestamp_s,sample.valid,sample.calibration_id,sample.source)
    def read_joint_positions(self,now_s):
        if not self.connected: raise ConnectionError('Disconnected')
        if self.sample is None or not self.sample.valid: raise RuntimeError('No valid observation')
        if not math.isfinite(now_s) or not 0<=now_s-self.sample.timestamp_s<=.05: raise RuntimeError('Stale or future observation')
        return JointSample(dict(self.sample.actual_rad),self.sample.timestamp_s,self.sample.valid,self.sample.calibration_id,self.sample.source)
    def write_joint_targets(self,targets_rad,now_s):
        self.read_joint_positions(now_s)
        if set(targets_rad)!=set(JOINTS): raise ValueError('Six named targets required')
        for n,x in targets_rad.items():
            if not math.isfinite(x) or not self.limits[n][0]<=x<=self.limits[n][1]: raise ValueError('Target outside limits')
        self.targets=dict(targets_rad)
        return dict(self.targets)
    def calibrate(self): raise NotImplementedError('No hardware calibration in this offline contract')
    def home(self): raise NotImplementedError('Collision-checked trajectory is required')
