import argparse
import random
import time
from task1 import Oracle
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def xor_bytes(b1, b2):
    from sys import byteorder
    b2 = b2[:len(b1)]
    int_var = int.from_bytes(b1, byteorder)
    int_key = int.from_bytes(b2, byteorder)
    int_enc = int_var ^ int_key
    return int_enc.to_bytes(len(b1), byteorder)

def Adversary():
    oracle = Oracle(api=True)
    
    encrypted, iv = oracle.getSomeCiphertext()

    encryptedBlocks = [encrypted[i:i+AES.block_size] for i in range(0, len(encrypted), AES.block_size)]
    blocks = [(block, iv) for block, iv in zip(encryptedBlocks, [iv]+encryptedBlocks)]
    plainblocks = []

    for (block, iv) in blocks:
        decrypted = bytearray(AES.block_size)
        testIV = bytearray(AES.block_size)
        for i in reversed(range(16)):
            for j in reversed(range(i, 16)):
                testIV[j] = decrypted[j] ^ AES.block_size-i
            for b in range(0, 256):
                testIV[i] = b              
                ans = oracle.paddingOracle(block, testIV)
                if ans:
                    decrypted[i] = testIV[i] ^ AES.block_size-i
                    break
        plainblocks.append(xor_bytes(iv, decrypted))
    plaintext = b''
    for block in plainblocks:
        plaintext += block
    plaintext = unpad(plaintext, AES.block_size).decode()
    print(f'Secret message found:\n{plaintext}')

Adversary() 
