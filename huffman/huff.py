#!/usr/bin/env python3.10
# coding: utf-8

#  __ __     ___ ___
# |  |  |_ _|  _|  _|_____ ___ ___
# |     | | |  _|  _|     | .'|   |
# |__|__|___|_| |_| |_|_|_|__,|_|_|
#            _ _
#  ___ ___ _| |_|___ ___
# |  _| . | . | |   | . |
# |___|___|___|_|_|_|_  |
#                   |___|

# A hufftree implementation in the most object-oriented and pythonic way possible.
# Maybe the heaviest piece of code I made but I learn a lot with.


from __future__ import annotations
from typing import Any, Generator, Iterable, Hashable
from dataclasses import dataclass
from heapq import heapify, heappop, heappushpop


__version__ = "1.0.0"
__license__ = "GPL-3"
__author__ = "Lucas Maillet"
__credits__ = [__author__]
__maintainer__ = __author__
__email__ = "...@gmail.com"
__copyright__ = "Copyright 2022, 3 years before climate disaster"

# For tree representation construction
X_SPACE = 2
Y_SPACE = 0
X_INDENT = ' ' * X_SPACE
X_STROKE = '─' * X_SPACE
DECO_WEIGHT = "\x1b[33m"
DECO_VALUE = "\x1b[32m"
EOL = '\n'
END = "\x1b[0m"
# For bytes manipulation
B_CODEMAP = 4
B_ORDER = "big"
B_ENCODING = "utf-8"


