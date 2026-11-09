// Logical instructions for the [[3,1,1]] repetition code (Rep3), built with
// qodec strategy "bare-css/v1". Declarations must match the built protocol:
//   prepare_z_all / prepare_x_all / syndrome / cx_all report 0 outcomes
//   measure_z_all / measure_x_all report 1 outcome (the logical readout)
// Check-based rejection is applied by the framework, not by this program.

operation prepare_z_all(block : Qubit) : Unit { body intrinsic; }
operation prepare_x_all(block : Qubit) : Unit { body intrinsic; }

@Measurement()
operation measure_z_all(block : Qubit) : Result { body intrinsic; }
@Measurement()
operation measure_x_all(block : Qubit) : Result { body intrinsic; }

operation cx_all(control : Qubit, target : Qubit) : Unit { body intrinsic; }
operation syndrome(block : Qubit) : Unit { body intrinsic; }

// State preparation and measurement, Z basis. Ideal outcome: [Zero]
operation TestSpamZ() : Result[] {
    use block = Qubit();
    prepare_z_all(block);
    let m = measure_z_all(block);
    [m]
}

// State preparation and measurement, X basis. Ideal outcome: [Zero]
operation TestSpamX() : Result[] {
    use block = Qubit();
    prepare_x_all(block);
    let m = measure_x_all(block);
    [m]
}

// Logical CNOT on |0>|0>. Ideal outcome: [Zero, Zero]
operation TestCnotZ() : Result[] {
    use (control, target) = (Qubit(), Qubit());
    prepare_z_all(control);
    prepare_z_all(target);
    cx_all(control, target);
    let mc = measure_z_all(control);
    let mt = measure_z_all(target);
    [mc, mt]
}

// Logical CNOT on |+>|+>. Ideal outcome: [Zero, Zero]
operation TestCnotX() : Result[] {
    use (control, target) = (Qubit(), Qubit());
    prepare_x_all(control);
    prepare_x_all(target);
    cx_all(control, target);
    let mc = measure_x_all(control);
    let mt = measure_x_all(target);
    [mc, mt]
}

// One syndrome round between preparation and measurement, Z basis.
operation TestSyndromeZ() : Result[] {
    use block = Qubit();
    prepare_z_all(block);
    syndrome(block);
    let m = measure_z_all(block);
    [m]
}

// One syndrome round between preparation and measurement, X basis.
operation TestSyndromeX() : Result[] {
    use block = Qubit();
    prepare_x_all(block);
    syndrome(block);
    let m = measure_x_all(block);
    [m]
}
