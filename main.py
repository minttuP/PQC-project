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

def meas_to_string(meas):
    s = ""
    for r in meas:
        if "One" in str(r) or str(r) == "1":
            s += "1"
        else:
            s += "0"
    return s

decoders = {
    "rep3": [
        ["000", "001", "010", "100"], 
        ["111", "110", "101", "011"]
    ],
    "rep5": [
        ["00000", "10010", "01001", "11011", "10100", "00110", "11101", "01111", "01010", "11000", "00011", "10001", "11110", "01100", "10111", "00101"], 
        ["11111", "01101", "10110", "00100", "01011", "11001", "00010", "10000", "10101", "00111", "11100", "01110", "00001", "10011", "01000", "11010"]
    ]
}

def logical_error_rate(name, shots):
    if not shots:
        return np.nan, np.nan, 0

    ones = decoders[name.replace("_B()", "").replace("_A()", "")][1]
    # Count failures in the codewords
    fails = sum([meas_to_string(s[1]) in ones for s in shots])

    n = len(shots)
    p = fails / n
    print("fails: ", fails, ", shots: ", len(shots))

    errors = np.sqrt(max(p * (1 - p), 1e-12) / n)
    return p, errors, n

def simulate(qirs, ps, SHOTS):
    data = {name: [] for name in qirs}
    for name in qirs:
        qir = qsharp.compile(name)
        for p in ps:
            shots = run_qir(qir, shots=SHOTS, noise=make_noise(p), type="clifford")
            #print(Counter(str(r) for r in shots))
            data[name].append(logical_error_rate(name, shots))
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
    plot_data(data, ps, ax)

# Initialize 
qsharp.init(target_profile=TargetProfile.Adaptive_RI)
qsharp.eval(Path("rep_instruction.qs").read_text())

ps = np.logspace(-5, -1.5, 12)
main(["rep3_A()", "rep3_B()", "rep5_B()", "rep5_A()"], 10000, ps)
plt.show()

#main(["rep5_B()"], 200, [0])
