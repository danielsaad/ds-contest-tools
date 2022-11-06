from operator import mod


"""
Converts an integer to a string from alphabet [A-Z] using radix 26
"""


def convert_idx_to_string(idx):
    ans = ''
    while True:
        rem = mod(idx, 26)
        ans += chr(ord('A')+rem)
        idx //= 26
        if idx == 0:
            break
    return ans
