import numpy as np
import matplotlib.pyplot as plt
import qodec
from qdk import ec, qsharp, TargetProfile
from pathlib import Path
from c4_optimization import c4_improve_circuit

from simulation import simulate

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
            "SPAM Z": str(qsharp.compile("TestSpamZ()")),
        }
    else: 
        return {}




def fit_slope(ps, rows, n_min_fails=20, p_max=0.1):
    p_L, err, n = (np.array(col) for col in zip(*rows))
    fails = n*p_L
    ps, p_L, err, fails = map(np.asarray, (ps, p_L, err, fails))

    mask = (fails >= n_min_fails) & (ps <= p_max) & (p_L > 0) & np.isfinite(err) & (err > 0)
    if mask.sum() < 3:
        print(f"Only {mask.sum()} usable points; need at least 3. "
              f"Increase shots or lower n_min_fails.")
        return np.nan, np.nan, np.nan, int(mask.sum())
    
    x, y = np.log10(ps[mask]), np.log10(p_L[mask])
    sigma = err[mask] / (p_L[mask] * np.log(10))   # propagate error to log10 space
    coeffs, cov = np.polyfit(x, y, 1, w=1 / sigma, cov="unscaled")
    slope, intercept = coeffs
    return slope, np.sqrt(cov[0, 0]), 10**intercept, mask.sum()



def plot_data(data, ps, codename):
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]; i=0
    xs = np.logspace(np.log10(ps.min()), np.log10(ps.max()), 50)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for name, rows in data.items():
        slope, slope_err, c, npts = fit_slope(ps, rows)
        if not np.isnan(slope):
            ax.plot(xs, c * xs**slope, "--", color=colors[i])
        print(name, " slope: ", slope)
        ler = np.array([r[0] for r in rows]); err = np.array([r[1] for r in rows])
        ax.errorbar(ps, ler, yerr=err, marker="o", capsize=3, label=name, color=colors[i])
        i +=1

    ax.plot(ps, ps, "k--", lw=1, label="logical = physical")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Physical error rate p"); ax.set_ylabel("Logical error rate (post-selected)")
    ax.set_title(codename + " code, bare-css/v1 protocol"); ax.legend(); ax.grid(True, which="both", alpha=0.3)

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
    data = simulate(protocol, benchmarks, code_dict["ps"], code_dict["shots"])
    plot_data(data, code_dict["ps"], code_dict["name"])

    #print("Check zero error rate")
    #verification = simulate(protocol, benchmarks, np.array([0]), code_dict["shots"])
    #print(verification)


# c4 error correction code
c4 = {
    "name": "C4",
    "stabilizers": ["X_0 X_1 X_2 X_3", "Z_0 Z_1 Z_2 Z_3"],
    "x": ["X_0 X_1", "X_0 X_2"],
    "z": ["Z_0 Z_2", "Z_0 Z_1"],
    "shots": 5000,
    "ps": np.logspace(-3.5, -1, 12)
}
main(c4)


# [[3,1,1]] repetition code
rep3 = {
    "name": "Rep3",
    "stabilizers":["Z_0 Z_1", "Z_1 Z_2"],
    "x":["X_0 X_1 X_2"],
    "z":["Z_0"],
    "shots": 5000,#100000
    "ps": np.logspace(-3.5, -1, 12)
}
main(rep3)

plt.show()