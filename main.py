import numpy as np
from qdk.simulation import NoiseConfig, run_qir
from qdk import qsharp, TargetProfile
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt
from instructions import gen_decoder_C2, gen_program_C2

def generate_instructions(qirs): 
    txt = ""
    if any(code in name for code in ["_A", "_B", "_C2"] for name in qirs):
        Path("rep_instruction.qs").read_text()
    if any("_C2" in name for name in qirs):
        for name in qirs:
            if "_C2" in name:
                n = int(name.split("_")[0].replace("rep", ""))
                txt += "\n" + gen_decoder_C2(n) + gen_program_C2(n)
    
    return txt
    

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
        if  r == qsharp.Result.One:
            s += "1"
        else:
            s += "0"
    return s

decoders = {
    "5_1_3": [
        ["00000", "10010", "01001", "11011", "10100", "00110", "11101", "01111", "01010", "11000", "00011", "10001", "11110", "01100", "10111", "00101"], 
        ["11111", "01101", "10110", "00100", "01011", "11001", "00010", "10000", "10101", "00111", "11100", "01110", "00001", "10011", "01000", "11010"]
    ],
    "steane": [
        ["0000000", "1010101", "0110011", "1100110", "0001111", "1011010", "0111100", "1101001"], 
        ["1111111", "0101010", "1001100", "0011001", "1110000", "0100101", "1000011", "0010110"]
    ]
}
def get_fails(name, shots): 
    if "rep" in name: 
        fails = 0
        for s in shots:
            result = sum([ r == qsharp.Result.One for r in s[1]])
            if result > len(s[1]) / 2 :
                fails += 1
        return fails
    else: 
        zeros = decoders[name.replace("_B()", "").replace("_A()", "")][0]
        return sum([meas_to_string(s[1]) not in zeros for s in shots])

def logical_error_rate(name, shots):
    if not shots:
        return np.nan, np.nan, 0

    # Count failures in the codewords
    fails = get_fails(name, shots)

    n = len(shots)
    p = fails / n
    print("fails: ", fails, ", shots: ", len(shots))

    errors = np.sqrt(max(p * (1 - p), 1e-12) / n)
    return p, errors, n

def simulate(qirs, ps, SHOTS, targetprofile):
    data = {name: [] for name in qirs}
    for name in qirs:
        if targetprofile == TargetProfile.Adaptive_RI: 
            qir = qsharp.compile(name + "()")
            for p in ps:
                shots = run_qir(qir, shots=SHOTS, noise=make_noise(p), type="clifford")
                #print(Counter(str(r) for r in shots))
                data[name].append(logical_error_rate(name, shots))
        elif targetprofile == TargetProfile.Unrestricted: 
            for p in ps:
                shots = qsharp.run(name + "(" + str(p) + ")", shots=SHOTS, noise=make_noise(p))
                #print(Counter(str(r) for r in shots))
                data[name].append(logical_error_rate(name, shots))
        else: 
            raise ValueError('No match for profile')
    return data

def plot_data(data, ps, ax):
    xs = np.logspace(np.log10(ps.min()), np.log10(ps.max()), 50)
    name = None
    for name, rows in data.items():
        ler = np.array([r[0] for r in rows]); err = np.array([r[1] for r in rows])
        ax.errorbar(ps, ler, yerr=err, marker="o", capsize=3, label=name.replace("()", ""))

    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Physical error rate p"); ax.set_ylabel("Logical error rate")
    #ax.set_title(name + " , bare-css/v1 protocol"); 
    ax.legend(); ax.grid(True, which="both", alpha=0.3)

def main(qirs, shots, ps, ax, targetprofile):
    qsharp.init(target_profile=targetprofile)
    qsharp.eval(generate_instructions(qirs))

    data = simulate(qirs, ps, shots, targetprofile)
    #print(data)
    ## Plot results ##
    plot_data(data, ps, ax)


ps = np.logspace(-5, -1.5, 12)
fig, ax = plt.subplots()
ax.plot(ps, ps, label="pL=p")

# Part A: plot different repetition codes
#main(["rep3_A", "rep5_A", "rep7_A"], 10000, ps, ax, TargetProfile.Adaptive_RI, "rep_instruction.qs")

#main(["rep3_B", "rep5_B", "rep7_B"], 10000, ps, ax, TargetProfile.Adaptive_RI, "rep_instruction.qs")

#main(["rep3_A", "rep3_B", "rep3_C"], 10000, ps, ax, TargetProfile.Adaptive_RI, "rep_instruction.qs")
#main(["rep5_A", "rep5_B", "rep5_C"], 10000, ps, ax, TargetProfile.Adaptive_RI, "rep_instruction.qs")
#main(["rep7_A", "rep7_B", "rep7_C"], 10000, ps, ax, TargetProfile.Adaptive_RI, "rep_instruction.qs")

#main(["rep3_C1", "rep5_C1", "rep7_C1"], 10000, ps, ax, TargetProfile.Unrestricted, "rep_instruction.qs")

main(["rep3_C2", "rep5_C2", "rep7_C2"], 10000, ps, ax, TargetProfile.Adaptive_RI)


plt.show()