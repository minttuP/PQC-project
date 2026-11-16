import numpy as np
from qdk.simulation import NoiseConfig, run_qir
from qdk import qsharp, TargetProfile
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt


def make_noise(p):
    noise = NoiseConfig()
    # Depolarizing on H, CZ and CX
    for gate in (noise.h, noise.cz, noise.cx):
        gate.set_depolarizing(p)
    # Bit flip on the qubit after measure/reset
    #noise.mresetz.x = p
    return noise

def is_one(r):
    return "One" in str(r) or str(r) == "1"

def logical_error_rate(shots):
    if not shots:
        return np.nan, np.nan, 0
    fails = 0
    for s in shots:
        result = sum([is_one(r) for r in s])
        if result > len(s) / 2 :
            fails += 1

    n = len(shots)
    p = fails / n
    print("fails: ", fails, ", shots: ", len(shots))

    errors = np.sqrt(max(p * (1 - p), 1e-12) / n)
    return p, errors, n

def simulate(qirs, ps, SHOTS):
    data = {name: [] for name in qirs}
    for circuit in qirs:
        qir = qsharp.compile(circuit)
        for p in ps:
            shots = run_qir(qir, shots=SHOTS, noise=make_noise(p), type="clifford")
            print(Counter(str(r) for r in shots))
            data[circuit].append(logical_error_rate(shots))
    return data

def plot_data(data, ps, ax):
    xs = np.logspace(np.log10(ps.min()), np.log10(ps.max()), 50)
    name = None
    for name, rows in data.items():
        ler = np.array([r[0] for r in rows]); err = np.array([r[1] for r in rows])
        ax.errorbar(ps, ler, yerr=err, marker="o", capsize=3, label=name)

    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Physical error rate p"); ax.set_ylabel("Logical error rate (post-selected)")
    ax.set_title(name + " , bare-css/v1 protocol"); ax.legend(); ax.grid(True, which="both", alpha=0.3)

def main(qirs, shots, ps):
    data = simulate(qirs, ps, shots)
    print(data)
    ## Plot results ##
    fig, ax = plt.subplots()
    ax.plot(ps, ps, label="pL=p")
    #plot_data(data, ps, ax)

# Initialize 
qsharp.init(target_profile=TargetProfile.Adaptive_RI)
qsharp.eval(Path("rep_instruction.qs").read_text())

ps = np.logspace(-5, -1.5, 12)
main(["rep3_A_Z()", "rep5_A_Z()", "rep7_A_Z()"], 100000, ps)
plt.show()

## TODO: write rep 5 and rep 7 codes, simulate them. The current codes are wrong. 