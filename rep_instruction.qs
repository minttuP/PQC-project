// https://quantum.cloud.ibm.com/learning/en/courses/foundations-of-quantum-error-correction/correcting-quantum-errors/repetition-codes

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

operation RepetitionCodeC(n : Int, k: Int) : (Result[], Result[]) {
    // Initialize
    use data = Qubit[n];       // initialised to |0>
    use anc = Qubit[n - 1];
    for i in 1..n - 1 {CNOT(data[0], data[i]);} // Entangle qubits

    addNoise(data, n, k);

    apply_syndrome(data, anc, n);
    let syndrome = MResetEachZ(anc);
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

operation rep3_C() : (Result[], Result[]) { RepetitionCodeC(3, 32) }
operation rep5_C() : (Result[], Result[]) { RepetitionCodeC(5, 32) }
operation rep7_C() : (Result[], Result[]) { RepetitionCodeC(7, 32) }
