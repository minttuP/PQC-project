from pathlib import Path

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


def gen_decoder_C2(n, iters=None, L=1):
    iters = iters or n
    out = [f"operation Decode{n}(data : Qubit[], syndrome: Result[]) : Unit {{"]
    for c in range(n - 1):
        out.append(f"    let s{c} = syndrome[{c}] == One ? -1 | 1;")
    adj = {v: [c for c in (v - 1, v) if 0 <= c < n - 1] for v in range(n)}
    v2c = {(c, v, 0): str(L) for c in range(n - 1) for v in (c, c + 1)}
    for t in range(1, iters + 1):
        c2v = {}
        for c in range(n - 1):
            for v, other in ((c, c + 1), (c + 1, c)):
                name = f"m{t}_{c}_{v}"
                out.append(f"    let {name} = s{c} * {v2c[(c, other, t-1)]};")
                c2v[(c, v)] = name
        for c in range(n - 1):
            for v in (c, c + 1):
                terms = [c2v[(c2, v)] for c2 in adj[v] if c2 != c]
                name = f"u{t}_{c}_{v}"
                out.append(f"    let {name} = {L}" + "".join(f" + {x}" for x in terms) + ";")
                v2c[(c, v, t)] = name
    for v in range(n):
        out.append(f"    let post{v} = {L}" + "".join(f" + {c2v[(c, v)]}" for c in adj[v]) + ";")
        out.append(f"    if post{v} < 0 {{ X(data[{v}]); }}")
    out.append("}")
    return "\n".join(out)

def gen_program_C2(n):
    return f"""
operation rep{n}_C2() : (Result[], Result[]) {{
    use data = Qubit[{n}];
    use anc = Qubit[{n-1}];
    for i in 1..{n-1} {{ CNOT(data[0], data[i]); }}

    // Add noise
    for i in 0..{n-1} {{
        for k in 0..32 {{
            H(data[i]); H(data[i]); 
        }}
    }}

    for i in 0..{n-2} {{
        CNOT(data[i], anc[i]);
        CNOT(data[i+1], anc[i]);
    }}
    let syndrome = MResetEachZ(anc);
    Decode{n}(data, syndrome);
    return (syndrome, MResetEachZ(data));
}}
"""



