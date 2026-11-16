import numpy as np 
c4 = {
    "name": "C4",
    "stabilizers": ["X_0 X_1 X_2 X_3", "Z_0 Z_1 Z_2 Z_3"],
    "x": ["X_0 X_1", "X_0 X_2"],
    "z": ["Z_0 Z_2", "Z_0 Z_1"],
    "shots": 5000,
    "ps": np.logspace(-3.5, -1, 12)
}


# [[3,1,1]] repetition code
rep3 = {
    "name": "Rep3",
    "stabilizers":["Z_0 Z_1", "Z_1 Z_2"],
    "x":["X_0 X_1 X_2"],
    "z":["Z_0"],
    "shots": 5000,#100000
    "ps": np.logspace(-3.5, -1, 12),
    "color": "tab:blue"
}

# [[5,1,1]] repetition code
rep5 = {
    "name": "Rep5",
    "stabilizers": ["Z_0 Z_1", "Z_1 Z_2", "Z_2 Z_3", "Z_3 Z_4"],
    "x":["X_0 X_1 X_2 X_3 X_4"],
    "z":["Z_0"],
    "shots": 5000,#100000
    "ps": np.logspace(-3.5, -1, 12), 
    "color": "tab:orange"
}

# [[7,1,1]] repetition code
rep7 = {
    "name": "Rep7",
    "stabilizers":["Z_0 Z_1", "Z_1 Z_2", "Z_2 Z_3", "Z_3 Z_4", "Z_4 Z_5", "Z_5 Z_6"],
    "x":["X_0 X_1 X_2 X_3 X_4 X_5 X_6"],
    "z":["Z_0"],
    "shots": 5000,#100000
    "ps": np.logspace(-3.5, -1, 12),
    "color": "tab:green"
}

#[[9,1,3]] d3 surface code
d3 = {
    "name": "d3-surface",
    "stabilizers": [
        # X-type: 2 bulk plaquettes + 2 boundary
        "X_0 X_1 X_3 X_4",
        "X_4 X_5 X_7 X_8",
        "X_1 X_2",
        "X_6 X_7",
        # Z-type: 2 bulk plaquettes + 2 boundary
        "Z_1 Z_2 Z_4 Z_5",
        "Z_3 Z_4 Z_6 Z_7",
        "Z_0 Z_3",
        "Z_5 Z_8",
    ],
    "x":["X_0 X_3 X_6"],  # left column
    "z":["Z_0 Z_1 Z_2"],  # top row
    "shots": 5000, 
    "ps": np.logspace(-3.5, -1, 12),
    "color": "tab:blue"
}