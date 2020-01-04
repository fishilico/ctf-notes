GreHack CTF 2019 - crypto 300
=============================

This challenge was about recovering a secret from a capture between a parking tag and a reader.
Both parties share a 32-byte secret that needs to be recovered through cracking the protocol that has been used to authenticate.

The files which are provided are the following:

* `<1573863538.43837_download/capture>`_: a text capture of challenge/response pairs
* `<1573863538.43837_download/reader.py>`_: a program that compute challenges and sends them to a tag.
* `<1573863538.43837_download/tag.py>`_: a program on a tag that computes the response to the received challenge.

Reading the Python scripts leads to understanding the protocol:

* The reader and the tag share the knowledge of 32 bytes (256 bits), the "secret"
* The reader generates two random numbers: ``p`` between 32 and 64 and ``i`` between 0 and 255.
* The reader then computes a challenge ``c = ROL256(pow(2, p) - 1, i)`` (where ``ROL256`` is the rotate-left operation over 256 bits). For example if ``p = 34`` and ``i = 12``, ``c = 0x3ffffffff000``.
* The reader sends the challenge to the tag.
* The tag receives the challenge and computes ``b`` as the number of bits set to 1 in ``c & secret``.
* The tag generates a random bit ``e`` which is ``0`` with a probability of 70% and ``1`` with a probability of 30%.
* The tag computes the response as ``r = b ^ e`` (so ``r`` has a 30% probability of being "wrong") and sends it back to the reader.
* The reader computes ``b`` (because it knowns the secret too) and finds out whether the response that an error by computing the bit ``e = r ^ b``.
* The reader asks responses for 65536 challenges. If the number of errors has been below 32% in the end, the tag is considered to know the secret and to be therefore authenticated.

The issue with this protocol is that 65535 random challenges give enough information about the secret, even with an error probability of ``p`` = 30%.

For a given challenge ``C``, if it was observed ``N0`` times to give ``0`` and ``N1`` times to give ``1``, the probability for the right response to be ``b=1`` is the probability of picking ``N0`` times ``1`` with the probability ``p`` and ``N1`` times ``0`` with the probability ``1 - p``, among ``N = N0 + N1`` tries::

    P(n0=N0 | b=1, n=N) = Comb(N, N0) * pow(p, N0) * pow(1 - p, N - N0)

(So the sum of probability for N0 from 0 to N is 1)

Likewise::

    P(n0=N0 | b=0, n=N) = Comb(N, N0) * pow(1 - p, N0) * pow(p, N - N0)

In order to compute ``P(b=1 | n0=N0, n=N)``, these probabilities need to be inverted somehow, for example using Bayes' theorem::

    P(b=1 | n0=N0, n=N) = P(n0=N0 | b=1, n=N) P(b=1, n=N) / P(n0=N0, n=N)

Moreover::

    P(b=0 | n0=N0, n=N) = P(n0=N0 | b=0, n=N) P(b=0, n=N) / P(n0=N0, n=N)

Therefore, under ``n=N``, with ``q1 = P(n0=N0 | b=1, n=N)`` and ``q0 = P(n0=N0 | b=0, n=N)``::

    P(b=1 | n0=N0) = q1 P(b=1) / P(n0=N0)
    1 - P(b=1 | n0=N0) = q0 (1 - P(b=1)) / P(n0=N0)

So::

    (1 - P(b=1 | n0=N0)) / P(b=1 | n0=N0) = q0 (1 - P(b=1)) / (q1 P(b=1))

    1/P(b=1 | n0=N0) - 1 = q0 (1/P(b=1) - 1) / q1

    1/P(b=1 | n0=N0) = (q0/P(b=1) - q0 + q1) / q1

    P(b=1 | n0=N0) = q1 / (q0/P(b=1) - q0 + q1)

Symmetrically::

    P(b=0 | n0=N0) = q0 / (q1/P(b=0) - q1 + q0)

Summing these two probabilities is 1:

    1 = q1 / (q0/P(b=1) - q0 + q1) + q0 / (q1/P(b=0) - q1 + q0)

This is like an equation with ``x=P(b=1)``:

    P(b=1 | n0=N0) = q1 / (q0/x - q0 + q1) = q1x/(q0 - q0x + q1x)

    P(b=0 | n0=N0) = q0 / (q1/(1-x) - q1 + q0)
    = q0(1-x)/(q1 - q1(1-x) + q0(1-x))
    = q0(1-x)/(q1x + q0 - q0x)
    = (q0 - q0x)/(q0 - q0x + q1x)
    = 1 - P(b=1 | n0=N0)

If there is not bias in choosing the secret, ``P(b=1) = 1/2`` and::

    P(b=0 | n0=N0) = q0 / (q1 * 2 - q1 + q0) = q0 / (q0 + q1)

    P(b=1 | n0=N0) = q1 / (q0 + q1)
