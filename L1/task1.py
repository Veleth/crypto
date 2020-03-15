import random
from math import gcd
from functools import reduce
from algorithms import lcg

#Config
numberOfRounds = 10000
initValues = 4
numberOfDifferences = 10

def getNextGuess(values):

    #Config
    n = min(len(values), numberOfDifferences)

    diffs = [x - y for x, y in zip(values[-(n-1):], values[-n:-1])]

    zeros = [t2*t0 - t1**2 for t0, t1,
               t2 in zip(diffs, diffs[1:], diffs[2:])]
    
    p = abs(reduce(gcd, zeros)) #gcd of all zeros mod p

    try:
        a = (values[-1] - values[-2]) * \
            pow((values[-2] - values[-3]), -1, p) % p
    except:
        a = 0  # extended gcd doesn't find solution

    c = (values[-1] - (values[-2]*a)) % p

    return (a * values[-1] + c) % p


def test():

    #LCG parameters
    p = (2**31) - 1
    a = random.randint(0, p)
    c = random.randint(0, p)
    seed = random.randint(0, p)

    generator = lcg(p, a, c, seed)

    values = []

    for _ in range(initValues):
        values.append(next(generator))

    right = 0
    wrong = 0

    for value in generator:
        guess = getNextGuess(values)
        if guess == value:
            right += 1
        else:
            wrong += 1
            lastWrong = len(values)
        values.append(value)
        if len(values) > numberOfRounds:
            break
    
    return right/(right+wrong), lastWrong
    
#To make Monte Carlo tests
def average(runs):
    import statistics
    accuracies = []
    lastWrongs = []
    for _ in range(runs):
        accuracy, lastWrong = test()
        accuracies.append(accuracy)
        lastWrongs.append(lastWrong)
    print(f'Runs: {runs}\nInitial values: {initValues}\nNumber of differences: {numberOfDifferences}\nRounds: {numberOfRounds}\nAccuracy (averaged): {statistics.mean(accuracies)}\nLast mistake (averaged): {statistics.mean(lastWrongs)}')

average(10)
