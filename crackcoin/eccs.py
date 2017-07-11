# from https://raw.githubusercontent.com/andreacorbellini/ecc/master/scripts/ecdsa.py
# (made to work with Python 2, made some adjustments)

from os import urandom
import crackcoin


class ellipticCurve(object):
    """ ECC class for crackcoin """

    def __init__(self):

        # Field characteristic.
        self.p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
        # Curve coefficients.
        self.a=0
        self.b=7
        # Base point.
        self.g=(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
           0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)
        # Subgroup order.
        self.n=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
        # Subgroup cofactor.
        self.h=1


    def inverse_mod(self, k, p):
        """Returns the inverse of k modulo p.

        This function returns the only integer x such that (x * k) % p == 1.

        k must be non-zero and p must be a prime.
        """

        if k == 0:
            raise ZeroDivisionError('division by zero')

        if k < 0:
            # k ** -1 = p - (-k) ** -1  (mod p)
            return p - self.inverse_mod(-k, p)

        # Extended Euclidean algorithm.
        s, old_s = 0, 1
        t, old_t = 1, 0
        r, old_r = p, k

        while r != 0:
            quotient = old_r // r
            old_r, r = r, old_r - quotient * r
            old_s, s = s, old_s - quotient * s
            old_t, t = t, old_t - quotient * t

        gcd, x, y = old_r, old_s, old_t

        assert gcd == 1
        assert (k * x) % p == 1

        return x % p

    def is_on_curve(self, point):
        """Returns True if the given point lies on the elliptic curve."""

        if point is None:
            # None represents the point at infinity.
            return True

        x, y = point

        return (y * y - x * x * x - self.a * x - self.b) % self.p == 0


    def point_neg(self, point):
        """Returns -point."""

        assert self.is_on_curve(point)

        if point is None:
            # -0 = 0
            return None

        x, y = point
        result = (x, -y % self.p)

        assert self.is_on_curve(result)

        return result


    def point_add(self, point1, point2):
        """Returns the result of point1 + point2 according to the group law."""
        assert self.is_on_curve(point1)
        assert self.is_on_curve(point2)

        if point1 is None:
            # 0 + point2 = point2
            return point2
        if point2 is None:
            # point1 + 0 = point1
            return point1

        x1, y1 = point1
        x2, y2 = point2

        if x1 == x2 and y1 != y2:
            # point1 + (-point1) = 0
            return None

        if x1 == x2:
            # This is the case point1 == point2.
            m = (3 * x1 * x1 + self.a) * self.inverse_mod(2 * y1, self.p)
        else:
            # This is the case point1 != point2.
            m = (y1 - y2) * self.inverse_mod(x1 - x2, self.p)

        x3 = m * m - x1 - x2
        y3 = y1 + m * (x3 - x1)
        result = (x3 % self.p,
                  -y3 % self.p)

        assert self.is_on_curve(result)

        return result


    def scalar_mult(self, k, point):
        """Returns k * point computed using the double and point_add algorithm."""

        assert self.is_on_curve(point)

        if k % self.n == 0 or point is None:
            return None

        if k < 0:
            # k * point = -k * (-point)
            return self.scalar_mult(-k, self.point_neg(point))

        result = None
        addend = point

        while k:
            if k & 1:
                # Add.
                result = self.point_add(result, addend)

            # Double.
            addend = self.point_add(addend, addend)

            k >>= 1

        assert self.is_on_curve(result)

        return result


    def make_keypair(self):
        """Generates a random private-public key pair."""

        private_key = int(urandom(64).encode('hex'),16) % self.n
        public_key = self.scalar_mult(private_key, self.g)

        return private_key, public_key

    def hash_message(self, message):
        """Returns the hash of the message."""

        message_hash = crackcoin.hasher(message).hexdigest()
        e = int(message_hash, 16)

        return e

    def sign_message(self, private_key, message):
        z = self.hash_message(message)

        r = 0
        s = 0

        while not r or not s:
            k = int(urandom(64).encode('hex'),16) % self.n
            x, y = self.scalar_mult(k, self.g)

            r = x % self.n
            s = ((z + r * private_key) * self.inverse_mod(k, self.n)) % self.n

        return (r, s)


    def verify_signature(self, public_key, message, signature):
        z = self.hash_message(message)

        r, s = signature

        w = self.inverse_mod(s, self.n)
        u1 = (z * w) % self.n
        u2 = (r * w) % self.n

        x, y = self.point_add(self.scalar_mult(u1, self.g),
                         self.scalar_mult(u2, public_key))

        if (r % self.n) == (x % self.n):
            return True
        else:
            return False
