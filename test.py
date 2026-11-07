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
    if codename == "c4":
        return {
            "SPAM Z": str(qsharp.compile("TestSpamZ()")),
            #"cx_all Z": str(qsharp.compile("TestCnotZ()")),
            "syndrome Z": str(qsharp.compile("TestSyndromeZ()")),
            "SPAM X": str(qsharp.compile("TestSpamX()")),
            #"cx_all X": str(qsharp.compile("TestCnotX()")),
            "syndrome X": str(qsharp.compile("TestSyndromeX()")),
        }
    else:
        return {}

def make_runtime(seed: int) -> Runtime:
    return Runtime(
        decoder="black-box-relay-bp",
        decoder_config={"parallel": 1, "seed": seed},
        coordinator="monolithic",
        controller="jit",
    )


def is_one(r):
    return "One" in str(r) or str(r) == "1"

def logical_error_rate(shots):
    kept = [s for s in shots if not any(is_one(r) for r in s[0])]  # post-select on flag = Zero
    if not kept:
        return np.nan, np.nan, 0
    fails = sum(any(is_one(r) for r in s[1]) for s in kept)
    n = len(kept)
    p = fails / n
    return p, np.sqrt(max(p * (1 - p), 1e-12) / n), n

def make_noise(p):
    noise = NoiseConfig()
    for gate in (noise.h, noise.cx):
        gate.set_depolarizing(p)
    noise.mresetz.x = p
    return noise

def simulate(protocol, qirs, ps):
    SHOTS = 5000
    data = {name: [] for name in qirs}

    for name, qir in qirs.items():
        for p in ps:
            shots = run_qir(qir, qodec=protocol, noise=make_noise(p),
                            type="stabilizer", shots=SHOTS, seed=42,
                            on_shot_failure="discard")
            data[name].append(logical_error_rate(shots))
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



def main(codename, code):
    protocol = ec.build_qodec(code, strategy="bare-css/v1", strict=False)
    if codename == 'c4':
        protocol = c4_improve_circuit(protocol)

    report = ec.audit(protocol)
    if report.errors or report.warnings:
        raise ValueError(str(report))

    available = set(protocol.layers[0].instruction_set.instructions)
    print("Logical instructions:", sorted(available))

    qsharp.init(target_profile=TargetProfile.Adaptive_RI)
    qsharp.eval(Path(codename + "_instructions.qs").read_text())
    benchmarks = get_benchmarks(codename)

    ### Run simulation ###
    ps = np.logspace(-3, -1.5, 8)
    data = simulate(protocol, benchmarks, ps)
    plot_data(data, ps, codename)


# c4 error correction code
c4 = qodec.Code(
    "C4",
    stabilizers=["X_0 X_1 X_2 X_3", "Z_0 Z_1 Z_2 Z_3"],
    x=["X_0 X_1", "X_0 X_2"],
    z=["Z_0 Z_2", "Z_0 Z_1"],
)
main("c4", c4)
print("done")
plt.show()