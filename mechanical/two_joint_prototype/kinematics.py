"""Two-link planar SI model, with no serial, USB or motor I/O."""
import math
from joint_config import JOINTS
L1, L2 = .09, .10

def forward(q, check=True):
    if len(q)!=2: raise ValueError('Two joints required')
    if check:
        for cfg, angle in zip(JOINTS,q): cfg.check(angle)
    a,b=q
    return L1*math.cos(a)+L2*math.cos(a+b), L1*math.sin(a)+L2*math.sin(a+b)

def inverse(x,y):
    if not math.isfinite(x+y): raise ValueError('Non-finite target')
    c=(x*x+y*y-L1*L1-L2*L2)/(2*L1*L2)
    if not -1-1e-12<=c<=1+1e-12: raise ValueError('Unreachable target')
    b=math.acos(max(-1,min(1,c)))
    candidates=[]
    for elbow in (b,-b):
        a=math.atan2(y,x)-math.atan2(L2*math.sin(elbow),L1+L2*math.cos(elbow))
        try:
            for cfg,angle in zip(JOINTS,(a,elbow)): cfg.check(angle)
            candidates.append((a,elbow))
        except ValueError: pass
    if not candidates: raise ValueError('Target violates joint limits')
    return candidates[0]

def trajectory(start,end,duration,dt=.02,vmax=.1,amax=.2):
    """Minimum-jerk interpolation with analytic peak velocity/acceleration checks."""
    for q in (start,end): forward(q)
    if not all(math.isfinite(x) and x>0 for x in (duration,dt,vmax,amax)):
        raise ValueError('Positive finite time and limits required')
    delta=max(abs(b-a) for a,b in zip(start,end))
    if 1.875*delta/duration>vmax or 5.773503*delta/duration**2>amax:
        raise ValueError('Trajectory exceeds velocity/acceleration envelope')
    steps=max(1,math.ceil(duration/dt))
    for i in range(steps+1):
        u=i/steps;s=10*u**3-15*u**4+6*u**5
        yield duration*u,tuple(a+(b-a)*s for a,b in zip(start,end))
