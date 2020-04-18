import os
import random
import argparse
from Crypto.Cipher import AES
# import pyjks

def padding(iv, length):
    pass #TODO: implement

def encrypt(key, inputs, iv, mode):
    encryptionModes = {
        'ECB' : AES.MODE_ECB,
        'CBC' : AES.MODE_CBC,
        'CFB' : AES.MODE_CFB,
        'OFB' : AES.MODE_OFB,
        'CTR' : AES.MODE_CTR,
        'EAX' : AES.MODE_EAX
    }

    pass #TODO: implement / handle all the cases for different AES modes

def challenge(key, inputs, iv, mode):
    if len(inputs) != 2:
        print(f'Invalid number of arguments for challenge: {len(inputs)}')
        exit(1)
    else:
        b = random.SystemRandom().randint(0,1)
        return encrypt(key, inputs[b], iv, mode)

def oracle(key, inputs, iv, mode):
    encrypted = []
    for message in inputs:
        encrypted.append(encrypt(key, message, iv, mode))
    return encrypted

def getKey(path, identifier):
    # keystore = pyjks.KeyStore.load(path, 'passphrase')
    pass #TODO: implement

def getIV():
    try:
        iv = int(os.environ['GTCryptoIV'])
    except KeyError:
        iv = 1
        os.environ['GTCryptoIV'] = str(iv)
    return iv

def incrementIV():
    try:
        iv = int(os.environ['GTCryptoIV'])
    except KeyError:
        iv = 1
    os.environ['GTCryptoIV'] = str(iv+1)

def execute(args, test=False):
    key = 'ABC' #TODO: get key
    inputs = args.inputs
    iv = getIV()
    mode = args.mode
    result = args.action(key, inputs, iv, mode)
    #incrementIV()
    if not test:
        print(result)
    else:
        return result

parser = argparse.ArgumentParser()
parser.add_argument("--mode",
                    choices=['ECB', 'CBC', 'CFB', 'OFB', 'CTR', 'EAX'],
                    default='CBC',
                    help='AES Encryption mode')

parser.add_argument("--keystore",
                    help='Path to keystore') #TODO : check relative/absolute

parser.add_argument("--identifier",
                    help='Key identifier')

parser.add_argument('--challenge', dest='action', action='store_const',
                    const=challenge, default=oracle,
                    help='Challenge mode (default - encryption oracle)')

parser.add_argument('inputs', metavar='msgs', type=str, nargs='+',
                    help='Messages to encrypt')

args = parser.parse_args()
execute(args)
