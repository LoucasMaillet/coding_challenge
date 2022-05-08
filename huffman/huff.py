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
from collections import defaultdict
from typing import Any, Generator, Iterable, Hashable
from codecs import CodecInfo, IncrementalEncoder, IncrementalDecoder, register
from heapq import heapify, heappop, heappushpop
from dataclasses import dataclass


__version__ = "1.0.1"
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
EOL = '\n'
# For bytes manipulation
BYTES_CODEMAP = 2
BYTES_ORDER = "big"
BYTES_ENCODING = "utf-8"
# For codecs
CODEC_NAME = "hfmn"


#* Binary tree data structure and huffman algorithm here:


class CodeMap():
    """A CodeMap mapping an hufftree

    A simple implementation of encoding / decoding map.
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
            # Why not calling self.add method ? Because why the fuck not, it's faster and it's intern.
            self.__encode_map[value] = code
            self.__decode_map[code] = value

    @classmethod
    def from_tuple(cls, root: tuple) -> CodeMap:
        """Build a CodeMap from a tuple

        Generate a CodeMap based on a tuple

        Args:
            root (tuple): The tuple of an Huffman tree

        Returns:
            CodeMap: The CodeMap mapping the tuple
        """
        code = cls()
        lenght = len(root)
        if lenght < 2:
            raise ValueError(f"require at least 2 items ({lenght} given)")
        code.__from_tuple__(root[0], '0')
        code.__from_tuple__(root[1], '1')
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
        stdout = "1"  # Need first bit to 1 to save the first 0 bits
        for v in stdin:
            stdout += self.__encode_map[v]
        # Normalize to bytes format
        length = 1 + len(stdout)
        offset = 8 - length % 8
        stdout = '0' * offset + stdout
        length += offset
        # Turn to bytes data
        return int(stdout, 2).to_bytes(length // 8, byteorder=BYTES_ORDER)

    def decode(self, stdin: bytes) -> Generator:
        """Decode some bytes

        Args:
            stdin (bytes): Some raw data

        Returns:
            Generator: yield value of each value
        """
        stdin = format(int.from_bytes(stdin, byteorder=BYTES_ORDER), "0b")  # Convert to binary string
        b = ""  # Binary string buffer
        for i in range(1, len(stdin)):  # Start after the first security bit
            b += stdin[i]
            if b in self.__decode_map:
                yield self.__decode_map[b]
                b = ""


@dataclass(frozen=True, eq=False, repr=False)
class __TreeMember:
    """A rot of the tree

    A part of the huffman tree, it can be either a Leaf or a Node,
    which are extended from here.
    """

    weight: int

    def __add__(self, rod: __TreeMember) -> Node:
        return Node(self.weight + rod.weight, self, rod)

    def __lt__(self, rod: __TreeMember) -> bool:
        return self.weight < rod.weight

    def __gt__(self, rod: __TreeMember) -> bool:
        return self.weight > rod.weight

    def __eq__(self, rod: __TreeMember) -> bool:
        return self.weight == rod.weight


@dataclass(frozen=True, repr=False)
class Leaf(__TreeMember):
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

        Finaly build a line of the leaf of the visual tree

        Args:
            offset (str): The line offset (which is not used in this case)

        Returns:
            str: The leaf line
        """
        return f""" {self.weight} {X_STROKE}╼ {repr(self.value)}"""

    def __depth__(self, offset: int) -> int:
        """Found Depth

        Finally found the Leaf depth relative to a parent Node

        Args:
            offset (int): The relative depth to the parent Node

        Returns:
            int: The final relative depth to the parent Node
        """
        return offset

    def __layer__(self, layers: list[list], offset: int):
        """Finally fill the layers

        Args:
            layers (list[list]): Layers list
            offset (int): Current offset from the tree
        """
        layers[offset].append(self)

    def __code__(self, call: function, code: str) -> None:
        """Add code

        Finally set the code coreesponding to the leaf

        Args:
            call (function): Something to call like that: fn(code, value)
            code (str): The Leaf code
        """
        call(code, self.value)

    def to_tuple(self) -> Any:
        return self.value


