"""Offline configuration. Pulse endpoints are intentionally uncommissioned."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class JointConfig:
    name: str
    minimum: float
    maximum: float
    encoder_counts: int = 4096
    encoder_zero: int = 0
    direction: int = 1
    calibration_id: str = 'UNVALIDATED'
    pulse_min_us: float | None = None
    pulse_max_us: float | None = None

    def check(self, angle):
        if not math.isfinite(angle) or not self.minimum <= angle <= self.maximum:
            raise ValueError(f'{self.name}: joint limit or non-finite value')
        return angle

    def measured_angle(self, count):
        if not isinstance(count, int) or not 0 <= count < self.encoder_counts:
            raise ValueError('Invalid absolute encoder count')
        delta = (count-self.encoder_zero+self.encoder_counts//2)%self.encoder_counts-self.encoder_counts//2
        return self.direction * delta * 2*math.pi/self.encoder_counts

    def command_pulse(self, angle):
        self.check(angle)
        if self.calibration_id == 'UNVALIDATED' or self.pulse_min_us is None or self.pulse_max_us is None:
            raise RuntimeError('Pulse calibration must be measured before any hardware use')
        return self.pulse_min_us+(angle-self.minimum)/(self.maximum-self.minimum)*(self.pulse_max_us-self.pulse_min_us)

JOINTS = (JointConfig('shoulder_lift', 0, math.radians(75)),
          JointConfig('elbow_flex', 0, math.radians(120)))

@dataclass(frozen=True)
class JointState:
    timestamp_s: float
    commanded_rad: tuple[float, float]
    measured_rad: tuple[float, float] | None
    calibration_id: str
    source: str
    valid: bool

    def to_record(self):
        if not math.isfinite(self.timestamp_s):
            raise ValueError('Invalid timestamp')
        for cfg, q in zip(JOINTS, self.commanded_rad, strict=True): cfg.check(q)
        if self.valid and (self.measured_rad is None or self.source not in ('simulated','encoder')):
            raise ValueError('Valid observation requires an explicit source and measurement')
        if self.measured_rad is not None and (len(self.measured_rad)!=2 or not all(math.isfinite(q) for q in self.measured_rad)):
            raise ValueError('Invalid measurement')
        from dataclasses import asdict
        return asdict(self)
