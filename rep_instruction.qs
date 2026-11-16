// https://quantum.cloud.ibm.com/learning/en/courses/foundations-of-quantum-error-correction/correcting-quantum-errors/repetition-codes

operation rep3_A_Z() : Result[] {
    use (q0, q1, q2) = (Qubit(), Qubit(), Qubit()); // Initialize to 0 state

    // Entangle qubits
    CNOT(q0, q1); CNOT(q0, q2);

    // Apply syndrome
    use (a1, a2) = (Qubit(), Qubit());
    // Apply CNOTs to ancillae
    CNOT(q0, a1); CNOT(q1, a1);
    CNOT(q1, a2); CNOT(q2, a2);

    // Measure in Z basis
    [M(q0), M(q1), M(q2)]
}

// 
operation rep5_A_Z() : Result[] {
    use (q0, q1, q2, q3, q4) = (Qubit(), Qubit(), Qubit(), Qubit(), Qubit()); // Initialize to 0 state

    // Entangle qubits
    CNOT(q0, q1); CNOT(q0, q2); CNOT(q0, q3); CNOT(q0, q4);

    // Apply syndrome
    use (a1, a2, a3, a4) = (Qubit(), Qubit(), Qubit(), Qubit());
    // Apply CNOTs to ancillae
    // TODO ???

    // Measure in Z basis
    [M(q0), M(q1), M(q2), M(q3), M(q4)]
}

operation rep7_A_Z() : Result[] {
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

operation rep3_B_Z() : Result[] {
    use (q0, q1, q2) = (Qubit(), Qubit(), Qubit()); // Initialize to 0 state

    // Entangle qubits
    CNOT(q0, q1); CNOT(q0, q2);

    use (a1, a2) = (Qubit(), Qubit());

    // Apply CNOTs to ancillae
    CNOT(q0, a1); CNOT(q1, a1);
    CNOT(q1, a2); CNOT(q2, a2);

    if (M(a1)== One){
        if (M(a2) == One) { // 11
            X(q1)
        } else { // 10
            X(q0)
        }
    } else { //a1 == 0
        if (M(a2) == One) { // 01
            X(q2)
        } // No correction needed for 00.      
    }

    // Measure in Z basis
    [M(q0), M(q1), M(q2)]
}

operation rep5_B_Z() : Result[] {
    use (q0, q1, q2, q3, q4) = (Qubit(), Qubit(), Qubit(), Qubit(), Qubit()); // Initialize to 0 state

    // Entangle qubits
    CNOT(q0, q1); CNOT(q0, q2); CNOT(q0, q3); CNOT(q0, q4);

    // Apply syndrome
    use (a1, a2, a3, a4) = (Qubit(), Qubit(), Qubit(), Qubit());
    // Apply CNOTs to ancillae
    // TODO ???

    // TODO ???
    if (M(a1)== One){
        if (M(a2) == One) { 
            if (M(a3) == One) { 
                if (M(a4) == One) {

                } else {

                }
            } else { 
                if (M(a4) == One) { 

                } else { 

                }
            }
        } else { 
            if (M(a3) == One) { 
                if (M(a4) == One) { 

                } else { 

                }
            } else { 
                if (M(a4) == One) { 

                } else { 

                }
            }
        }
    } else { //a1 == 0
        if (M(a2) == One) { 
            if (M(a3) == One) { 
                if (M(a4) == One) { // 0111

                } else { // 0110

                }
            } else { 
                if (M(a4) == One) { // 0101

                } else { // 0100

                }
            }
        } else { 
            if (M(a3) == One) { 
                if (M(a4) == One) { // 0011

                } else { // 0010

                }
            } else {
                if (M(a4) == One) { // 0001

                } else { // 0000

                }
            }
        }    
    }   

    // Measure in Z basis
    [M(q0), M(q1), M(q2), M(q3), M(q4)]
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