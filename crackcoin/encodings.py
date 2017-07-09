# from https://pypi.python.org/pypi/base58/0.2.2

import crackcoin


class b58encoder(object):
    """ Base58 encoder for crackcoin """

    def __init__(self):
        self.alphabet = 'zyxwvutsrqponmkjihgfedcbaZYXWVUTSRQPNMLKJHGFEDCBA987654321'

        self.iseq = lambda s: map(ord, s)
        self.bseq = lambda s: ''.join(map(chr, s))


    def b58encode(self, v):
        '''Encode a string using Base58'''

        origlen = len(v)
        v = v.lstrip(b'\0')
        newlen = len(v)

        p, acc = 1, 0
        for c in self.iseq(v[::-1]):
            acc += p * c
            p = p << 8

        result = ''
        while acc > 0:
            acc, mod = divmod(acc, 58)
            result += self.alphabet[mod]

        return (result + self.alphabet[0] * (origlen - newlen))[::-1]


    def b58decode(self, v):
        '''Decode a Base58 encoded string'''

        if not isinstance(v, str):
            v = v.decode('ascii')

        origlen = len(v)
        v = v.lstrip(self.alphabet[0])
        newlen = len(v)

        p, acc = 1, 0
        for c in v[::-1]:
            acc += p * self.alphabet.index(c)
            p *= 58

        result = []
        while acc > 0:
            acc, mod = divmod(acc, 256)
            result.append(mod)

        return (self.bseq(result) + b'\0' * (origlen - newlen))[::-1]

