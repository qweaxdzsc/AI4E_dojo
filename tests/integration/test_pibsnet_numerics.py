"""数值参考场的独立热方程极限、空间收敛与制造解消融校验。"""

import numpy as np

from ai4e_contrib.application.datasets.burgers.generate import solve as burgers_solve
from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import solve as trapezoid_solve


def test_burgers_heat_limit_matches_fourier_exact_evolution():
    x, t, actual = burgers_solve(nx=64, nt=9, mu=0, m=5, nu=0.1, rtol=1e-10, atol=1e-12)
    k = 2 * np.pi * np.fft.fftfreq(64, d=10 / 64)
    initial = np.exp(-((x - 5) ** 2) / 2)
    expected = np.fft.ifft(
        np.fft.fft(initial)[None] * np.exp(-0.1 * t[:, None] * k[None] ** 2), axis=1
    ).real
    np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=2e-9)


def test_trapezoid_grid_refinement_reduces_error():
    results = [trapezoid_solve(nx=n, ny=n, nt=2001, a=0.8)[-1] for n in (9, 17, 33)]
    coarse, middle, fine = [value[-1] for value in results]
    error_coarse = np.linalg.norm(coarse - fine[::4, ::4]) / coarse.size**0.5
    error_middle = np.linalg.norm(middle - fine[::2, ::2]) / middle.size**0.5
    assert error_middle < error_coarse / 2
    for values in results:
        assert np.isfinite(values).all()
        np.testing.assert_allclose(values[:, [0, -1], :], 1)
        np.testing.assert_allclose(values[:, :, [0, -1]], 1)
