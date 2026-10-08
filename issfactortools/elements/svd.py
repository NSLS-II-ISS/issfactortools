import numpy as np
import matplotlib.pyplot as plt


def gaussian(x, amplitude, center, sigma):
    return amplitude * np.exp(-np.power(x - center, 2) / np.power(np.sqrt(2) * sigma, 2))


def exponentialDecay(time, amplitude, tau):
    return amplitude * np.exp(-time / tau)


def creategraph(matrix, t, x, y, *args, fig=None):
    """Plot a matrix or a labeled selection of its rows or columns."""
    if fig is None:
        _, ax = plt.subplots()
    else:
        ax = fig.gca()
    ax.set(xlabel=x, ylabel=y, title=t)
    if args:
        num, orientation, label = args
        if orientation not in ("c", "r"):
            raise ValueError("orientation must be 'c' or 'r'")
        data = matrix[:, :num] if orientation == "c" else matrix[:num, :].T
        ax.plot(data, label=[label + str(i + 1) for i in range(data.shape[1])])
        ax.legend()
    else:
        ax.plot(matrix)
    plt.show()


def getRankedMatrices(number, matrix, rcd):
    if rcd == "r":
        # print("Row")
        return matrix[:number, :]
    elif rcd == "c":
        return matrix[:, :number]
    elif rcd == "d":
        m = np.diag(matrix)
        return m[:number, :number]


def getResiduals(uN, sN, vN, A):
    An = uN @ sN @ vN
    residuals = A - An
    return An, residuals


def getChiSqS(S):
    return np.sum((S**2))


def getChiSq(x):
    return np.sum((x**2))


def plot_data(
    x=None,
    data=None,
    ax=None,
    fmt="ks-",
    limits=None,
    yscale="log",
    labels=None,
    plot_title="",
    font=None,
):
    """Plot each data column once, respecting coordinates and display limits."""
    if ax is None:
        _, ax = plt.subplots()
    data = np.asarray(data)
    if x is None:
        x = np.arange(data.shape[0])
    x = np.asarray(x)
    ax.plot(x[:limits], data[:limits], fmt, label=labels)
    ax.set_yscale("log" if yscale is True else (yscale or "linear"))
    ax.set_title(plot_title, fontsize=font)
    if labels is not None:
        ax.legend()
    return ax


def getPicture(name, matrix, fig=None, font=None):
    if fig is not None:
        fig.set_title(name, fontsize=font)
        fig.imshow(matrix)
    else:
        plt.figure()
        plt.title(name)
        plt.imshow(matrix)
        plt.show()


def getSubset(startcolumns, endcolumns, matrix):
    return matrix[:, startcolumns:endcolumns]


def SVDNoise(A, noiseLevel, noise):
    noiseA = A + (noiseLevel * noise)
    (
        u,
        s,
        v,
    ) = np.linalg.svd(noiseA)
    return noiseA, u, s, v


def LRA(uMatrix, sMatrix, vMatrix, n, A, noiseLevel=None, fig=None, font=None):
    """Plot residual sums for ranks 1 through n-1 using incremental updates.

    vMatrix follows NumPy's Vh convention (unlike the V returned by doSVD).
    The explicit residual is retained so this also works with approximate
    factors, where the singular-value tail alone need not equal the residual.
    """
    if not isinstance(n, (int, np.integer)) or not 1 <= n <= len(sMatrix) + 1:
        raise ValueError("n must be between 1 and the number of singular values + 1")
    chiSqS = _get_lra_chisq(sMatrix)[: n - 1]
    chiSq = np.empty(n - 1)
    residual = np.array(A, dtype=np.result_type(A, uMatrix, sMatrix, vMatrix), copy=True)
    for i in range(n - 1):
        residual -= sMatrix[i] * np.outer(uMatrix[:, i], vMatrix[i])
        chiSq[i] = getChiSq(residual)
    if fig is None:
        _, fig = plt.subplots()
    ranks = np.arange(1, n)
    fig.plot(ranks, chiSq, ".-", label="Residuals")
    fig.plot(ranks, chiSqS, ".-", label="Singular Values")
    fig.legend()
    fig.set_xlabel("Rank(n)", fontsize=font)
    fig.set_ylabel("Chi Squared", fontsize=font)
    if noiseLevel is not None:
        fig.set_title("Rank vs Chi Squared for a noise level of " + str(noiseLevel), fontsize=font)
    return chiSqS, chiSq


def plotsingvalues(s, fig=None, font=None):  # plot a matrix of singular values
    if fig is not None:  # if the user has passed in their own figure, use that
        fig.semilogy(s, ".-", label="sN")
        fig.set_xlabel("Index", fontsize=font)
        fig.set_ylabel("Singular Value", fontsize=font)
        fig.legend()
        fig.set_title("Singular Values vs Index", fontsize=font)
    else:  # otherwise design a new plot for them
        plt.figure()
        plt.plot(s, "o-", label="sN")
        plt.xlabel("Index")
        plt.ylabel("Singular Value")
        plt.legend()
        plt.title("Singular Values vs Index")


def _getAutocorrelation(matrix, lag=1):
    """Return the unnormalized lagged product sum for each column."""
    matrix = np.asarray(matrix)
    if matrix.ndim != 2:
        raise ValueError("matrix must be two-dimensional")
    if not isinstance(lag, (int, np.integer)) or lag < 1:
        raise ValueError("lag must be a positive integer")
    return np.sum(matrix[lag:] * matrix[:-lag], axis=0)


