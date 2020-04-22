import os
import math
import random
import argparse
from Crypto.Cipher import AES
import jks


#TODO: change to a class
def encrypt(key, message, mode):
    encryptionModes = {
        'CBC' : AES.MODE_CBC,
        'CFB' : AES.MODE_CFB,
        'OFB' : AES.MODE_OFB,
        'CTR' : AES.MODE_CTR,
        'EAX' : AES.MODE_EAX
    }

    if mode in ['CBC', 'CFB', 'OFB']:
        # 16-byte IV
        cipher = AES.new(key=key, mode=encryptionModes[mode], iv=getIV(16))
        if mode == 'CBC':
            # padding the message to nearest 16 bytes
            message = message.zfill(math.ceil(len(message)/16)*16)
    elif mode in ['CTR', 'EAX']:
        # 15-byte nonce
        cipher = AES.new(key=key, mode=encryptionModes[mode], nonce=getIV(15))
    else:
        raise Exception(f'Undefined behavior for mode: {mode}')
    return cipher.encrypt(message.encode())

def challenge(inputs, key=None, mode='CBC'):
    if not key:
        key = getDefaultKey()
    if len(inputs) != 2:
        print(f'Invalid number of arguments for challenge: {len(inputs)}')
        exit(1)
    else:
        b = random.SystemRandom().randint(0,1)
        return encrypt(key, inputs[b], mode), b

def oracle(inputs, key=None, mode='CBC'):
    if not key:
        key = getDefaultKey()
    encrypted = []
    for message in inputs:
        encrypted.append(encrypt(key, message, mode))
    return encrypted

def getKey(path, identifier, password):
    keystore = jks.KeyStore.load(path, password) #TODO: JKS or jceks required (try-except)
    keyEntry = keystore.secret_keys[identifier] #TODO: try-except KeyError
    key = keyEntry.key
    return key

# Default key path and name for CPA Experiment (the program is imported as dependency rather than ran from command line)
def getDefaultKey():
    keystore = jks.KeyStore.load('keystore.jks', 'changeit') #TODO: File not available try-except
    keyEntry = keystore.secret_keys['crypto'] #TODO: try-except KeyError
    key = keyEntry.key
    return key

def getIV(length):
    val = getWeakIV()
    if len(val[-length:]) < length:
        return val.zfill(length).encode()
    return val[-length:].encode()

def getStrongIV():
    random.SystemRandom().randint(2**127,2**128)

def getWeakIV():
    try:
        iv = int(os.environ['CryptoWeakIV'])
        os.environ['CryptoWeakIV'] = str(iv+1) #TODO: make more persistent
    except KeyError:
        iv = 1
        os.environ['CryptoWeakIV'] = str(iv)
    return str(iv)

def execute(args, printRes=False):
    key = getKey(args.keystore, args.identifier, args.keystorepass) 
    inputs = args.inputs
    mode = args.mode
    result = args.action(inputs=inputs, key=key, mode=mode)
    if printRes:
        print(result)
    else:
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",
                        choices=['CBC', 'CFB', 'OFB', 'CTR', 'EAX'],
                        default='CBC',
                        help='AES Encryption mode')

    parser.add_argument("--keystore",
                        help='Path to keystore')

    parser.add_argument("--keystorepass",
                        help='Keystore password')

    parser.add_argument("--identifier",
                        help='Key identifier')

    parser.add_argument('--challenge', dest='action', action='store_const',
                        const=challenge, default=oracle,
                        help='Challenge mode (default - encryption oracle)')

    parser.add_argument('inputs', metavar='msgs', type=str, nargs='+',
                        help='Messages to encrypt')

    args = parser.parse_args()

    execute(args, printRes=True)