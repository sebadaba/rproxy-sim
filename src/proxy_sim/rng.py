"""Generador de números aleatorios reproducible."""

import numpy as np


def make_rng(seed: int) -> np.random.Generator:
    """Devuelve un Generator de numpy sembrado con `seed`.

    Pasar la misma instancia a todos los muestreos de una corrida garantiza
    que dos corridas con la misma semilla produzcan la misma secuencia.
    """
    return np.random.default_rng(seed)