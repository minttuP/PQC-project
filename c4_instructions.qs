@Measurement()
operation prepare_z_all(block : Qubit) : Result { body intrinsic; }
@Measurement()
operation prepare_x_all(block : Qubit) : Result { body intrinsic; }
@Measurement()
operation measure_z_all(block : Qubit) : (Result, Result) { body intrinsic; }
@Measurement()
operation measure_x_all(block : Qubit) : (Result, Result) { body intrinsic; }
operation cx_all(control : Qubit, target : Qubit) : Unit { body intrinsic; }
operation syndrome(block : Qubit) : Unit { body intrinsic; }

operation TestSpamZ() : (Result[], Result[]) {
    use block = Qubit();
    let reject = prepare_z_all(block);
    let (left, right) = measure_z_all(block);
    ([reject], [left, right])
}

operation TestSpamX() : (Result[], Result[]) {
    use block = Qubit();
    let reject = prepare_x_all(block);
    let (left, right) = measure_x_all(block);
    ([reject], [left, right])
}

operation TestCnotZ() : (Result[], Result[]) {
    use (control, target) = (Qubit(), Qubit());
    let rejectControl = prepare_z_all(control);
    let rejectTarget = prepare_z_all(target);
    cx_all(control, target);
    let (controlLeft, controlRight) = measure_z_all(control);
    let (targetLeft, targetRight) = measure_z_all(target);
    ([rejectControl, rejectTarget], [controlLeft, controlRight, targetLeft, targetRight])
}

operation TestCnotX() : (Result[], Result[]) {
    use (control, target) = (Qubit(), Qubit());
    let rejectControl = prepare_x_all(control);
    let rejectTarget = prepare_x_all(target);
    cx_all(control, target);
    let (controlLeft, controlRight) = measure_x_all(control);
    let (targetLeft, targetRight) = measure_x_all(target);
    ([rejectControl, rejectTarget], [controlLeft, controlRight, targetLeft, targetRight])
}

operation TestSyndromeZ() : (Result[], Result[]) {
    use block = Qubit();
    let reject = prepare_z_all(block);
    syndrome(block);
    let (left, right) = measure_z_all(block);
    ([reject], [left, right])
}

operation TestSyndromeX() : (Result[], Result[]) {
    use block = Qubit();
    let reject = prepare_x_all(block);
    syndrome(block);
    let (left, right) = measure_x_all(block);
    ([reject], [left, right])
}