N_CLASSES_MAX = 10

# 10 colors
COLORS = [
    (0.0, 0.0, 1.0),  # blue
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (1.0, 1.0, 0.0),
    (0.0, 1.0, 1.0),
    (1.0, 0.0, 1.0),
    (0.5, 1.0, 0.0),
    (0.0, 0.5, 1.0),
    (1.0, 0.0, 0.5),
    (1.0, 0.5, 0.0),
]
assert len(COLORS) >= N_CLASSES_MAX, "not enough colors defined"
