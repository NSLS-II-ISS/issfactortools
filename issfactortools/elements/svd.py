from matplotlib import pyplot as plt
import numpy as np
np.set_printoptions(threshold=np.inf)

def gaussian(x, amplitude, center, sigma): #calculate gaussian function
    return amplitude * np.exp(-np.power(x - center, 2) / np.power(np.sqrt(2) * sigma, 2))


def exponentialDecay(time, amplitude, tau): #calculate exponential decay
    return amplitude * np.exp(-time / tau)

def getRankedMatrices(number, matrix, rcd): #get matrices of a certain rank from a certain orientation
    if rcd == "r":
        # print("Row")
        return matrix[:number, :]
    elif rcd == "c":
        return matrix[:, :number]
    elif rcd == "d":
        m = np.diag(matrix)
        return m[:number, :number]


def getResiduals(uN, sN, vN, A): #calculate residual matrix
    An = uN @ sN @ vN
    residuals = A - An
    return An, residuals


def getChiSqS(S): #get chi squared using singular values
    return np.sum((S ** 2))


def getChiSq(x): #get chi squared using residuals
    return np.sum((x ** 2))


def plots(name, matrix, fig=None, font=None): #generate a plot of a matrix
    if fig is not None:
        fig.set_title(name, fontsize=font)
        fig.plot(matrix)
    else:
        plt.figure()
        plt.title(name)
        plt.plot(matrix)
        plt.show()


def getPicture(name, matrix, fig=None, font=None): #generate a picture of a matrix
    if fig is not None:
        fig.set_title(name, fontsize=font)
        fig.imshow(matrix)
    else:
        plt.figure()
        plt.title(name)
        plt.imshow(matrix)
        plt.show()


def getSubset(startcolumns, endcolumns, matrix): #get a subset of a matrix
    return matrix[:, startcolumns:endcolumns]


def SVDNoise(A, noiseLevel, noise):  #calculate SVD with some noise for a matrix
    noiseA = A + (noiseLevel * noise)
    u, s, v, = np.linalg.svd(noiseA)
    return noiseA, u, s, v


def LRA(uMatrix, sMatrix, vMatrix, n, A, noiseLevel=None, fig=None, font=None): #calculate and graph LRA
    chiSq = []
    chiSqS = []
    placeholder = np.copy(sMatrix)
    i = 1
    while i < n:
        uN = getRankedMatrices(i, uMatrix, "c")
        sN = getRankedMatrices(i, sMatrix, "d")
        vN = getRankedMatrices(i, vMatrix, "r")

        temp = np.diag(sMatrix)
        num = 0
        for num in range(i):
            placeholder[num] = 0

        chiSqS.append(getChiSqS(placeholder))
        An, residuals = getResiduals(uN, sN, vN, A)
        chiSq.append(getChiSq(residuals))

        i = i + 1
    nArr = np.arange(1, len(chiSq) + 1)

    if fig is not None:
        fig.plot(nArr, chiSq, ".-", label="Residuals")
        fig.plot(nArr, chiSqS, ".-", label="Singular Values")
        fig.legend()
        fig.set_xlabel("Rank(n)", fontsize=font)
        fig.set_ylabel("Chi Squared", fontsize=font)
        if noiseLevel is not None:
            fig.set_title("Rank vs Chi Squared for a noise level of " + str(noiseLevel), fontsize=font)
    else:
        plt.figure()
        plt.plot(nArr, chiSq, ".-", label="Residuals")
        plt.plot(nArr, chiSqS, ".-", label="Singular Values")
        plt.legend()
        plt.xlabel("Rank(n)")
        plt.ylabel("Chi Squared")
        if noiseLevel is not None:
            plt.title("Rank vs Chi Squared for a noise level of " + str(noiseLevel))

        else:
            plt.set_text("Rank vs Chi Squared")


def plotsingvalues(s, fig=None, font=None):  # plot a matrix of singular values
    nArr = np.arange(1, len(s + 1))
    if fig is not None:  # if the user has passed in their own figure, use that
        print("HERE!")
        fig.semilogy(s, ".-", label="sN")
        fig.set_xlabel("Index", fontsize=font)
        fig.set_ylabel("Singular Value", fontsize=font)
        fig.legend()
        fig.set_title("Singular Values vs Index", fontsize=font)
    else:  # otherwise design a new plot for them
        print(s)
        plt.figure()
        plt.plot(s, "o-", label="sN")
        plt.xlabel("Index")
        plt.ylabel("Singular Value")
        plt.legend()
        plt.title("Singular Values vs Index")


def getAutocorrelation(matrix, lag, title=None, fig=None, font=None): #find the autocorrelation of a matrix and graph it
    autocorrelation = []
    rows, cols = np.shape(matrix)
    k = lag
    for i in range(cols):
        vec = matrix[:, i]
        x1 = vec[k:]
        x2 = vec[:-k]
        ac = np.sum(x1 * x2)
        autocorrelation.append(ac)
    if fig is not None:
        fig.plot(autocorrelation, "k.-")
        if title is not None:
            fig.set_title("Autocorrelation of " + title, fontsize=font)
        fig.plot([0, cols], [0.8, 0.8], color='r', linestyle='dashed')
    else:
        plt.figure()
        plt.plot(autocorrelation, "k.-")
        if title is not None:
            plt.title("Autocorrelation of " + title)
        plt.plot([0, cols], [0.8, 0.8], color='r', linestyle='dashed')


