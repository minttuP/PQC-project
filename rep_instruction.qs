// https://quantum.cloud.ibm.com/learning/en/courses/foundations-of-quantum-error-correction/correcting-quantum-errors/repetition-codes

operation rep3_A() : (Result[], Result[]) {
    use (q0, q1, q2) = (Qubit(), Qubit(), Qubit()); // Initialize to 0 state

    // Entangle qubits
    CNOT(q0, q1); CNOT(q0, q2);

    // Apply syndrome
    use (a1, a2) = (Qubit(), Qubit());
    // Apply CNOTs to ancillae
    CNOT(q0, a1); CNOT(q1, a1);
    CNOT(q1, a2); CNOT(q2, a2);

    let m1 = M(a1); let m2 = M(a2);

    // Measure in Z basis
    ([m1, m2], [M(q0), M(q1), M(q2)])
}

operation rep3_B() : (Result[], Result[]) {
    use (q0, q1, q2) = (Qubit(), Qubit(), Qubit()); // Initialize to 0 state

    // Entangle qubits
    CNOT(q0, q1); CNOT(q0, q2);

    use (a1, a2) = (Qubit(), Qubit());

    // Apply CNOTs to ancillae
    CNOT(q0, a1); CNOT(q1, a1);
    CNOT(q1, a2); CNOT(q2, a2);

    let m1 = M(a1);
    let m2 = M(a2);
    if (m1== One){
        if (m2 == One) { // 11
            X(q1)
        } else { // 10
            X(q0)
        }
    } else { //a1 == 0
        if (m2 == One) { // 01
            X(q2)
        } // No correction needed for 00.      
    }

    // Measure in Z basis
    ([m1, m2], [M(q0), M(q1), M(q2)])
}
//  https://en.wikipedia.org/wiki/Five-qubit_error_correcting_code
// https://www.dhuality.com/posts/2022-09-27-qec513code/
operation rep5_A() : (Result[], Result[]) {
    use (q0, q1, q2, q3, q4) = (Qubit(), Qubit(), Qubit(), Qubit(), Qubit()); // Initialize to 0 state

    // Entangle qubits
    CNOT(q0, q1); CNOT(q0, q2); CNOT(q0, q3); CNOT(q0, q4);

    // Apply syndrome
    use (a1, a2, a3, a4) = (Qubit(), Qubit(), Qubit(), Qubit());
    // Apply controls to ancillae
    // XZZXI
    CNOT(q0, a1); CZ(q1, a1); CZ(q2, a1); CNOT(q3, a1);
    // IXZZX 
    CNOT(q1, a2); CZ(q2, a2); CZ(q3, a2); CNOT(q4, a2);
    // XIXZZ 
    CNOT(q0, a3); CNOT(q2, a3); CZ(q3, a3); CZ(q4, a3);
    // ZXIXZ
    CZ(q0, a4); CNOT(q1, a4); CNOT(q3, a4); CZ(q4, a4);

    let m1 = M(a1); let m2 = M(a2); let m3 = M(a3); let m4 = M(a4);

    // Measure in Z basis
    ([m1, m2, m3, m4], [M(q0), M(q1), M(q2), M(q3), M(q4)])
}

operation rep7_A() : Result[] {
    use (q0, q1, q2, q3, q4, q5, q6) = (Qubit(), Qubit(), Qubit(), Qubit(), Qubit(), Qubit(), Qubit()); // Initialize to 0 state

    // Entangle qubits
    CNOT(q0, q1); CNOT(q0, q2); CNOT(q0, q3); CNOT(q0, q4); CNOT(q0, q5); CNOT(q0, q6);

    // Apply syndrome
    use (a1, a2, a3, a4, a5, a6) = (Qubit(), Qubit(), Qubit(), Qubit(), Qubit(), Qubit());
    // Apply CNOTs to ancillae
    // TODO ???

    // Measure in Z basis
    [M(q0), M(q1), M(q2), M(q3), M(q4), M(q5), M(q6)]
}



function Stabilizers5() : Pauli[][] {
    [
        [PauliX, PauliZ, PauliZ, PauliX, PauliI],
        [PauliI, PauliX, PauliZ, PauliZ, PauliX],
        [PauliX, PauliI, PauliX, PauliZ, PauliZ],
        [PauliZ, PauliX, PauliI, PauliX, PauliZ]
    ]
}

operation Encode5(data : Qubit[]) : Unit is Adj + Ctl {
    H(data[0]);
    for i in 1..4 {
        CNOT(data[0], data[i]);
    }
    ApplyToEachCA(H, data);
    for i in 0..4 {
        CZ(data[i], data[(i + 1) % 5]);
    }
}

function SameSyndrome5(syndrome : Result[], error: Pauli, qubit: Int) : Bool {
    mutable b = [];
    for g in Stabilizers5() {
        let p = g[qubit];
        set b += [p != PauliI and p != error];
    }

    mutable a = [];
    for res in syndrome {
        set a += [res == One]
    }

    mutable same = true;
    for i in 0..Length(a) - 1 {
        if a[i] != b[i] {
            set same = false;
        }
    }
    same
}

operation rep5_B() : (Result[], Result[]) {
    use data = Qubit[5];
    Encode5(data);

    // Measure syndrome
    mutable syndrome = [];
    for g in Stabilizers5() {
        use anc = Qubit();
        H(anc);
        Controlled ApplyPauli([anc], (g, data));
        H(anc);
        set syndrome += [MResetZ(anc)];
    }

    // Correct errors
    for q in 0..4 {
        for p in [PauliX, PauliY, PauliZ] {
            if SameSyndrome5(syndrome, p, q) {
                ApplyPauli([p], [data[q]]);
            }
        }
    }

    Adjoint Encode5(data);
    let m0 = M(data[0]); let m1 = M(data[1]); let m2 = M(data[2]); let m3 = M(data[3]); let m4 = M(data[4]);
    ResetAll(data);
    (syndrome, [m0, m1, m2, m3, m4])
}

operation rep7_B_Z() : Result[] {
    use (q0, q1, q2, q3, q4, q5, q6) = (Qubit(), Qubit(), Qubit(), Qubit(), Qubit(), Qubit(), Qubit()); // Initialize to 0 state

    // Entangle qubits
    CNOT(q0, q1); CNOT(q0, q2); CNOT(q0, q3); CNOT(q0, q4); CNOT(q0, q5); CNOT(q0, q6);

    // Apply syndrome
    use (a1, a2, a3, a4, a5, a6) = (Qubit(), Qubit(), Qubit(), Qubit(), Qubit(), Qubit());
    // TODO ???: Apply stabilizers, correct errors

    // Measure in Z basis
    [M(q0), M(q1), M(q2), M(q3), M(q4), M(q5), M(q6)]
}