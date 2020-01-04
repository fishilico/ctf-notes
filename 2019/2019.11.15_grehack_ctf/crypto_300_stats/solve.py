#!/usr/bin/env python3
from functools import reduce
import operator
from pathlib import Path


PROB = 0.3
MIN_COUNT_FOR_MEANING = 10


def ncr(n, r):
    """Compute Comb(n, r)"""
    r = min(r, n - r)
    numer = reduce(operator.mul, range(n, n - r, -1), 1)
    denom = reduce(operator.mul, range(1, r + 1), 1)
    return numer // denom


# Load the captured challenges and their responses as: c => [number of r=0, number of r=1]
capture = {}
with (Path(__file__).parent / '1573863538.43837_download' / 'capture').open('r') as fcap:
    for line in fcap:
        if ':' not in line:
            continue
        prompt, val = line.split(':')
        if prompt == 'Enter your challenge (32 bytes, hex encoded)':
            last_chall = int(val.strip(), 16)
        else:
            assert prompt == 'Response'
            assert last_chall is not None
            response = int(val.strip())
            assert response in (0, 1)

            if last_chall not in capture:
                capture[last_chall] = [0, 0]
            capture[last_chall][response] += 1
            last_chall = None

print(f"Loaded {len(capture)} distinct challenges/responses")


def count_ones(value):
    """Count the number of bits set to one in a value"""
    return bin(value).count('1')


def get_most_probable_bit_with_thres(filtered_capture, prob_threshold):
    """Get the most probable value of a bit, with a threshold on the considered probabilities"""
    # Enumerate challenge/responses to build a list of
    # (probabilities, challenge, value)
    sorted_prob = []
    for challenge, response in filtered_capture.items():
        n0, n1 = response
        n = n0 + n1
        if n < MIN_COUNT_FOR_MEANING:
            # Ignore challenges with not enough measures
            continue
        # q0 = ncr(n, n0) * pow(1 - PROB, n0) * pow(PROB, n1)
        # q1 = ncr(n, n0) * pow(PROB, n0) * pow(1 - PROB, n1)
        # unnormalize_q0 = pow(1 - PROB, n0) * pow(PROB, n1)
        # unnormalize_q1 = pow(PROB, n0) * pow(1 - PROB, n1)
        # p_b0 = unnormalized_q0 / (unnormalized_q1 + unnormalized_q0)
        # p_b1 = unnormalized_q1 / (unnormalized_q1 + unnormalized_q0)
        if n >= 500:
            # Prevent "OverflowError: (34, 'Numerical result out of range')"
            p_b0 = n0 / (n0 + n1)
            p_b1 = n1 / (n1 + n0)
        else:
            p_b0 = 1. / (1 + pow(PROB / (1 - PROB), n0) * pow((1 - PROB) / PROB, n1))
            p_b1 = 1. / (1. + pow(PROB / (1 - PROB), n1) * pow((1 - PROB) / PROB, n0))
        # print(f"[{n0:2}+{n1:2}={n:2}] pb0={p_b0:.3},  pb1={p_b1:.3}")
        if p_b1 > prob_threshold and p_b1 > p_b0:
            sorted_prob.append((p_b1, challenge, 1))
        elif p_b0 > prob_threshold and p_b0 > p_b1:
            sorted_prob.append((p_b0, challenge, 0))

    sorted_prob.sort()
    # print(f"Trying to find a bit out of {len(sorted_prob)} challenges with p>={prob_threshold}...")
    while sorted_prob:
        best_prob, best_chall, best_val = sorted_prob.pop()
        best_count = count_ones(best_chall)
        if best_count == 1:
            print(f"Found a bit: {best_chall:#x} = {best_val} (proba {best_prob})")
            return (best_chall, best_val)

        # Combine the probabilities
        for prob, chall, val in sorted_prob.copy():
            if chall == best_chall:
                continue
            # Reduce the masking with XOR
            if chall & ~best_chall == 0:
                # Ensure that the masking is reasonable
                count_xor = count_ones(best_chall ^ chall)
                if count_xor <= 2 and count_xor < best_count:
                    new_prob = prob * best_prob
                    if new_prob > prob_threshold:
                        sorted_prob.append((new_prob, chall ^ best_chall, val ^ best_val))
        sorted_prob.sort()

    print(f"Unable to found a bit with threshold={prob_threshold}")
    return None


def get_most_probable_bit(filtered_capture):
    """Get the most probable value of a bit"""
    for prob_threshold in (.9, .8, .7, .6):
        result = get_most_probable_bit_with_thres(filtered_capture, prob_threshold)
        if result is not None:
            return result
    return None


flag = 0
flag_mask = 0
FINAL_FLAG_MASK = (1 << 256) - 1

while flag_mask != FINAL_FLAG_MASK:
    result = get_most_probable_bit(capture)
    if result is None:
        break
    best_chall, best_val = result

    flag_mask |= best_chall
    if best_val:
        flag |= best_chall

    # Build a filtred capture without the found bit
    filtered_capture = {}
    for challenge, response in capture.items():
        if challenge & best_chall:
            # Remove the bit and eventually update the response
            challenge &= ~best_chall
            if best_val:
                response = [response[1], response[0]]
        if challenge:
            if challenge not in filtered_capture:
                filtered_capture[challenge] = [0, 0]
            filtered_capture[challenge][0] += response[0]
            filtered_capture[challenge][1] += response[1]

    capture = filtered_capture

    print(f"Flag: {repr(int.to_bytes(flag, 32, 'big'))} / {flag_mask:064x}")
