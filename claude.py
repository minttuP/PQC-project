import numpy as np
import matplotlib.pyplot as plt
import qodec
from qdk import ec, qsharp, TargetProfile
from qdk.simulation import run_qir, NoiseConfig

# 1. Define the C4 code and build + audit a qodec
c4 = qodec.Code(
    "C4",
    stabilizers=["X_0 X_1 X_2 X_3", "Z_0 Z_1 Z_2 Z_3"],
    x=["X_0 X_1", "X_0 X_2"],
    z=["Z_0 Z_2", "Z_0 Z_1"],
)
protocol = ec.build_qodec(c4, strategy="bare-css/v1", strict=False)

report = ec.audit(protocol)
if report.errors or report.warnings:
    raise ValueError(str(report))

available = set(protocol.layers[0].instruction_set.instructions)
print("Logical instructions:", sorted(available))

# 2. Declare logical instructions in Q# and define experiments
qsharp.init(target_profile=TargetProfile.Adaptive_RI)
qsharp.eval("""
@Measurement()
operation prepare_z_all(block : Qubit) : Result { body intrinsic; }
@Measurement()
operation prepare_x_all(block : Qubit) : Result { body intrinsic; }
@Measurement()
operation measure_z_all(block : Qubit) : (Result, Result) { body intrinsic; }
@Measurement()
operation measure_x_all(block : Qubit) : (Result, Result) { body intrinsic; }
operation syndrome(block : Qubit) : Unit { body intrinsic; }

operation SpamZ() : (Result[], Result[]) {
    use block = Qubit();
    let reject = prepare_z_all(block);
    let (a, b) = measure_z_all(block);
    ([reject], [a, b])
}
operation SpamX() : (Result[], Result[]) {
    use block = Qubit();
    let reject = prepare_x_all(block);
    let (a, b) = measure_x_all(block);
    ([reject], [a, b])
}
operation MemoryZ() : (Result[], Result[]) {
    use block = Qubit();
    let reject = prepare_z_all(block);
    syndrome(block);
    let (a, b) = measure_z_all(block);
    ([reject], [a, b])
}
""")

experiments = {"SPAM Z": ("SpamZ()", {"prepare_z_all", "measure_z_all"}),
               "SPAM X": ("SpamX()", {"prepare_x_all", "measure_x_all"}),
               "Memory Z (1 syndrome round)": ("MemoryZ()", {"prepare_z_all", "syndrome", "measure_z_all"})}

# 3. Compile each experiment to QIR
qirs = {}
for name, (entry, needed) in experiments.items():
    if needed <= available:
        qirs[name] = str(qsharp.compile(entry))
    else:
        print(f"Skipping {name}: qodec lacks {needed - available}")

# 4. Helpers: a shot is a logical error if any logical result is One
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

# 5. Sweep the physical error rate
ps = np.logspace(-3, -1.5, 8)
SHOTS = 5000
data = {name: [] for name in qirs}

for name, qir in qirs.items():
    for p in ps:
        shots = run_qir(qir, qodec=protocol, noise=make_noise(p),
                        type="stabilizer", shots=SHOTS, seed=42,
                        on_shot_failure="discard")
        data[name].append(logical_error_rate(shots))
    print("done:", name)

# 6. Plot
fig, ax = plt.subplots(figsize=(6, 4.5))
for name, rows in data.items():
    ler = np.array([r[0] for r in rows]); err = np.array([r[1] for r in rows])
    ax.errorbar(ps, ler, yerr=err, marker="o", capsize=3, label=name)
ax.plot(ps, ps, "k--", lw=1, label="logical = physical")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Physical error rate p"); ax.set_ylabel("Logical error rate (post-selected)")
ax.set_title("C4 code, bare-css/v1 protocol"); ax.legend(); ax.grid(True, which="both", alpha=0.3)
plt.show()

for name, rows in data.items():
    print(name, [f"{r[0]:.4f} (kept {r[2]}/{SHOTS})" for r in rows])