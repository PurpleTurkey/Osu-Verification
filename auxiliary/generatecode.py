import random
#from constants import *

PREFIX = "VRY"

def gen_code(size=6, alphanum=False):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if alphanum:
        chars += "1234567890"
    
    code = ""
    for i in range(size):
        code += random.choice(chars)
    
    return PREFIX + code