def getAutocorrelation(matrix, lag=1, title=None, fig=None, font=None):
    autocorrelation = _getAutocorrelation(matrix, lag=lag)
    if fig is None:
        _, fig = plt.subplots()
    fig.plot(autocorrelation, "k.-")
    fig.axhline(0.8, color="r", linestyle="dashed")
    if title is not None:
        fig.set_title("Autocorrelation of " + title, fontsize=font)


def _get_lra_chisq(s):
    chisq = (np.cumsum((s**2)[::-1])[::-1])[1:]
    return np.concatenate((chisq, np.zeros(min(1, np.size(s)))))


def doSVD(A, full_matrices=False):
    """Compute SVD and rank diagnostics using compact factors by default.

    For an (m, n) matrix, U and V have min(m, n) columns. Set
    full_matrices=True when the complete orthonormal bases are needed.
    V is returned transposed relative to NumPy's Vh, as in earlier releases.
    """
    u, s, vT = np.linalg.svd(A, full_matrices=full_matrices)
    v = vT.T
    return u, s, v, _get_lra_chisq(s), _getAutocorrelation(u), _getAutocorrelation(v)


def plot_svd_results(
    x,
    t,
    u,
    s,
    v,
    lra_chisq,
    ac_u,
    ac_v,
    figure1,
    figure2,
    energy=None,
    n_cmp_show=3,
    n_val_show=25,
    font=8,
):

    ax_u = figure1.add_subplot(2, 1, 1)
    ax_v = figure1.add_subplot(2, 1, 2)

    ax_s = figure2.add_subplot(2, 1, 1)
    ax_ac = figure2.add_subplot(2, 1, 2)

    subsetu = getSubset(0, n_cmp_show, u)
    subsetv = getSubset(0, n_cmp_show, v)

    plot_data(
        x, subsetu, ax_u, fmt="-", yscale=False, plot_title="subset of U", font=font
    )  # , lab = "Componenets")  # 2
    plot_data(
        t, subsetv, ax_v, fmt="-", yscale=False, plot_title="subset of V", font=font
    )  # , lab = "Comp")  # 3

    plot_data(
        data=s,
        ax=ax_s,
        fmt="k.-",
        limits=n_val_show,
        yscale=True,
        labels="Singular Values",
        plot_title="Singular values",
        font=font,
    )  # 7
    plot_data(
        data=lra_chisq,
        ax=ax_s,
        fmt="bs-",
        limits=n_val_show,
        yscale=True,
        labels="Chi Squared",
        plot_title="Singular values",
        font=font,
    )  # 7

    plot_data(
        data=ac_u,
        ax=ax_ac,
        fmt="ks-",
        limits=n_val_show,
        labels="AC_U",
        yscale=False,
        plot_title="",
        font=font,
    )  # 3
    plot_data(
        data=ac_v,
        ax=ax_ac,
        fmt="r.-",
        limits=n_val_show,
        labels="AC_V",
        yscale=False,
        plot_title="autocorrelation",
        font=font,
    )  # 3


def eigen(sValue, m):
    covariance = (sValue**2) / (m - 1)
    return covariance


def REV(eigen, i, m, n):
    revi = eigen / ((m - i + 1) * (n - i + 1))
    return revi


def fTest(rev, eig, k, m, n):
    bigSum = 0
    j = k - 1
    while j < n:
        bigSum += (m - j + 1) * (n - j + 1)
        j = j + 1

    littleSum = 0
    j = k + 1
    while j < n:
        # print(j)
        littleSum += eig[j]

        j = j + 1
    F = (rev / littleSum) * (bigSum)
    return F


def fullFTest(sValues, m, n):
    cov = []
    rev = []
    ans = []
    index = 0
    rows, cols = sValues.shape
    print(sValues.shape)
    while index < rows:
        cov.append(eigen(sValues[index][index], m))
        rev.append(REV(cov[index], index, m, n))
        index = index + 1

    k = 0
    while k < rows:
        ans.append(fTest(rev[k], cov, k, m, n))
        k = k + 1

    plt.figure()
    plt.plot(cov, ".-")
    plt.title("Eigen")
    plt.xlabel("Index")
    plt.ylabel("Eigenvalue")
    plt.show()
    plt.figure()
    plt.title("Rev")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.plot(rev, ".-")
    plt.show()
    plt.figure()
    plt.plot(ans, ".-")
    plt.title("F")
    plt.xlabel("Index")
    plt.show()
    return ans


def compute_efa(dataset):
    """Compute forward/backward EFA spectra, preserving legacy window alignment.

    The forward windows are data[:, :i], and the backward windows are
    data[:, -i-1:] for i in range(1, nt). Only singular values are needed.
    """
    data = dataset.data
    _, nt = data.shape
    if nt == 0:
        raise ValueError("EFA requires at least one spectrum")
    ss_forward = np.zeros((nt, nt - 1))
    ss_backward = np.zeros((nt, nt - 1))
    for i in range(1, nt):
        forward = np.linalg.svd(data[:, :i], compute_uv=False)
        backward = np.linalg.svd(data[:, -i - 1 :], compute_uv=False)
        ss_forward[: forward.size, i - 1] = forward
        ss_backward[: backward.size, -i] = backward
    return ss_forward, ss_backward


def compute_fwefa(dataset, w=5):
    """Compute singular values for the legacy fixed-width EFA windows.

    Window starts run from w to nt-w (exclusive). An empty selection returns
    an array with zero rows and min(number of energy points, w) columns.
    """
    if not isinstance(w, (int, np.integer)) or w < 1:
        raise ValueError("w must be a positive integer")
    data = dataset.data
    nx, nt = data.shape
    starts = range(w, nt - w)
    ss = np.empty((len(starts), min(nx, w)))
    for row, start in enumerate(starts):
        ss[row] = np.linalg.svd(data[:, start : start + w], compute_uv=False)
    return ss