@dataclass(frozen=True, repr=False)
class Node(__TreeMember):
    """A Node of the Huffman Tree

    Create a node of the tree

    Args:
        weight (int): The node weight
        left (Self | Leaf): The left part
        right (Self | Leaf): The right part
    """

    left: __TreeMember
    right: __TreeMember

    def __len__(self) -> int:
        return len(self.left) + len(self.right) + 1

    def __tree__(self, offset: str) -> str:
        """Spread tree build function

        Spread the recurent function to build the visual tree

        Args:
            offset (str): The line offset

        Returns:
            str: The generated trunc
        """
        indent = f"""{offset}{f"│{EOL + offset}" * Y_SPACE}"""
        return f"""┮ {self.weight}\n{indent}├{X_STROKE}{self.left.__tree__(f"{offset}│{X_INDENT}")}\n{indent}└{X_STROKE}{self.right.__tree__(f"{offset} {X_INDENT}")}"""

    def __depth__(self, offset: int) -> int:
        """Recursively found the maximal offset

        Args:
            offset (int): Parent offset

        Returns:
            int: His max offset
        """
        offset += 1
        return max(self.left.__depth__(offset), self.right.__depth__(offset))

    def __code__(self, call: function, code: str) -> None:
        """Add code

        Spread the code generation to the leafs

        Args:
            call (function): Something to call like that in the end: fn(code, value)
            code (str): The code already generated
        """
        self.left.__code__(call, f"{code}0")
        self.right.__code__(call, f"{code}1")

    def __layer__(self, layers: list[list], offset: int):
        """Recursively fill the layers

        Args:
            layers (list[list]): Layers list
            offset (int): Current offset from the tree
        """
        layers[offset].append(self)
        offset += 1
        if offset == len(layers):
            layers.append([])
        self.left.__layer__(layers, offset)
        self.right.__layer__(layers, offset)

    def __from_tuple__(value: tuple | Any) -> __TreeMember:
        """Recursively build a hufftree from a tuple

        Generate a hufftree based on a tuple

        Args:
            value (tuple | Any): The node / child

        Returns:
            __TreeMember: The corresponding part of the tree
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
        self.left.__layer__(layers, 1)
        self.right.__layer__(layers, 1)
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
        self.__code__(code.add, '')
        return code

    @classmethod
    def from_tuple(cls, root: tuple) -> Node:
        """Build a hufftree from a tuple

        Generate a hufftree based on a tuple

        Args:
            root (tuple): The tuple of some huffman tree

        Returns:
            Node: The root of the tree
        """
        lenght = len(root)
        if lenght < 2:
            raise ValueError(f"require at least 2 items ({lenght} given)")
        left = Node.__from_tuple__(root[0])
        right = Node.__from_tuple__(root[1])
        root = cls(left.weight + right.weight, left, right)
        return root

    def to_tuple(self) -> tuple[tuple | Any]:
        """Convert to tuple

        Returns:
            tuple[tuple | Any]: The node in tuple format
        """
        return (self.left.to_tuple(), self.right.to_tuple())


def make_tree(iterable: Iterable[Hashable]) -> Node:
    """Generate Root of the Huffman Tree

    Build an simple Huffman tree based on Leafs & Nodes

    Args:
        iterable (Iterable[Hashable]): Something iterable with at least 2 hashable values

    Returns:
        Node: The root of the tree (wich is technicaly a node)
    """
    entropy_map = defaultdict(int)

    for k in iterable:
        entropy_map[k] += 1

    lenght = len(entropy_map)
    if lenght < 2:
        raise ValueError(f"require at least 2 different items ({lenght} given)")

    tree = [Leaf(v, k) for k, v in entropy_map.items()]
    # Sum every time the 2 lightest node / leaf
    heapify(tree)
    left = heappop(tree)
    for _ in range(2, lenght):
        left = heappushpop(tree, left + heappop(tree))  # That just an optimization
    return left + tree[0]


#* Codecs setup here:


def __encode__(stdin: str) -> bytes:
    tree = make_tree(stdin)
    root = str(tree.to_tuple()).encode(BYTES_ENCODING)
    encode_map = {}

    def __find_code__(code: str, value: Hashable) -> None:
        encode_map[value] = code

    tree.__code__(__find_code__, '')
    stdout = "1"  # Need first bit to 1 to save the first 0 bits

    for v in stdin:
        stdout += encode_map[v]

    # Normalizing the binary string to bytes format
    length = len(stdout)
    offset = 8 - length % 8
    stdout = '0' * offset + stdout
    length += offset

    return len(root).to_bytes(BYTES_CODEMAP, byteorder=BYTES_ORDER) + root + int(stdout, 2).to_bytes(length // 8, byteorder=BYTES_ORDER)


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

    stdin = format(int.from_bytes(stdin[code_len:], byteorder=BYTES_ORDER), "0b")  # Convert to binary string
    stdout = ""
    b = ""  # Binary string buffer

    for i in range(1, len(stdin)):  # Start after the first security bit
        b += stdin[i]
        if b in decode_map:
            stdout += decode_map[b]
            b = ""
    return stdout


class __IncrementalEncoder(IncrementalEncoder):

    def encode(self, stdin: str) -> bytes:
        return __encode__(stdin)


class __IncrementalDecoder(IncrementalDecoder):

    def decode(self, stdin: bytes, final: bool) -> str:
        return __decode__(stdin)


def __find_codec(encoding: str) -> CodecInfo | None:
    if encoding != CODEC_NAME: return None
    return CodecInfo(
        name=CODEC_NAME,
        encode=lambda stdin: (__encode__(stdin), 0),
        decode=lambda stdin: (__decode__(stdin), 0),
        incrementalencoder=__IncrementalEncoder,
        incrementaldecoder=__IncrementalDecoder
    )


register(__find_codec)