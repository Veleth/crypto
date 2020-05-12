import random
import math
import argparse
import jks
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

encryptionModes = {
    'CBC' : AES.MODE_CBC,
    'CFB' : AES.MODE_CFB,
    'OFB' : AES.MODE_OFB,
    'CTR' : AES.MODE_CTR,
    'EAX' : AES.MODE_EAX
}

class Oracle():
    def __init__(self, keystore=None, keyIdentifier=None, keystorePass=None, mode='CBC', predictable=False, api=False):
        if (None in [keystore, keyIdentifier, keystorePass == None]):
            self.key = self.getDefaultKey()
        else:
            self.key = self.setKey(keystore, keyIdentifier, keystorePass)

        self.mode = encryptionModes[mode]
        self.predictable = predictable
        if self.predictable:
            self.ivGenerator = self.getPredictableIV()
        self.api = api

    def getIV(self, length):
        if not self.predictable:
            self.iv = get_random_bytes(length)
        else:
            iv = next(self.ivGenerator)
            self.iv = iv[-length:] #Trim leftmost bytes if needed
        return self.iv

    def getPredictableIV(self):
        iv = get_random_bytes(AES.block_size)
        i = int(iv.hex(), AES.block_size)
        while True:
            yield i.to_bytes(AES.block_size, 'big')
            i += 1

    def encrypt(self, message, mode=None):
        mode = mode or self.mode #Defaults to self.mode if mode is not set explicitly
        
        if self.key == None:
            raise Exception(f'No encryption key!')

        #These modes require a 16-byte IV
        if mode in [AES.MODE_CBC, AES.MODE_CFB, AES.MODE_OFB]:
            cipher = AES.new(key=self.key, mode=mode, iv=self.getIV(16))
        #These modes require a nonce, 15 bytes is a value supported by both
        elif mode in [AES.MODE_CTR, AES.MODE_EAX]:
            cipher = AES.new(key=self.key, mode=mode, nonce=self.getIV(15))
        else:
            raise Exception(f'Undefined behavior for mode: {mode}')
        
        #Turn strings to bytes
        if type(message) == str:
            message = message.encode()
        
        #CBC mode requires padding, pkcs7 used by default
        if mode == AES.MODE_CBC:
            message = pad(message, AES.block_size)
        
        try:
            cipherIV = cipher.IV
        except AttributeError:
            cipherIV = cipher.nonce

        return (cipher.encrypt(message), cipherIV)

    def challenge(self, inputs, mode=None):
        if len(inputs) != 2:
            raise Exception(f'Invalid number of arguments for challenge: {len(inputs)}')
        else:
            self.b = random.SystemRandom().randint(0,1)
        
        #If called from another module, b is accessible via the instance. For console mode return b for reference
        if self.api:
            return self.encrypt(inputs[self.b])
        else:
            return self.encrypt(inputs[self.b]), self.b

    def encryptionOracle(self, inputs, mode=None):
        #INFO: by default the ciphertexts are encrypted independently
        encrypted = []
        for message in inputs:
            encrypted.append(self.encrypt(message))
        return encrypted

    def setKey(self, path, identifier, password):
        try:
            keystore = jks.KeyStore.load(path, password)
            keyEntry = keystore.secret_keys[identifier] 
            key = keyEntry.key
            return key
        except (jks.BadKeystoreFormatException, FileNotFoundError, KeyError) as e:
            raise Exception(f'Error while retrieving the key: {e}')

    # Default key path and name, used in the CPA experiment
    def getDefaultKey(self):
        try:
            keystore = jks.KeyStore.load('keystore.jks', 'changeit')
            keyEntry = keystore.secret_keys['crypto'] 
            key = keyEntry.key
            return key
        except (jks.BadKeystoreFormatException, FileNotFoundError, KeyError) as e:
            raise Exception(f'Error while retrieving default key: {e}')

    def decrypt(self, ciphertexts, iv, mode=None):
        mode = mode or self.mode
        decrypted = []
        if mode in [AES.MODE_CBC, AES.MODE_CFB, AES.MODE_OFB]:
            cipher = AES.new(key=self.key, mode=mode, iv=iv)
        elif mode in [AES.MODE_CTR, AES.MODE_EAX]:
            cipher = AES.new(key=self.key, mode=mode, nonce=iv)
        if not iv:
            raise Exception(f'IV not provided')
        for c in ciphertexts:            
            plaintext = cipher.decrypt(bytearray.fromhex(c))
            if mode == AES.MODE_CBC:
                plaintext = unpad(plaintext, AES.block_size)
            decrypted.append(plaintext.decode())
        return decrypted

    def getSomeCiphertext(self):
        secret = 'This is my super confidential secret!'
        return self.encrypt(secret)

    def paddingOracle(self, ciphertext, iv):
        cipher = AES.new(key=self.key, mode=AES.MODE_CBC, iv=iv)
        message = cipher.decrypt(ciphertext)
        try:
            unpad(message, AES.block_size)
            return True
        except ValueError:
            return False

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
                        const='challenge', default='oracle',
                        help='Challenge mode (default - encryption oracle)')

    parser.add_argument('-d', '--decrypt', action='store_true',
                        help='Decryption (overrides --challenge and oracle modes)')

    parser.add_argument ('--iv', 
                        help='Used for decryption (hex)')

    parser.add_argument('inputs', metavar='msgs', type=str, nargs='+',
                        help='Messages to encrypt (str)/decrypt (hex)')

    args = parser.parse_args()

    oracle = Oracle(keystore=args.keystore, keyIdentifier=args.identifier, keystorePass=args.keystorepass, mode=args.mode)
    if args.decrypt:
        result = oracle.decrypt(ciphertexts=args.inputs, iv=bytes(bytearray.fromhex(args.iv)))
    else:
        if args.action == 'challenge':
            result = oracle.challenge(inputs=args.inputs)
        else: 
            result = oracle.encryptionOracle(inputs=args.inputs)
    print(result)