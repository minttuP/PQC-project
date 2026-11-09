import numpy as np
import matplotlib.pyplot as plt
import qodec
from qdk import ec, qsharp, TargetProfile
from qdk.simulation import run_qir, NoiseConfig
from pathlib import Path
from c4_optimization import c4_improve_circuit
from functools import partial
from deq.runtime import Runtime
from qdk.simulation import NoiseConfig, run_qir, decoders
#from deq.circuit import model


def get_benchmarks(codename):
    if codename == "C4":
        return {
            "SPAM Z": str(qsharp.compile("TestSpamZ()")),
            #"cx_all Z": str(qsharp.compile("TestCnotZ()")),
            "syndrome Z": str(qsharp.compile("TestSyndromeZ()")),
            "SPAM X": str(qsharp.compile("TestSpamX()")),
            #"cx_all X": str(qsharp.compile("TestCnotX()")),
            "syndrome X": str(qsharp.compile("TestSyndromeX()")),
        }
    elif codename == "Rep3":
        return {
            "syndrome Z": str(qsharp.compile("TestSyndromeZ()")),
            "syndrome X": str(qsharp.compile("TestSyndromeX()")),
            "SPAM X": str(qsharp.compile("TestSpamX()")),
            "SPAM Z": str(qsharp.compile("TestSpamZ()"))
        }
    else: 
        return {}


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

def plot_data(data, ps, codename):
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for name, rows in data.items():
        ler = np.array([r[0] for r in rows]); err = np.array([r[1] for r in rows])
        ax.errorbar(ps, ler, yerr=err, marker="o", capsize=3, label=name)
    ax.plot(ps, ps, "k--", lw=1, label="logical = physical")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Physical error rate p"); ax.set_ylabel("Logical error rate (post-selected)")
    ax.set_title(codename + " code, bare-css/v1 protocol"); ax.legend(); ax.grid(True, which="both", alpha=0.3)
    plt.show()



def main(code_dict):
    code = qodec.Code(
        code_dict["name"],
        stabilizers=code_dict["stabilizers"],
        x=code_dict["x"],
        z=code_dict["z"],
    )
    profile = ec.CodeProfile(code)
    print(profile.logical_qubit_count, profile.distance())

    protocol = ec.build_qodec(code, strategy="bare-css/v1", strict=False)
    if code_dict["name"] == 'C4':
        protocol = c4_improve_circuit(protocol)

    report = ec.audit(protocol)
    if report.errors or report.warnings:
        raise ValueError(str(report))

    #for name, gadget in sorted(protocol.layers[0].gadgets.items()):
    #    print(name, gadget)   # inspect operands and outcomes

    available = set(protocol.layers[0].instruction_set.instructions)
    print("Logical instructions:", sorted(available))

    qsharp.init(target_profile=TargetProfile.Adaptive_RI)
    qsharp.eval(Path(code_dict["name"] + "_instructions.qs").read_text())
    benchmarks = get_benchmarks(code_dict["name"])

    ### Run simulation ###
    ps = np.logspace(-3, -0.5, 15)
    data = simulate(protocol, benchmarks, ps, code_dict["shots"])
    plot_data(data, ps, code_dict["name"])

    print("Check zero error rate")
    verification = simulate(protocol, benchmarks, np.array([0]), code_dict["shots"])
    print(verification)


# c4 error correction code
c4 = {
    "name": "C4",
    "stabilizers": ["X_0 X_1 X_2 X_3", "Z_0 Z_1 Z_2 Z_3"],
    "x": ["X_0 X_1", "X_0 X_2"],
    "z": ["Z_0 Z_2", "Z_0 Z_1"],
    "shots": 5000
}
#main(c4)


# [[3,1,1]] repetition code
rep3 = {
    "name": "Rep3",
    "stabilizers":["Z_0 Z_1", "Z_1 Z_2"],
    "x":["X_0 X_1 X_2"],
    "z":["Z_0"],
    "shots": 100000
}
main(rep3)

plt.show()