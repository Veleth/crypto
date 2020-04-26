import unittest
from task1 import Oracle
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES

class TestEncDec(unittest.TestCase):
    def test_CBC(self):
        oracle = Oracle()
        mode = AES.MODE_CBC
        plaintext = str(get_random_bytes(AES.block_size).hex())
        ciphertext, iv = oracle.encrypt(plaintext, mode)
        decrypted = oracle.decrypt([ciphertext.hex()], iv, mode)[0]
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext, ciphertext)

    def test_CFB(self):
        oracle = Oracle()
        mode = AES.MODE_CFB
        plaintext = str(get_random_bytes(AES.block_size).hex())
        ciphertext, iv = oracle.encrypt(plaintext, mode)
        decrypted = oracle.decrypt([ciphertext.hex()], iv, mode)[0]
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext, ciphertext)

    def test_OFB(self):
        oracle = Oracle()
        mode = AES.MODE_OFB
        plaintext = str(get_random_bytes(AES.block_size).hex())
        ciphertext, iv = oracle.encrypt(plaintext, mode)
        decrypted = oracle.decrypt([ciphertext.hex()], iv, mode)[0]
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext, ciphertext)

    def test_CTR(self):
        oracle = Oracle()
        mode = AES.MODE_CTR
        plaintext = str(get_random_bytes(AES.block_size).hex())
        ciphertext, iv = oracle.encrypt(plaintext, mode)
        decrypted = oracle.decrypt([ciphertext.hex()], iv, mode)[0]
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext, ciphertext)

    def test_EAX(self):
        oracle = Oracle()
        mode = AES.MODE_EAX
        plaintext = str(get_random_bytes(AES.block_size).hex())
        ciphertext, iv = oracle.encrypt(plaintext, mode)
        decrypted = oracle.decrypt([ciphertext.hex()], iv, mode)[0]
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext, ciphertext)

if __name__ == '__main__':
    unittest.main()
