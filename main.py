import numpy as np
import matplotlib.pyplot as plt
import qodec
from qdk import ec, qsharp, TargetProfile
from pathlib import Path
from c4_optimization import c4_improve_circuit

from simulation import simulate

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



def plot_data(data, code_dict, ax):
    ps = code_dict["ps"]
    xs = np.logspace(np.log10(ps.min()), np.log10(ps.max()), 50)
    name = None
    for name, rows in data.items():
        slope, slope_err, c, npts = fit_slope(ps, rows)
        if not np.isnan(slope):
            ax.plot(xs, c * xs**slope, "--", color=code_dict["color"])
        print(name, " slope: ", slope)
        ler = np.array([r[0] for r in rows]); err = np.array([r[1] for r in rows])
        ax.errorbar(ps, ler, yerr=err, marker="o", capsize=3, label=code_dict["name"], color=code_dict["color"])

    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Physical error rate p"); ax.set_ylabel("Logical error rate (post-selected)")
    ax.set_title(name + " , bare-css/v1 protocol"); ax.legend(); ax.grid(True, which="both", alpha=0.3)

def main(code_dict, ax):
    code = qodec.Code(
        code_dict["name"],
        stabilizers=code_dict["stabilizers"],
        x=code_dict["x"],
        z=code_dict["z"],
    )
    profile = ec.CodeProfile(code)
    print(profile.logical_qubit_count, profile.distance())

    protocol = ec.build_qodec(code, strategy="flagged-css/v1", strict=False)
    if code_dict["name"] == 'C4':
        protocol = c4_improve_circuit(protocol)

    report = ec.audit(protocol)
    if report.errors or report.warnings:
        raise ValueError(str(report))

    for name, gadget in sorted(protocol.layers[0].gadgets.items()):
        print(name, gadget)   # inspect operands and outcomes

    available = set(protocol.layers[0].instruction_set.instructions)
    print("Logical instructions:", sorted(available))

    qsharp.init(target_profile=TargetProfile.Adaptive_RI)
    qsharp.eval(Path(code_dict["name"] + "_instructions.qs").read_text())
    benchmarks = {
        "syndrome Z": str(qsharp.compile("TestSyndromeZ()")),
        #"syndrome X": str(qsharp.compile("TestSyndromeX()")),
        }

    ### Run simulation ###
    data = simulate(protocol, benchmarks, code_dict["ps"], code_dict["shots"])
    plot_data(data, code_dict, ax)

    #print("Check zero error rate")
    #verification = simulate(protocol, benchmarks, np.array([0]), code_dict["shots"])
    #print(verification)

from codes import rep3, rep5, rep7
fig, ax = plt.subplots(figsize=(6, 4.5))
ax.plot([1e-3, 10**-1.5], [10**-3, 10**-1.5], "k--", lw=1, label="logical = physical")
main(rep3, ax)
main(rep5, ax)
main(rep7, ax)

#fig, ax1 = plt.subplots(figsize=(6, 4.5))
#ax1.plot([1e-3, 10**-1.5], [10**-3, 10**-1.5], "k--", lw=1, label="logical = physical")
#main(c4, ax1)
#main(d3, ax1)

plt.show()