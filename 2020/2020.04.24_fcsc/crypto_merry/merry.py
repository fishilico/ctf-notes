import sys
import numpy as np
from flag import flag
from zlib import compress, decompress
from base64 import b64encode as b64e, b64decode as b64d

class Server:
    def __init__(self, q, n, n_bar, m_bar):
        self.q     = q
        self.n     = n
        self.n_bar = n_bar
        self.m_bar = m_bar
        self.__S_a = np.matrix(np.random.randint(-1, 2, size = (self.n, self.n_bar)))
        self.__E_a = np.matrix(np.random.randint(-1, 2, size = (self.n, self.n_bar)))
        self.A     = np.matrix(np.random.randint( 0, q, size = (self.n, self.n)))
        self.B     = np.mod(self.A * self.__S_a + self.__E_a, self.q)

    ### Private methods
    def __decode(self, mat):
        def recenter(x):
            if x > self.q // 2:
                return x - self.q
            else:
                return x

        def mult_and_round(x):
            return round((x / (self.q / 4)))

        out = np.vectorize(recenter)(mat)
        out = np.vectorize(mult_and_round)(out)
        return out

    def __decaps(self, U, C):
        key_a = self.__decode(np.mod(C - np.dot(U, self.__S_a), self.q))
        return key_a

    ### Public methods
    def pk(self):
        return self.A, self.B

    def check_exchange(self, U, C, key_b):
        key_a = self.__decaps(U, C)
        return (key_a == key_b).all()

    def check_sk(self, S_a, E_a):
        return (S_a == self.__S_a).all() and (E_a == self.__E_a).all()

def menu():
    print("Possible actions:")
    print("  [1] Key exchange")
    print("  [2] Get flag")
    print("  [3] Exit")
    return int(input(">>> "))

if __name__ == "__main__":

    q     = 2 ** 11
    n     = 280
    n_bar = 4
    m_bar = 4

    server = Server(q, n, n_bar, m_bar)

    A, B = server.pk()
    print("Here are the server public parameters:")
    print("A = {}".format(b64e(compress(A.tobytes())).decode()))
    print("B = {}".format(b64e(compress(B.tobytes())).decode()))

    nbQueries = 0
    while True:
        try:
            choice = menu()
            if choice == 1:
                nbQueries += 1
                print("Key exchange #{}".format(nbQueries), file = sys.stderr)
                U     = np.reshape(np.frombuffer(decompress(b64d(input("U = "))), dtype = np.int64), (m_bar, n))
                C     = np.reshape(np.frombuffer(decompress(b64d(input("C = "))), dtype = np.int64), (m_bar, n_bar))
                key_b = np.reshape(np.frombuffer(decompress(b64d(input("key_b = "))), dtype = np.int64), (m_bar, n_bar))

                if server.check_exchange(U, C, key_b):
                    print("Success, the server and the client share the same key!")
                else:
                    print("Failure.")

            elif choice == 2:
                S_a = np.reshape(np.frombuffer(decompress(b64d(input("S_a = "))), dtype = np.int64), (n, n_bar))
                E_a = np.reshape(np.frombuffer(decompress(b64d(input("E_a = "))), dtype = np.int64), (n, n_bar))

                if server.check_sk(S_a, E_a):
                    print("Correct key, congratulations! Here is the flag: {}".format(flag))
                else:
                    print("Sorry, this is not the correct key.")
                    print("Bye bye.")
                    exit(1)

            elif choice == 3:
                print("Bye bye.")
                break

        except:
            pass
