//  https://en.wikipedia.org/wiki/Five-qubit_error_correcting_code
// https://www.dhuality.com/posts/2022-09-27-qec513code/
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

function SameSyndrome5(a : Bool[], error: Pauli, qubit: Int) : Bool {
    mutable b = [];
    for g in Stabilizers5() {
        let p = g[qubit];
        set b += [p != PauliI and p != error];
    }

    mutable same = true;
    for i in 0..Length(a) - 1 {
        if a[i] != b[i] {
            set same = false;
        }
    }
    same
}


operation MeasureSyndrome5(data: Qubit[]) : Bool[] {
    mutable syndrome = [];
    for g in Stabilizers5() {
        use anc = Qubit();
        H(anc);
        Controlled ApplyPauli([anc], (g, data));
        H(anc);
        set syndrome += [MResetZ(anc) == One];
    }
    syndrome
}

operation rep5_A() : (Bool[], Result[]) {
    use data = Qubit[5];
    Encode5(data);
    // Measure syndrome
    let syndrome = MeasureSyndrome5(data);
    Adjoint Encode5(data);
    let m0 = M(data[0]); let m1 = M(data[1]); let m2 = M(data[2]); let m3 = M(data[3]); let m4 = M(data[4]);
    ResetAll(data);
    (syndrome, [m0, m1, m2, m3, m4])
}

operation rep5_B() : (Bool[], Result[]) {
    use data = Qubit[5];
    Encode5(data);
    // Measure syndrome
    let syndrome = MeasureSyndrome5(data);
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



operation Encode7(data : Qubit[]) : Unit is Adj + Ctl {
    // Put the input into the |0...0> / |0010110> coset representatives.
    CNOT(data[2], data[4]);
    CNOT(data[2], data[5]);

    // Pivots into superposition.
    H(data[0]);
    H(data[1]);
    H(data[3]);

    // Pivot 0 -> rest of h1 = {0,2,4,6}
    CNOT(data[0], data[2]);
    CNOT(data[0], data[4]);
    CNOT(data[0], data[6]);

    // Pivot 1 -> rest of h2 = {1,2,5,6}
    CNOT(data[1], data[2]);
    CNOT(data[1], data[5]);
    CNOT(data[1], data[6]);

    // Pivot 3 -> rest of h3 = {3,4,5,6}
    CNOT(data[3], data[4]);
    CNOT(data[3], data[5]);
    CNOT(data[3], data[6]);
}

function Supports7() : Int[][] {
    [[0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6]]
}
function PauliString7(p : Pauli, support : Int[]) : Pauli[] {
    mutable s = Repeated(PauliI, 7);
    for i in support {
        set s w/= i <- p;
    }
    s
}


operation MeasureSyndrome7(data : Qubit[], p : Pauli) : Int {
    mutable syndrome = 0;
    for k in 0..2 {
        use anc = Qubit();
        H(anc);
        Controlled ApplyPauli([anc], (PauliString7(p, Supports7()[k]), data));
        H(anc);
        if MResetZ(anc) == One {
            set syndrome += 1 <<< k;
        }
    }
    syndrome
}
//https://errorcorrectionzoo.org/c/steane
operation rep7_A() : (Int[], Result[]) {
    use data = Qubit[7];
    Encode7(data);

    let xErrorPos = MeasureSyndrome7(data, PauliZ); // 0 = none, otherwise 1-indexed qubit
    let zErrorPos = MeasureSyndrome7(data, PauliX);
    Adjoint Encode7(data);
    let m0 = M(data[0]); let m1 = M(data[1]); let m2 = M(data[2]); let m3 = M(data[3]); let m4 = M(data[4]); let m5 = M(data[5]); let m6 = M(data[6]);
    ResetAll(data);
    ([xErrorPos, zErrorPos], [m0, m1, m2, m3, m4, m5, m6])
}

operation rep7_B() : (Int[], Result[]) {
    use data = Qubit[7];
    Encode7(data);

    let xErrorPos = MeasureSyndrome7(data, PauliZ); // 0 = none, otherwise 1-indexed qubit
    let zErrorPos = MeasureSyndrome7(data, PauliX);
    if xErrorPos == 1 {
        X(data[0])
    } elif xErrorPos == 2 {
        X(data[1])
    } elif xErrorPos == 3 {
        X(data[2])
    } elif xErrorPos == 4 {
        X(data[3])
    } elif xErrorPos == 5 {
        X(data[4])
    } elif xErrorPos == 6 {
        X(data[5])
    } elif xErrorPos == 7 {
        X(data[6])
    } 
    
    if zErrorPos == 1 {
        Z(data[0])
    } elif zErrorPos == 2 {
        Z(data[1])
    } elif zErrorPos == 3 {
        Z(data[2])
    } elif zErrorPos == 4 {
        Z(data[3])
    } elif zErrorPos == 5 {
        Z(data[4])
    } elif zErrorPos == 6 {
        Z(data[5])
    } elif zErrorPos == 7 {
        Z(data[6])
    } 
    Adjoint Encode7(data);
    let m0 = M(data[0]); let m1 = M(data[1]); let m2 = M(data[2]); let m3 = M(data[3]); let m4 = M(data[4]); let m5 = M(data[5]); let m6 = M(data[6]);
    ResetAll(data);
    ([xErrorPos, zErrorPos], [m0, m1, m2, m3, m4, m5, m6])
}