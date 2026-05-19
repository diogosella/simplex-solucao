import numpy as np
from scipy.optimize import linprog


def resolver(tipo, c, A_ub, b_ub):
    c_arr = np.asarray(c, dtype=float)
    objetivo = -c_arr if tipo == "max" else c_arr

    resultado = linprog(
        objetivo,
        A_ub=np.asarray(A_ub, dtype=float),
        b_ub=np.asarray(b_ub, dtype=float),
        bounds=[(0, None)] * len(c_arr),
        method="highs-ds",
    )

    if not resultado.success:
        return None

    x = resultado.x
    z = -resultado.fun if tipo == "max" else resultado.fun
    return x, float(z)
