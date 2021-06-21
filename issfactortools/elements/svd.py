def SVDNoise(A, noiseLevel, noise):
    noiseA = A+(noiseLevel * noise)
    u, s, v, = np.linalg.svd(noiseA)
    return noiseA, u, s, v


def LRA(uMatrix, sMatrix, vMatrix, n, A, *args):
    chiSq = []
    i = 1
    while i < n:
        uN = getRankedMatrices(i, uMatrix, "c")
        sN = getRankedMatrices(i, sMatrix, "d")
        vN = getRankedMatrices(i, vMatrix, "r")
        An, residuals = getResiduals(uN, sN, vN, A)
        chiSq.append(getChiSq(residuals))
        i = i + 1
    nArr = np.arange(1, len(chiSq) + 1)
    plt.plot(nArr, chiSq)
    plt.xlabel("Rank(n)")
    plt.ylabel("Chi Squared")
    if args:
        plt.title("Rank vs Chi Squared for a noise level of " + str(args))
    else:
        plt.title("Rank vs Chi Squared")
    plt.show()

    i = 0
    j = 0
    sDiags = np.diag(sMatrix)
    rows = (np.diag(sDiags))
    cols = len(sDiags[i])
    list = []
    while i < 51:
        j = 0
        while j < cols:
            if sDiags[i][j] != 0:
                list.append(sDiags[i][j])
            j = j + 1
        i = i + 1
    plt.plot(list, "o-", label="sN")
    plt.xlabel("Index")
    plt.ylabel("Singular Value")
    plt.legend()
    plt.title("Singular Values vs Index")
    plt.show()


def getRankedMatrices(number, matrix, rcd):
    if rcd == "r":
        #print("Row")
        return matrix[0:number, :]
        #return matrix[0:number, 0:number]
    elif rcd == "c":
        #print("Column")
        return matrix[:, 0:number]
        #return matrix[0:number, 0:number]
    elif rcd == "d":
        #print("Diagonal")
        m =  np.diag(matrix)
        return m[0:number, 0:number]

def getResiduals(uN, sN, vN, A):
    An = uN @ sN @ vN
    residuals = A - An
    return An, residuals
def getChiSq(An):
    rows, cols = An.shape
    sum = 0
    for i in range(rows):
        for j in range(cols):
            sum += np.power(An[i][j], 2)


# here goes the SVD code