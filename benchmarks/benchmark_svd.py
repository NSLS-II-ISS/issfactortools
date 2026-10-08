"""Compare the original full-SVD approach with the optimized analysis routines.

Run with a fixed BLAS thread count for reproducible comparisons:
OPENBLAS_NUM_THREADS=1 python benchmarks/benchmark_svd.py
"""

import argparse
from statistics import median
from time import perf_counter

import numpy as np
from numpy.testing import assert_allclose

from issfactortools.elements.mcrproject import DataSet
from issfactortools.elements.svd import compute_efa, doSVD


def legacy_svd(data):
    u, s, vh = np.linalg.svd(data, full_matrices=True)
    v = vh.T
    ac_u = np.array([np.sum(col[1:] * col[:-1]) for col in u.T])
    ac_v = np.array([np.sum(col[1:] * col[:-1]) for col in v.T])
    chisq = np.r_[np.cumsum((s ** 2)[::-1])[::-1][1:], 0]
    return u, s, v, chisq, ac_u, ac_v


def legacy_efa(dataset):
    _, nt = dataset.data.shape
    forward, backward = np.zeros((nt, nt - 1)), np.zeros((nt, nt - 1))
    for i in range(1, nt):
        s = legacy_svd(dataset.data[:, :i])[1]
        forward[:s.size, i - 1] = s
        s = legacy_svd(dataset.data[:, -i - 1:])[1]
        backward[:s.size, -i] = s
    return forward, backward


def measure(function, repeats):
    function()  # Warm up imports, allocation, and BLAS.
    timings = []
    for _ in range(repeats):
        start = perf_counter()
        function()
        timings.append(perf_counter() - start)
    return median(timings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rows', type=int, default=600)
    parser.add_argument('--columns', type=int, default=60)
    parser.add_argument('--repeats', type=int, default=3)
    args = parser.parse_args()
    data = np.random.default_rng(42).normal(size=(args.rows, args.columns))
    dataset = DataSet(np.arange(args.rows), {'index': np.arange(args.columns)}, data)
    old, new = legacy_svd(data), doSVD(data)
    assert_allclose(old[1], new[1])
    assert_allclose((new[0] * new[1]) @ new[2].T, data, atol=1e-12)
    for expected, actual in zip(legacy_efa(dataset), compute_efa(dataset)):
        assert_allclose(actual, expected, atol=1e-12)
    print(f'Matrix: {args.rows} x {args.columns}; median of {args.repeats} runs')
    for label, before, after in [
        ('SVD + diagnostics', lambda: legacy_svd(data), lambda: doSVD(data)),
        ('EFA', lambda: legacy_efa(dataset), lambda: compute_efa(dataset)),
    ]:
        old_time, new_time = measure(before, args.repeats), measure(after, args.repeats)
        print(f'{label}: {old_time:.4f}s -> {new_time:.4f}s ({old_time / new_time:.1f}x)')
    old_bytes = old[0].nbytes + old[2].nbytes
    new_bytes = new[0].nbytes + new[2].nbytes
    print(f'U + V storage: {old_bytes:,} -> {new_bytes:,} bytes ({old_bytes / new_bytes:.1f}x smaller)')


if __name__ == '__main__':
    main()
