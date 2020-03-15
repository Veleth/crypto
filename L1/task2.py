import random
from algorithms import glibc

#Config
numberOfRounds = 100000
p = (2**31) - 1
initValues = 32

def getNextGuess(values):
    try:
        return (values[-31] + values[-3]) % (2**31)
    except IndexError:
        print('Too short list passed as argument for getNextGuess()')
        exit(1)

def test():
    seed = random.randint(0, p)

    generator = glibc(seed)
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
        values.append(value)
        if len(values) > numberOfRounds:
            break
    
    return right/(right+wrong)

#To make Monte Carlo tests
def average(runs):
    import statistics
    #Config
    accuracies = []
    lastWrongs = []
    for _ in range(runs):
        accuracy = test()
        accuracies.append(accuracy)
    print(f'Runs: {runs}\nInitial values: {initValues}\nRounds: {numberOfRounds}\nAccuracy (averaged): {statistics.mean(accuracies)}')

average(10)