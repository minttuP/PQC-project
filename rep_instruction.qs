// https://quantum.cloud.ibm.com/learning/en/courses/foundations-of-quantum-error-correction/correcting-quantum-errors/repetition-codes

import Std.Convert.IntAsDouble;
/// Bit-flip repetition codes [[n,1,n]] for odd n (3, 5, 7).
///
/// - Encode:   |ψ> on data[0], then CNOT(data[0] -> data[i]) for all i.
/// - Syndrome: ancilla i measures the parity of data[i] and data[i+1]
///             (n-1 ancillae; for n = 3 this is exactly your a1, a2).
/// - Decode:   rebuild the error pattern implied by the syndrome and flip the
///             qubits of the lighter of the two matching patterns
///             (equivalent to a majority vote). Corrects up to (n-1)/2 X errors.
///
/// Note: like rep3_B, this only protects against bit flips (X errors).
import Std.Arrays.*;
import Std.Measurement.*;
import Std.Math.*;
import Std.Random.*;

/// Generic repetition code. `errors` lists the data qubits that get an X error
/// (empty array = noiseless run). Returns (syndrome, final Z-basis data measurements).
operation addNoise(data: Qubit[], n: Int, k: Int) : Unit {
    // Adding random errors: error happens with gates with some propability. 
    // Simulates waiting time
    for i in 0..n-1 {
        for k in 0..k {
            H(data[i]); H(data[i]); 
        }
    }
}

operation apply_syndrome(data: Qubit[], anc: Qubit[], n: Int) : Unit {
    // Parity checks between neighbouring data qubits
    for i in 0..n - 2 {
        CNOT(data[i], anc[i]);
        CNOT(data[i + 1], anc[i]);
    }
}

operation correct_lookuptable(data: Qubit[], syndrome: Result[], n: Int) : Unit {
    // Reconstruct the error pattern with e[0] = false: e[i+1] = e[i] xor s[i].
    // The complement of that pattern has the same syndrome, so pick the lighter one.
    mutable e = [false, size = n];
    mutable weight = 0;
    for i in 0..n - 2 {
        let next = e[i] != (syndrome[i] == One);
        set e w/= i + 1 <- next;
        if next {
            set weight += 1;
        }
    }

    let val = (weight > n / 2);
    for i in 0..n - 1 {
        if e[i] != val {
            X(data[i]);
        }
    }
}

operation RepetitionCodeB(n : Int, k: Int) : (Result[], Result[]) {
    // Initialize
    use data = Qubit[n];       // initialised to |0>
    use anc = Qubit[n - 1];
    for i in 1..n - 1 {CNOT(data[0], data[i]);} // Entangle qubits

    addNoise(data, n, k);

    apply_syndrome(data, anc, n);
    let syndrome = MResetEachZ(anc);
    correct_lookuptable(data, syndrome, n);
    // Measure in Z basis
    let results = MResetEachZ(data);
    (syndrome, results)
}

operation RepetitionCodeA(n : Int, k: Int) : (Result[], Result[]) {
    // Initialize
    use data = Qubit[n];       // initialised to |0>
    use anc = Qubit[n - 1];
    for i in 1..n - 1 {CNOT(data[0], data[i]);} // Entangle qubits

    addNoise(data, n, k);
    let results = MResetEachZ(data);
    ([results[0]], results)
}

/// Parity-check matrix of the n-qubit repetition code: (n-1) x n.
function RepetitionH(n : Int) : Int[][] {
    mutable H = [];
    for c in 0..n-2 {
        mutable row = Repeated(0, n);
        set row w/= c <- 1;
        set row w/= c + 1 <- 1;
        set H += [row];
    }
    return H;
}

