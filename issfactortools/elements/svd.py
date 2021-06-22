from matplotlib import pyplot as plt
import numpy as np


# here goes the SVD code

def gaussian(x, amplitude, center, sigma):  # function to calculate a gaussian equation
    return amplitude * np.exp(-np.power(x - center, 2) / np.power(np.sqrt(2) * sigma, 2))


def exponentialdecay(time, amplitude, tau):  # calculate exponential decay of data
    return amplitude * np.exp(-time / tau)


def newplots(matrix, t, x, y, *args):  # takes in matrix, title, xlabel, ylabel, and potenteial args to make plot
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(t)
    plt.plot(matrix)
    if args:  # potential args are number of data points to plot, oriented by colums or rows, and a label
        num, orientation, lab = args
        if (orientation == "c"):
            i = 0
            for i in range(num):
                plt.plot(matrix[:, i], label=(lab + str(i + 1)))
        elif (orientation == "r"):
            i = 0
            for i in range(num):
                plt.plot(matrix[i, :], label=(lab + str(i + 1)))
        plt.legend()
    else:
        plt.plot(matrix)
    plt.show()


def getrankedmatrices(number, matrix, rcd):  # return a matrix of a specific rank
    if rcd == "r":  # takes in the desired rank, the matrix, and whether to take in that many rows, columns, or diagonals
        # print("Row")
        return matrix[0:number, :]
        # return matrix[0:number, 0:number]
    elif rcd == "c":
        # print("Column")
        return matrix[:, 0:number]
        # return matrix[0:number, 0:number]
    elif rcd == "d":
        # print("Diagonal")
        m = np.diag(matrix)
        return m[0:number, 0:number]


def getresiduals(uN, sN, vN, A):  # returns matrix A of rank n, and the residual matrix
    An = uN @ sN @ vN  # takes in u, s, and v of rank N, as well as the original matrix, A
    residuals = A - An
    return An, residuals


def getchisq(An):  # takes in matrix A of rank N, and calculates chi squared for it
    rows, cols = An.shape
    sum = 0
    for i in range(rows):
        for j in range(cols):
            sum += np.power(An[i][j], 2) #iterate through the matrix, and sum each element squared
    chiSq = sum
    return chiSq


def plots(name, matrix):
    plt.figure()
    plt.title(name)
    plt.imshow(matrix)
    plt.figure()
    plt.plot(matrix)
    plt.show()


def svdnoise(A, noiseLevel, noise):  # pass original matrix A, a noise level, and a noise Matrix
    # calculate the SVD on matrix A at that noise level
    noiseA = A + (noiseLevel * noise)
    u, s, v, = np.linalg.svd(noiseA)
    return noiseA, u, s, v #return a copy of matrix A with that noise Level applied, and u, s, and v


def plotsingvalues(s): # plot a matrix of singular values
    sMatrix = s
    i = 0
    j = 0
    sDiags = np.diag(sMatrix)  #take the diagonals of the matrix
    rows = (np.diag(sDiags))
    cols = len(sDiags[i])
    list = []
    while i < 51: # iterate through, and plot
        j = 0
        while j < cols:
            if sDiags[i][j] != 0:
                list.append(sDiags[i][j])
            j = j + 1
        i = i + 1
    #label the plot
    plt.plot(list, "o-", label="sN")
    plt.xlabel("Index")
    plt.ylabel("Singular Value")
    plt.legend()
    plt.title("Singular Values vs Index")
    plt.show()


def lra(uMatrix, sMatrix, vMatrix, n, A, *args): #computer the lra of a matrix
    # pass in matrix u, s, and v
    # pass in the number of times to run LRA, n
    # pass in the original matrix A
    # pass in potential extra arguments, args, that can be used to title the plot
    chiSq = []
    i = 1
    while i < n: # compute LRA for each n rank
        uN = getrankedmatrices(i, uMatrix, "c")
        sN = getrankedmatrices(i, sMatrix, "d")
        vN = getrankedmatrices(i, vMatrix, "r")
        An, residuals = getresiduals(uN, sN, vN, A) # calculate the residuals
        chiSq.append(getchisq(residuals))  # append the chi squared at this rank to the chi squared list
        i = i + 1
    nArr = np.arange(1, len(chiSq) + 1) # create a matrix from 1 to the maximum rank
    plt.plot(nArr, chiSq) # plot chiSquared against it
    # label the plot
    plt.xlabel("Rank(n)")
    plt.ylabel("Chi Squared")
    # if additional arguments were passed in, use them for the title of the plot
    if args:
        plt.title("Rank vs Chi Squared for a noise level of " + str(args))
    else:
        plt.title("Rank vs Chi Squared")
    plt.show()
    plotsingvalues(sMatrix)



