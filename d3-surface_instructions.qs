operation prepare_z_all(block : Qubit) : Unit { body intrinsic; }
operation prepare_x_all(block : Qubit) : Unit { body intrinsic; }

@Measurement()
operation measure_z_all(block : Qubit) : Result { body intrinsic; }
@Measurement()
operation measure_x_all(block : Qubit) : Result { body intrinsic; }
operation cx_all(control : Qubit, target : Qubit) : Unit { body intrinsic; }
//operation syndrome(block : Qubit) : Result[] { body intrinsic; }
operation syndrome(block : Qubit) : Unit { body intrinsic; }

operation TestSpamZ() : Result[] {
    use block = Qubit();
    prepare_z_all(block);
    let m = measure_z_all(block);
    [m]
}

operation TestSpamX() : Result[] {
    use block = Qubit();
    prepare_x_all(block);
    let m = measure_x_all(block);
    [m]
}

operation TestSyndromeZ() : Result[] {
    use block = Qubit();
    prepare_z_all(block);
    syndrome(block);
    let m = measure_z_all(block);
    [m]
}

operation TestSyndromeX() : Result[] {
    use block = Qubit();
    prepare_x_all(block);
    syndrome(block);
    let m = measure_x_all(block);
    [m]
}

operation TestSyndrome10Z() : Result[] {
    use block = Qubit();
    prepare_z_all(block);
    for _ in 1..10 { syndrome(block); }
    let m = measure_z_all(block);
    [m]
}