function BPDecode(H : Int[][], syndrome : Int[], p : Double, maxIter : Int) : Int[] {
    let m = Length(H);
    let n = Length(H[0]);
    let Lch = Log((1.0 - p) / p);   // prior LLR: positive = "no error"

    // Variable -> check messages start at the prior
    mutable v2c = Repeated(Repeated(0.0, n), m);
    for c in 0..m-1 {
        for v in 0..n-1 {
            if H[c][v] == 1 { set v2c w/= c <- (v2c[c] w/ v <- Lch); }
        }
    }

    mutable c2v = Repeated(Repeated(0.0, n), m);
    mutable est = Repeated(0, n);
    mutable done = false;

    for _ in 1..maxIter {
        if not done {
            // Check-node update (sign flipped if the syndrome bit is 1)
            for c in 0..m-1 {
                let sgn = if syndrome[c] == 1 { -1.0 } else { 1.0 };
                for v in 0..n-1 {
                    if H[c][v] == 1 {
                        mutable prod = 1.0;
                        for u in 0..n-1 {
                            if u != v and H[c][u] == 1 {
                                set prod *= Tanh(v2c[c][u] / 2.0);
                            }
                        }
                        let clamped = MinD(MaxD(prod, -0.999999), 0.999999);
                        set c2v w/= c <- (c2v[c] w/ v <- sgn * 2.0 * ArcTanh(clamped));
                    }
                }
            }

            // Posterior LLRs and hard decision (negative LLR = error)
            for v in 0..n-1 {
                mutable post = Lch;
                for c in 0..m-1 { set post += c2v[c][v]; }
                set est w/= v <- (if post < 0.0 { 1 } else { 0 });
            }

            // Stop if the estimate reproduces the syndrome
            mutable ok = true;
            for c in 0..m-1 {
                mutable par = 0;
                for v in 0..n-1 { set par += H[c][v] * est[v]; }
                if par % 2 != syndrome[c] { set ok = false; }
            }
            if ok { set done = true; }

            // Variable-node update (extrinsic: exclude the receiving check)
            if not done {
                for v in 0..n-1 {
                    for c in 0..m-1 {
                        if H[c][v] == 1 {
                            mutable total = Lch;
                            for c2 in 0..m-1 {
                                if c2 != c { set total += c2v[c2][v]; }
                            }
                            set v2c w/= c <- (v2c[c] w/ v <- total);
                        }
                    }
                }
            }
        }
    }
    return est;
}

operation RepetitionCodeC1(n : Int, k: Int, p: Double) : (Result[], Result[]) {
    // Initialize
    use data = Qubit[n];       // initialised to |0>
    use anc = Qubit[n - 1];
    for i in 1..n - 1 {CNOT(data[0], data[i]);} // Entangle qubits

    addNoise(data, n, k);

    apply_syndrome(data, anc, n);
    let syndrome = MResetEachZ(anc);
    let synd_mapped = Mapped(r -> r == One ? 1 | 0, syndrome);
    let H = RepetitionH(n);
    let est = BPDecode(H, synd_mapped, MaxD(p, 1e-6), n);

    for i in 0..n-1 {
        if est[i] == 1 { X(data[i]); }
    }


    // Measure in Z basis
    let results = MResetEachZ(data);
    (syndrome, results)
}

operation rep3_A() : (Result[], Result[]) { RepetitionCodeA(3, 32) }
operation rep5_A() : (Result[], Result[]) { RepetitionCodeA(5, 32) }
operation rep7_A() : (Result[], Result[]) { RepetitionCodeA(7, 32) }

operation rep3_B() : (Result[], Result[]) { RepetitionCodeB(3, 32) }
operation rep5_B() : (Result[], Result[]) { RepetitionCodeB(5, 32) }
operation rep7_B() : (Result[], Result[]) { RepetitionCodeB(7, 32) }

operation rep3_C1(p: Double) : (Result[], Result[]) { RepetitionCodeC1(3, 32, p) }
operation rep5_C1(p: Double) : (Result[], Result[]) { RepetitionCodeC1(5, 32, p) }
operation rep7_C1(p: Double) : (Result[], Result[]) { RepetitionCodeC1(7, 32, p) }
