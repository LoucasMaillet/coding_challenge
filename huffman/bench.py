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
        return make_tree(text)


text = "Hi everybody do the flop!"
root = make_tree(text)

print(Node.from_tuple(root.to_tuple()))
print(root.tree)
print(root.to_tuple())
print('\n'.join(map(repr, root.layers)))
print(len(root))
