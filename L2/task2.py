import argparse
from task1 import challenge, oracle


def CPADistinguisher():
    res = challenge(['123', '321']) #CBC mode and key set by default
    print(res)
    
CPADistinguisher()