import numpy as np
from qdk.simulation import NoiseConfig, run_qir

def is_one(r):
    return "One" in str(r) or str(r) == "1"

def logical_error_rate(shots, total):
    try: 
        kept = [s for s in shots if not any(is_one(r) for r in s[0])]  # post-select on flag = Zero
    except:
        kept = shots

    if not kept:
        return np.nan, np.nan, 0
    try: 
        fails = sum(any(is_one(r) for r in s[1]) for s in kept)
    except: 
        fails = sum(any(is_one(r) for r in s) for s in kept)
    n = len(kept)
    p = fails / n
    print("fails: ", fails, ", shots: ", len(shots), ", kept: ", n)

    errors = np.sqrt(max(p * (1 - p), 1e-12) / n)
    return p, errors, n

def make_noise(p):
    noise = NoiseConfig()
    for gate in (noise.h, noise.cx, noise.cz):
        gate.set_depolarizing(p)
    noise.mresetz.x = p
    return noise

def simulate(protocol, qirs, ps, SHOTS):
    data = {name: [] for name in qirs}

    for name, qir in qirs.items():
        print(name)
        for p in ps:
            shots = run_qir(qir, qodec=protocol, noise=make_noise(p),
                            type="stabilizer", shots=SHOTS, seed=42,
                            on_shot_failure="discard")
            data[name].append(logical_error_rate(shots, SHOTS))
        print("done:", name)
    return data