def doSVD(matrixA, noiseLevel, noiseArray, f=None): # take in a matrix, and perform all SVD operations, with their graphs
    if f is not None:
        fig = plt.figure(f.number)
        font = (fig.get_figwidth() + fig.get_figheight()) / 2
        # fig.set_figheight(20)
        # fig.set_figwidth(20)

        ax1 = fig.add_subplot(7, 2, 1)
        ax2 = fig.add_subplot(7, 2, 2)
        ax3 = fig.add_subplot(7, 2, 3)
        ax4 = fig.add_subplot(7, 2, 4)
        ax5 = fig.add_subplot(7, 2, 5)
        ax6 = fig.add_subplot(7, 2, 6)
        ax7 = fig.add_subplot(7, 2, 7)
        ax8 = fig.add_subplot(7, 2, 8)
        ax9 = fig.add_subplot(7, 2, 9)
        ax10 = fig.add_subplot(7, 2, 10)
        ax11 = fig.add_subplot(7, 2, 11)
        ax12 = fig.add_subplot(7, 2, 12)
        ax13 = fig.add_subplot(7, 2, 13)
        subplotList = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10, ax11, ax12, ax13]
        plt.subplots_adjust(left=0.125,
                            bottom=0.1,
                            right=0.9,
                            top=0.9,
                            wspace=10,
                            hspace=10)
        for sub in subplotList:
            for label in (sub.get_xticklabels() + sub.get_yticklabels()):
                label.set_fontsize(font)

        fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.25, hspace=0.5)
        noiseA, noiseu, noises, noisev = SVDNoise(matrixA, noiseLevel, noiseArray)
        noiseAx, u, s, v = SVDNoise(matrixA, 0, noiseArray)

        plots("Representation of Matrix A(No noise)", A, ax1, font)  # 1
        getPicture("Representation of Matrix A(No noise)", A, ax2, font)  # 2
        plots("Representations of Matrix A(With noise)", noiseA, ax3, font)  # 3
        getPicture("Representations of Matrix A(With noise)", noiseA, ax4, font)  # 4

        subsetu = getSubset(0, 3, u)
        subsetnu = getSubset(0, 3, noiseu)
        plots("Representations of Subset of Matrix U(No noise)", subsetu, ax5, font)  # 5
        plots("Representations of Subset of Matrix U(With noise)", subsetnu3, ax6, font)  # 6

        diagonals = np.diag(s)
        ax7.set_title("Representations of Matrix S With(O) and Without(B) noise", fontsize=font)  # 7
        ax7.semilogy(s, "s-", label="noiseless")
        ax7.semilogy(noises, ".-", label="with noise")
        ax7.legend()

        subsetv = getSubset(0, 3, v.T)
        subnoisev = getSubset(0, 3, noisev.T)
        plots("Representation of subset V(No noise)", subsetv, ax8, font)  # 8
        plots("Representation of subset V with noise", subnoisev, ax9, font)  # 9
        getAutocorrelation(noiseu, 1, "u", ax10, font)  # 10
        getAutocorrelation(noisev.T, 1, "v", ax11, font)  # 11
        LRA(noiseu, noises, noisev, len(noises) + 1, noiseA, noiseLevel, ax12, font)  # 12
        plotsingvalues(noises, ax13, font)  # 13
    else:
        noiseA, noiseu, noises, noisev = SVDNoise(matrixA, noiseLevel, noiseArray)
        noiseAx, u, s, v = SVDNoise(matrixA, 0, noiseArray)

        plots("Representation of Matrix A(No noise)", A)  # 1
        getPicture("Representation of Matrix A(No noise)", A)  # 2
        plots("Representations of Matrix A(With noise)", noiseA)  # 3
        getPicture("Representations of Matrix A(With noise)", noiseA)  # 4

        subsetu = getSubset(0, 3, u)
        subsetnu = getSubset(0, 3, noiseu)
        plots("Representations of Subset of Matrix U(No noise)", subsetu)  # 5
        plots("Representations of Subset of Matrix U(With noise)", subsetnu3)  # 6

        diagonals = np.diag(s)
        plt.title("Representations of Matrix S With(O) and Without(B) noise")  # 7
        plt.semilogy(s, "s-", label="noiseless")
        plt.semilogy(noises, ".-", label="with noise")
        plt.legend()

        subsetv = getSubset(0, 3, v.T)
        subnoisev = getSubset(0, 3, noisev.T)
        plots("Representation of subset V(No noise)", subsetv)  # 8
        plots("Representation of subset V with noise", subnoisev)  # 9
        getAutocorrelation(noiseu, 1, "u")  # 10
        getAutocorrelation(noisev.T, 1, "v")  # 11
        LRA(noiseu, noises, noisev, len(noises) + 1, noiseA, noiseLevel)  # 12
        plotsingvalues(noises)  # 13