class CodeMap:
    """A CodeMap mapping an hufftree

    A simple implementation of encoding / decoding map: self[code]=value
    """

    __encode_map: dict[Hashable, Hashable] = {}
    __decode_map: dict[Hashable, Hashable] = {}

    def __repr__(self) -> str:
        return f"""CodeMap({", ".join(f"{repr(value)} : 0b{code}" for value, code in self.__encode_map.items())})"""

    def __from_tuple__(self, value: tuple | Any, code: str) -> None:
        if isinstance(value, tuple):
            self.__from_tuple__(value[0], f"{code}0")
            self.__from_tuple__(value[1], f"{code}1")
        else:
            # why not calling self.add method ? Because why the fuck not, is faster and it's intern.
            self.__encode_map[value] = code
            self.__decode_map[code] = value

    @classmethod
    def from_tuple(cls, value: tuple) -> CodeMap:
        """Build a CodeMap from a tuple

        Generate a CodeMap based on a tuple

        Args:
            value (tuple): The tuple of an Huffman tree

        Returns:
            CodeMap: The CodeMap mapping the tuple
        """
        code = cls()
        lenght = len(value)
        if lenght < 2:
            raise TypeError(f"require at least 2 items ({lenght} given)")
        code.__from_tuple__(value[0], '0')
        code.__from_tuple__(value[1], '1')
        return code

    def add(self, code: Hashable, value: Hashable) -> None:
        self.__encode_map[value] = code
        self.__decode_map[code] = value

    def encode(self, decoded: Iterable) -> bytes:
        """Encode some Iterable

        Args:
            decoded (Iterable): Some iterable data

        Returns:
            bytes: The encoded data
        """
        encoded = "1"  # need first bit to 1 to save the first 0 bits
        for v in decoded:
            encoded += self.__encode_map[v]
        length = 1 + len(encoded)
        offset = 8 - length % 8
        encoded = '0' * offset + encoded
        length += offset
        # turn to bytes data
        return int(encoded, 2).to_bytes(length // 8, byteorder=B_ORDER)

    def decode(self, encoded: bytes, offset_index: int = 0) -> Generator:
        """Decode some bytes

        Args:
            decoded (bytes): Some raw data
            offset_index (int): Starting index of buffer (to avoid copy of bytes)

        Returns:
            Generator: yield value of each value
        """
        encoded = format(int.from_bytes(encoded, byteorder=B_ORDER), "0b")  # convert to bit string
        b = ""  # bit buffer
        for i in range(offset_index * 8 + 1, len(encoded)):  # start after the first security bit
            b += encoded[i]
            if b in self.__decode_map:
                yield self.__decode_map[b]
                b = ""


@dataclass(frozen=True, eq=False, repr=False)
class Rod:
    """A rot of the tree

    A part of the huffman tree, it can be either a Leaf or a Node,
    which are extended from here.
    """

    weight: int

    def __add__(self, rod: Rod) -> Node:
        return Node(self.weight + rod.weight, self, rod)

    def __lt__(self, rod: Rod) -> bool:
        return self.weight < rod.weight

    def __gt__(self, rod: Rod) -> bool:
        return self.weight > rod.weight

    def __eq__(self, rod: Rod) -> bool:
        return self.weight == rod.weight


@dataclass(frozen=True, repr=False)
class Leaf(Rod):
    """A Leaf of the Huffman Tree

    Create a leaf of the Huffman Tree

    Args:
        weight (int): The leaf weight
        value (Any): His corresponding value
    """

    value: Any

    def __tree__(self, offset: str) -> str:
        """Build visual tree

        Finnaly build a line of the leaf of the visual tree

        Args:
            offset (str): The line offset (which is not used in this case)

        Returns:
            str: The leaf line
        """
        return f""" {DECO_WEIGHT}{self.weight}{END} {X_STROKE}╼ {DECO_VALUE}{repr(self.value)}{END}"""

    def __depth__(self, offset: int) -> int:
        """Found Depth

        Finally found the Leaf depth relative to a parent Node

        Args:
            offset (int): The relative depth to the parent Node

        Returns:
            int: The final relative depth to the parent Node
        """
        return offset

    def __set_layer__(self, layers: tuple, offset: int):
        """Finally fill the layers

        Args:
            layers (tuple): Layers hashmap
            offset (int): Current offset from the root
        """
        layers[offset].append(self)

    def __set_code__(self, codemap: CodeMap, code: str) -> None:
        """Set code

        Finally set the code coreesponding to the leaf

        Args:
            codemap (CodeMap): The CodeMap mapping the tree
            code (str): The Leaf code
        """
        codemap.add(code, self.value)

    def to_tuple(self) -> Any:
        return self.value


@dataclass(frozen=True, repr=False)
class Node(Rod):
    """A Node of the Huffman Tree

    Create a node of the tree

    Args:
        weight (int): The node weight
        left (Self | Leaf): The left part
        right (Self | Leaf): The right part
    """

    left: Rod
    right: Rod

    def __tree__(self, offset: str) -> str:
        """Spread tree build function

        Spread the recurent function to build the visual tree

        Args:
            offset (str): The line offset

        Returns:
            str: The generated trunc
        """
        indent = f"""{offset}{f"│{EOL + offset}" * Y_SPACE}"""
        return f"""┮ {DECO_WEIGHT}{self.weight}{END}\n{indent}├{X_STROKE}{self.left.__tree__(f"{offset}│{X_INDENT}")}\n{indent}└{X_STROKE}{self.right.__tree__(f"{offset} {X_INDENT}")}"""

    def __depth__(self, offset: int) -> int:
        """Recursively found the maximal offset

        Args:
            offset (int): Parent offset

        Returns:
            int: His max offset
        """
        offset += 1
        return max(self.left.__depth__(offset), self.right.__depth__(offset))

    def __set_code__(self, codemap: CodeMap, code: str) -> None:
        """Set binary

        Spread the code generation in a CodeMap to his extension

        Args:
            code (CodeMap): The CodeMap mapping the tree
            code (str): The binary already generated

        """
        self.left.__set_code__(codemap, f"{code}0")
        self.right.__set_code__(codemap, f"{code}1")

    def __set_layer__(self, layers: list, offset: int):
        """Recursively fill the layers

        Args:
            layers (tuple): Layers hashmap
            offset (int): Current offset from the root
        """
        layers[offset].append(self)
        offset += 1
        if offset == len(layers):
            layers.append([])
        self.left.__set_layer__(layers, offset)
        self.right.__set_layer__(layers, offset)

    def __from_tuple__(value: tuple | Any) -> Rod:
        """Recursively build a hufftree from a tuple

        Generate a hufftree based on a tuple

        Args:
            value (tuple | Any): The node / child

        Returns:
            Rod: The corresponding part of the tree
        """
        if isinstance(value, tuple):
            return Node.__from_tuple__(value[0]) + Node.__from_tuple__(value[1])
        else:
            return Leaf(1, value)

    @property
    def depth(self) -> int:
        """Get his depth

        Found his maximal depth of his extensions

        Returns:
            int: His max depth
        """
        return self.__depth__(1)

    @property
    def layers(self) -> list[list]:
        """Get his layers

        Generate layer from the root

        Returns:
            list: The layers looking like this: [[Node], [Node, Leaf], ...]
        """
        layers = [[self], []]
        self.left.__set_layer__(layers, 1)
        self.right.__set_layer__(layers, 1)
        return layers
    
    @property
    def tree(self) -> str:
        """A visual representation of the tree

        Returns:
            str: The representation
        """
        return self.__tree__('')

    @property
    def code(self) -> CodeMap:
        """Get his CodeMap

        Generate the CodeMap mapping the tree

        Returns:
            CodeMap: His CodeMap
        """
        code = CodeMap()
        self.__set_code__(code, '')
        return code

    @staticmethod
    def from_tuple(value: tuple) -> Node:
        """Build a hufftree from a tuple

        Generate a hufftree based on a tuple

        Args:
            value (tuple): The tuple of some huffman tree

        Returns:
            Node: The corresponding part of the tree
        """
        lenght = len(value)
        if lenght < 2:
            raise TypeError(f"require at least 2 items ({lenght} given)")
        return Node.__from_tuple__(value[0]) + Node.__from_tuple__(value[1])

    def to_tuple(self) -> tuple[tuple | Any]:
        """Convert to tuple

        Returns:
            tuple[tuple | Any]: The node in tuple format
        """
        return (self.left.to_tuple(), self.right.to_tuple())


def frequency_map(iterable: Iterable[Hashable]) -> dict[Hashable, int]:
    """Get occurences of something iterable

    Loop over value and get value's frequency

    Args:
        value (Iterable[Hashable]): The object you want to analyse

    Returns:
        dict[Hashable, int]: The results in form of: { value: frequency, ... }
    """
    freq = {}
    for value in iterable:
        if value in freq:
            freq[value] += 1
        else:
            freq[value] = 1
    return freq


def huff_tree(frequency_map: dict[Hashable, int]) -> Node:
    """Generate Root of the Huffman Tree

    Build an simple Huffman tree based on Leafs & Nodes

    Args:
        frequency_map (dict[Hashable, int]): Some Iterable occurences (at least 2)

    Returns:
        Node: The root of the tree (wich is also a node)
    """
    lenght = len(frequency_map)
    if lenght < 2:
        raise TypeError(f"require at least 2 items ({lenght} given)")
    tree = [Leaf(v, k) for k, v in frequency_map.items()]
    # Sum every time the 2 lightest node / leaf
    heapify(tree)
    left = heappop(tree)
    for _ in range(2, lenght):
        left = heappushpop(tree, left + heappop(tree))
    return left + tree[0]


if __name__ == "__main__":
    
    from timeit import timeit

    def encode():
        with open("tour_du_monde.txt") as file:
            text = file.read()
            root = huff_tree(frequency_map(text))
            codemap = str(root.to_tuple()).encode(B_ENCODING)
            with open("tour_du_monde_compressed.bin", 'wb') as file:
                file.write(len(codemap).to_bytes(B_CODEMAP, byteorder=B_ORDER) + codemap + root.code.encode(text))

    def decode():
        with open("tour_du_monde_compressed.bin", "rb") as file:
            encoded = file.read()
            code_len = int.from_bytes(encoded[0:B_CODEMAP], byteorder=B_ORDER) + B_CODEMAP
            codemap = CodeMap.from_tuple(eval(encoded[B_CODEMAP:code_len]))
            with open("tour_du_monde_uncompressed.txt", 'w') as file:
                file.write(''.join(v for v in codemap.decode(encoded, code_len)))

    # print(f"Encoding took approximatly {timeit(encode, number=1)} ms")
    #print(f"Decoding took approximatly {timeit(decode, number=1)} ms")

    def bench():
        with open("tour_du_monde.txt") as file:
            text = file.read()
            return huff_tree(frequency_map(text))

    root = huff_tree(frequency_map("Wikipedia"))
    def bench():
        layers = root.layers

    print(f"Bench took approximatly {timeit(bench, number=100)} ms")

    # LEVEL = 1

    # def encode_level():
    #     with open("tour_du_monde.txt") as file:
    #         decoded = file.read()
    #     for _ in range(LEVEL):
    #         root = huff_tree(frequency_map(decoded))
    #         codemap = str(root.to_tuple()).encode(B_ENCODING)
    #         decoded = len(codemap).to_bytes(B_CODEMAP, byteorder=B_ORDER) + codemap + root.code.encode(decoded)
    #     with open("tour_du_monde_compressed.bin", 'wb') as file:
    #         file.write(decoded)

    # def decode_level():
    #     for _ in range(LEVEL-1):
    #         with open("tour_du_monde_compressed.bin", "rb+") as file:
    #             encoded = file.read()
    #             code_len = int.from_bytes(encoded[0:B_CODEMAP], byteorder=B_ORDER) + B_CODEMAP
    #             codemap = CodeMap.from_tuple(eval(encoded[B_CODEMAP:code_len]))
    #             file.truncate(0)
    #             for v in codemap.decode(encoded, code_len):
    #                 file.write(v)

    #     with open("tour_du_monde_compressed.bin", "rb+") as file:
    #         encoded = file.read()
    #         code_len = int.from_bytes(encoded[0:B_CODEMAP], byteorder=B_ORDER) + B_CODEMAP
    #         codemap = CodeMap.from_tuple(eval(encoded[B_CODEMAP:code_len]))
    #         with open("tour_du_monde_uncompressed.txt", 'w') as file:
    #             code_len = int.from_bytes(encoded[0:B_CODEMAP], byteorder=B_ORDER) + B_CODEMAP
    #             codemap = CodeMap.from_tuple(eval(encoded[B_CODEMAP:code_len]))
    #             file.write(''.join(v for v in codemap.decode(encoded, code_len)))

    # print(f"Encoding with level {LEVEL} took approximatly {timeit(encode_level, number=1)} ms")
    # print(f"Decoding with level {LEVEL} took approximatly {timeit(decode_level, number=1)} ms")
