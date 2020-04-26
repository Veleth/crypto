import argparse
import random
import time
from task1 import Oracle
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES

def xor_bytes(b1, b2):
    from sys import byteorder
    b2 = b2[:len(b1)]
    int_var = int.from_bytes(b1, byteorder)
    int_key = int.from_bytes(b2, byteorder)
    int_enc = int_var ^ int_key
    return int_enc.to_bytes(len(b1), byteorder)

def checkIV(iv, attempts):
    maxVal = 2**(8*AES.block_size)-1
    ivInt = int(iv.hex(), AES.block_size)
    if maxVal >= ivInt+attempts:
        pass
    else:
        #EXTREMELY RARE but theoretically possible
        print('Due to a very rare issue, the IV will overflow.\nPlease repeat the experiment')

def CPADistinguisher(attempts):
    start = time.time()
    oracle = Oracle(predictable=True, api=True)

    m = get_random_bytes(AES.block_size)
    c, iv = oracle.encrypt(m)
    iv0 = iv
    checkIV(iv, attempts)

    win = 0
    loss = 0
    for _ in range(attempts):
        ivNext = (int(iv.hex(), 16) + 1).to_bytes(AES.block_size, 'big')
        m0 = xor_bytes(xor_bytes(m, iv0), ivNext)
        while (m1 := get_random_bytes(AES.block_size)) == m0:
            continue
        
        cNext, iv = oracle.challenge([m0, m1])

        if c == cNext:
            b = 0
        else:
            b = 1

        try:
            assert b == oracle.b, 'The Distinguisher has made a mistake!'
            win += 1
        except AssertionError:
            loss += 1

    end = time.time()
    print(f'{100*win/attempts}% success rate out of {attempts} attempts')
    print(f'Time elapsed: {end-start}s')

CPADistinguisher(10**5)