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
from codecs import Codec, CodecInfo, IncrementalEncoder, IncrementalDecoder, register
from collections.abc import Mapping
from typing import Any, Callable, Generator, Iterable, Hashable
from dataclasses import dataclass
from heapq import heapify, heappop, heappushpop


__version__ = "1.0.0"
__license__ = "GPL-3"
__author__ = "Lucas Maillet"
__credits__ = [__author__]
__maintainer__ = __author__
__email__ = "loucas.maillet.pro@gmail.com"
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
BYTES_CODEMAP = 2
BYTES_ORDER = "big"
BYTES_ENCODING = "utf-8"
CODEC_NAME = "hfmn"


class CodeMap():
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

    def encode(self, stdin: Iterable) -> bytes:
        """Encode some Iterable

        Args:
            decoded (Iterable): Some iterable data

        Returns:
            bytes: The encoded data
        """
        encoded = "1"  # need first bit to 1 to save the first 0 bits
        for v in stdin:
            encoded += self.__encode_map[v]
        length = 1 + len(encoded)
        offset = 8 - length % 8
        encoded = '0' * offset + encoded
        length += offset
        # turn to bytes data
        return int(encoded, 2).to_bytes(length // 8, byteorder=BYTES_ORDER)

    def decode(self, stdin: bytes) -> Generator:
        """Decode some bytes

        Args:
            stdin (bytes): Some raw data

        Returns:
            Generator: yield value of each value
        """
        stdin = format(int.from_bytes(stdin, byteorder=BYTES_ORDER), "0b")  # convert to bit string
        b = ""  # bit buffer
        for i in range(1, len(stdin)):  # start after the first security bit
            b += encoded[i]
            if b in self.__decode_map:
                yield self.__decode_map[b]
                b = ""


@dataclass(frozen=True, eq=False, repr=False)
class __TreePart:
    """A rot of the tree

    A part of the huffman tree, it can be either a Leaf or a Node,
    which are extended from here.
    """

    weight: int

    def __add__(self, rod: __TreePart) -> Node:
        return Node(self.weight + rod.weight, self, rod)

    def __lt__(self, rod: __TreePart) -> bool:
        return self.weight < rod.weight

    def __gt__(self, rod: __TreePart) -> bool:
        return self.weight > rod.weight

    def __eq__(self, rod: __TreePart) -> bool:
        return self.weight == rod.weight


@dataclass(frozen=True, repr=False)
class Leaf(__TreePart):
    """A Leaf of the Huffman Tree

    Create a leaf of the Huffman Tree

    Args:
        weight (int): The leaf weight
        value (Any): His corresponding value
    """

    value: Any

    def __len__(self) -> int:
        return 1

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
            offset (int): Current offset from the tree
        """
        layers[offset].append(self)

    def __add_code__(self, callable_: Callable, code: str) -> None:
        """Set code

        Finally set the code coreesponding to the leaf

        Args:
            callable_ (Callable): Something to call like that: fn(code, value)
            code (str): The Leaf code
        """
        callable_(code, self.value)

    def to_tuple(self) -> Any:
        return self.value


@dataclass(frozen=True, repr=False)
class Node(__TreePart):
    """A Node of the Huffman Tree

    Create a node of the tree

    Args:
        weight (int): The node weight
        left (Self | Leaf): The left part
        right (Self | Leaf): The right part
    """

    left: __TreePart
    right: __TreePart

    def __len__(self) -> int:
        return self.left.__len__() + self.right.__len__()

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

    def __add_code__(self, callable_: Callable, code: str) -> None:
        """Set code

        Spread the code generation to the leafs

        Args:
            callable_ (Callable): Something to call like that in the end: fn(code, value)
            code (str): The code already generated

        """
        self.left.__add_code__(callable_, f"{code}0")
        self.right.__add_code__(callable_, f"{code}1")

    def __set_layer__(self, layers: list, offset: int):
        """Recursively fill the layers

        Args:
            layers (tuple): Layers hashmap
            offset (int): Current offset from the tree
        """
        layers[offset].append(self)
        offset += 1
        if offset == len(layers):
            layers.append([])
        self.left.__set_layer__(layers, offset)
        self.right.__set_layer__(layers, offset)

    def __from_tuple__(value: tuple | Any) -> __TreePart:
        """Recursively build a hufftree from a tuple

        Generate a hufftree based on a tuple

        Args:
            value (tuple | Any): The node / child

        Returns:
            __TreePart: The corresponding part of the tree
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

        Generate layer from the tree

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
        self.__add_code__(code.add, '')
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
        Node: The tree of the tree (wich is also a node)
    """
    lenght = len(frequency_map)
    if lenght < 2:
        raise TypeError(f"require at least 2 items ({lenght} given)")
    tree = [Leaf(v, k) for k, v in frequency_map.items()]
    # Sum every time the 2 lightest node / leaf
    heapify(tree)
    left = heappop(tree)
    for _ in range(2, lenght):
        left = heappushpop(tree, left + heappop(tree))  # just an optimization
    return left + tree[0]


# * --- Codecs setup here ---

def __encode__(stdin: str) -> bytes:
    tree = huff_tree(frequency_map(stdin))
    tuple_tree = str(tree.to_tuple()).encode(BYTES_ENCODING)
    encode_map = {}

    def __find_code__(code: str, value: Any) -> None:
        encode_map[value] = code

    tree.__add_code__(__find_code__, '')
    encoded = "1"  # need first bit to 1 to save the first 0 bits

    for v in stdin:
        encoded += encode_map[v]

    length = 1 + len(encoded)
    offset = 8 - length % 8
    encoded = '0' * offset + encoded
    length += offset
    return len(tuple_tree).to_bytes(BYTES_CODEMAP, byteorder=BYTES_ORDER) + tuple_tree + int(encoded, 2).to_bytes(length // 8, byteorder=BYTES_ORDER)


def __decode__(stdin: bytes) -> str:
    code_len = int.from_bytes(stdin[0:BYTES_CODEMAP], byteorder=BYTES_ORDER) + BYTES_CODEMAP
    decode_map = {}

    def __find_code__(value: Any | tuple, code: str) -> None:

        if isinstance(value, tuple):
            __find_code__(value[0], f"{code}0")
            __find_code__(value[1], f"{code}1")
        else:
            decode_map[code] = value

    tuple_ = eval(stdin[BYTES_CODEMAP:code_len])
    __find_code__(tuple_[0], '0')
    __find_code__(tuple_[1], '1')

    stdin = format(int.from_bytes(stdin[code_len:], byteorder=BYTES_ORDER), "0b")  # convert to bit string
    stdout = ""
    b = ""  # bit buffer

    for i in range(1, len(stdin)):  # start after the first security bit
        b += stdin[i]
        if b in decode_map:
            stdout += decode_map[b]
            b = ""
    return stdout


class __IncrementalEncoder__(IncrementalEncoder):

    def encode(self, stdin: str) -> bytes:
        return __encode__(stdin)


class __IncrementalDecoder__(IncrementalDecoder):

    def decode(self, stdin: bytes, final: bool) -> str:
        return __decode__(stdin)


def __codec__(encoding: str) -> CodecInfo | None:
    if encoding == CODEC_NAME:
        return CodecInfo(
            name=CODEC_NAME,
            encode=lambda stdin: (__encode__(stdin), 0),
            decode=lambda stdin: (__decode__(stdin), 0),
            incrementalencoder=__IncrementalEncoder__,
            incrementaldecoder=__IncrementalDecoder__
        )
    return None


register(__codec__)
