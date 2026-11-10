import numpy as np
from qdk.simulation import NoiseConfig, run_qir

def is_one(r):
    return "One" in str(r) or str(r) == "1"

### Function for part B ###
def logical_error_rate(shots, total, n_final=1):
    """
    Parses flat shot arrays where the last n_final elements are the final logical 
    readout(s), and all preceding elements are mid-circuit syndrome measurements.
    """
    parsed_shots = []
    for s in shots:
        if not isinstance(s, (list, np.ndarray)):
            s = [s]
        
        # Separate syndrome history from final readouts
        if len(s) > n_final:
            syndromes = s[:-n_final]
            final_readout = s[-n_final:]
        else:
            syndromes = []
            final_readout = s
        parsed_shots.append((syndromes, final_readout))

    # Post-select: keep shots where all syndrome/flag measurements are Zero (no 'One')
    try: 
        kept = [final for synd, final in parsed_shots if not any(is_one(r) for r in synd)]
    except:
        kept = [final for synd, final in parsed_shots]

    if not kept:
        return np.nan, np.nan, 0

    fails = sum(any(is_one(r) for r in final) for final in kept)
        
    n = len(kept)
    p = fails / n if n > 0 else 0
    print("fails: ", fails, ", shots: ", len(shots), ", kept: ", n, " all: ", total)

    errors = np.sqrt(max(p * (1 - p), 1e-12) / n) if n > 0 else np.nan
    return p, errors, n

"""
### Original function for part A ###
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
"""
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