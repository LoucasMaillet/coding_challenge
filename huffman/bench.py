#!/usr/bin/env python3.10
# coding: utf-8

from timeit import timeit
from huff import *


def encode():
    with open("tour_du_monde.txt") as f1:
        with open("tour_du_monde_compressed.bin", 'w', encoding="hfmn") as f2:
            f2.write(f1.read())


def decode():
    with open("tour_du_monde_compressed.bin", "r", encoding="hfmn") as f1:
        with open("tour_du_monde_uncompressed.txt", 'w') as f2:
            f2.write(f1.read())


print(f"Encoding took approximatly {timeit(encode, number=1)} ms")
print(f"Decoding took approximatly {timeit(decode, number=1)} ms")


def bench():
    with open("tour_du_monde.txt") as file:
        text = file.read()
        return huff_tree(frequency_map(text))

text = "Hi everybody do the flop!"
root = huff_tree(frequency_map(text))
print(root.tree)
print('\n'.join(map(repr, root.layers)))
print(len(root))
enc0 = root.code.encode(text)
print(enc0, len(enc0))
enc1 = text.encode("hfmn")
print(enc1, len(enc1))
print(enc1.decode("hfmn"))

# print(f"Bench took approximatly {timeit(bench, number=100)} ms")
