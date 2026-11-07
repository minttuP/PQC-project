import numpy as np
import matplotlib.pyplot as plt
import qodec
from qdk import ec, qsharp, TargetProfile
from qdk.simulation import run_qir, NoiseConfig
from pathlib import Path
from tempfile import TemporaryDirectory


def improve_syndrome(protocol, gadgets):
    reichardt_source = """
    R 4 5
    H 4
    CX 4 0
    CX 2 5
    CX 0 5
    CX 1 5
    CX 4 2
    CX 4 3
    CX 4 1
    CX 3 5
    H 4
    M 4 5
    """
    gadgets["syndrome"].circuit.source = reichardt_source
    gadgets["syndrome"] = ec.filled(gadgets["syndrome"])

    improved_syndrome_profile = ec.GadgetProfile(gadgets["syndrome"])
    print("Improved syndrome distance:", improved_syndrome_profile.distance())
    print(ec.audit(protocol))
    return gadgets, improved_syndrome_profile

def detect_analogous_hook_faults(protocol, gadgets, improved_syndrome_profile):

    # Detect analoguous 
    improved_calls = gadgets["syndrome"].circuit.calls()
    faults = [
        ec.FaultEvent.after(5, ec.Pauli("Z_5")),
        ec.FaultEvent.after(7, ec.Pauli("X_4"))
    ]
    effects = improved_syndrome_profile.effects_of(faults)

    for fault, effect in zip(faults, effects):
        call = improved_calls[fault.locations[0].after_call]
        print(f"{fault} ({call.mnemonic} {call.operands}) →")
        for reference in effect.checks + effect.readouts:
            equation = gadgets["syndrome"].resolve(reference).value(tuple)
            print(f"  {reference} = {[str(term) for term in equation]}")
        for reference in effect.frames:
            print(f"  {reference}")
        print()
    return gadgets

def improve_prepare(protocol, gadgets):
    flagged_preparation_source = """R 0 1 2 3 4
    H 0
    CX 0 4
    CX 0 1
    CX 0 2
    CX 0 3
    CX 0 4
    """
    preparation_suffixes = {
        "prepare_z_all": "M 4\n",
        "prepare_x_all": "H 0 1 2 3\nM 4\n",
    }

    for mnemonic, suffix in preparation_suffixes.items():
        gadget = gadgets[mnemonic]
        gadget.implements.flags = ["reject"]
        gadget.circuit.source = flagged_preparation_source + suffix
        gadget.readouts = [{"reject": ["circuit.readouts[0]"]}]
        gadgets[mnemonic] = ec.filled(gadget)
        print(mnemonic, "distance:", ec.GadgetProfile(gadgets[mnemonic]).distance())
    print(ec.audit(protocol))
    return gadgets

def c4_improve_circuit(protocol):
    gadgets = protocol.layers[0].gadgets
    gadgets, profile = improve_syndrome(protocol, gadgets)
    gadgets = detect_analogous_hook_faults(protocol, gadgets, profile)
    gadgets = improve_prepare(protocol, gadgets)

    protocol.description = (
        "C4 built with bare-css/v1, with self-checking syndrome extraction "
        "and single-flag preparation circuits."
    )
    print(ec.audit(protocol))

    with TemporaryDirectory() as directory:
        saved_path = protocol.save(directory, single_file=True)
        assert qodec.Qodec.load(saved_path) == protocol
    print("Round trip: OK")
    return protocol
