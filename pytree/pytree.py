#!/usr/bin/env python3.10
# coding: utf-8

#  _____     _
# |  _  |_ _| |_ ___ ___ ___
# |   __| | |  _|  _| -_| -_|
# |__|  |_  |_| |_| |___|___|
#       |___|

# A tree data structure implementation in python with multiple varient.
# Everything work fine if you read docstrings.


from __future__ import annotations
from typing import Any, Iterable, Callable
from dataclasses import dataclass
from collections import defaultdict
from heapq import heapify, heappop, heappushpop


__version__ = "1.0.0"
__license__ = "GPL-3"
__author__ = "Lucas Maillet"
__credits__ = [__author__]
__maintainer__ = __author__
__email__ = "loucas.maillet.pro@gmail.com"
__copyright__ = "Copyright 2022, 2 years before climate disaster"


# For tree visual string construction
X_SPACE = 2
Y_SPACE = 0
X_INDENT = ' ' * X_SPACE
X_STROKE = '─' * X_SPACE


# * Error class


class ChildError(Exception):
    """Raise if there something wrong with node's children
    """


# * Class fragments


@dataclass(eq=False, repr=False)
class __Fragment:

    weight: int

    def __lt__(self, fragment: __Fragment) -> bool:
        """Comparaison based on weight

        Args:
            fragment (__Fragment): A tree fragment

        Returns:
            bool: If it's less than the other fragment
        """
        return self.weight < fragment.weight

    def __gt__(self, fragment: __Fragment) -> bool:
        """Comparaison based on weight

        Args:
            fragment (__Fragment): A tree fragment

        Returns:
            bool: If it's greater than the other fragment
        """
        return self.weight > fragment.weight

    def __eq__(self, fragment: __Fragment) -> bool:
        """Comparaison based on weight

        Args:
            fragment (__Fragment): A tree fragment

        Returns:
            bool: If it's esual to the other fragment
        """
        return self.weight == fragment.weight

    def __repr__(self) -> str:
        """Simple representation only based on weight

        Returns:
            str: A readable representation
        """
        return f"{self.__class__.__name__}(w={self.weight})"


@dataclass(repr=False)
class __LeafFragment(__Fragment):

    """A leaf of a tree

    It can have any value

    Args:
        weight (int): Self weight
        value (Any): Self value
    """

    value: Any

    def __len__(self) -> int:
        """Lenght in the tree

        Returns:
            int: Always 1
        """
        return 1

    def __tree__(self, offset: str) -> str:
        return f""" {self.weight} {X_STROKE}╼ {repr(self.value)}"""

    def __code__(self, call: Callable, code: str) -> None:
        call(self.value, code)

    def __depth__(self, offset: int) -> int:
        return offset

    def __layer__(self, layers: list[list], offset: int):
        layers[offset].append(self)

    def to_tuple(self) -> Any:
        """Turn itself into a tuple

        Returns:
            Any: Self.value
        """
        return self.value

    def spread(self, calls: tuple[Callable, Callable], *args) -> Any:
        """Spread a call to the end of tree

        Here we call: calls[1](self, *args)

        Args:
            calls (tuple[Callable, Callable]): Correspond of 2 different call like: tuple[on_node, on_leaf]

        Returns:
            Any: Anything returned by calls[1]
        """
        return calls[1](self, *args)


class __NodeFragment:

    @property
    def depth(self) -> int:
        """Depth of node

        Returns:
            int: His maximal depth
        """
        return self.__depth__(1)

    @property
    def tree(self) -> str:
        """A simple string representation

        Returns:
            str: A visual tree
        """
        return self.__tree__('')

    @property
    def layers(self) -> list[list]:
        """Get each layers of a tree

        Returns:
            list[list]: List of layers by depth
        """
        layers = [[]]
        self.__layer__(layers, 0)
        return layers

    def spread(self, calls: tuple[Callable, Callable], *args) -> Any:
        """Spread a call into a tree 

        Here we call: calls[0](self, calls, *args)

        Args:
            calls (tuple[Callable, Callable]): Correspond of 2 different call like: tuple[on_node, on_leaf]

        Returns:
            Any: Anything returned by calls[0]
        """
        return calls[0](self, calls, *args)


# * Binary tree


class __BinFragment(__Fragment):

    def __add__(self, fragment: __BinFragment) -> BinNode:
        """Sum 2 __BinFragment into a new parent Node

        Args:
            fragment (__BinFragment): A binary tree fragment

        Returns:
            BinNode: Parent Node
        """
        return BinNode(self.weight + fragment.weight, self, fragment)


class BinLeaf(__LeafFragment, __BinFragment):
    ...


@dataclass(repr=False)
class BinNode(__BinFragment, __NodeFragment):

    """A binary node of a tree

    It can contain only two child (left and right)

    Args:
        weight (int): Weight of node
        left (__BinFragment): First child of node
        right (__BinFragment): Last child of node
    """

    left: __BinFragment
    right: __BinFragment

    def __len__(self) -> int:
        """Get total number of BinNode and BinLeaf

        Returns:
            int: Total number of __BinFragment of the tree
        """
        return len(self.left) + len(self.right) + 1

    def __tree__(self, offset: str) -> str:
        indent = offset + f"│\n{offset}" * Y_SPACE
        return f"""┮ {self.weight}\n{indent}├{X_STROKE}{self.left.__tree__(f"{offset}│{X_INDENT}")}\n{indent}└{X_STROKE}{self.right.__tree__(f"{offset} {X_INDENT}")}"""

    def __code__(self, call: Callable, code: str) -> None:
        self.left.__code__(call, f"{code}0")
        self.right.__code__(call, f"{code}1")

    def __depth__(self, offset: int) -> int:
        offset += 1
        return max(self.left.__depth__(offset), self.right.__depth__(offset))

    def __layer__(self, layers: list[list], offset: int):
        layers[offset].append(self)
        offset += 1
        if offset == len(layers):
            layers.append([])
        self.left.__layer__(layers, offset)
        self.right.__layer__(layers, offset)

    @classmethod
    def __from_tuple__(cls, value: tuple | Any) -> __BinFragment:
        if isinstance(value, tuple):
            return cls.__from_tuple__(value[0]) + cls.__from_tuple__(value[1])
        else:
            return BinLeaf(1, value)

    @classmethod
    def from_tuple(cls, root: tuple) -> BinNode:
        """Build itself from a tuple

        Args:
            root (tuple): A tuple version of a binary tree

        Raises:
            ChildError: If the tuple have less than 2 children

        Returns:
            BinNode: A binary node corresponding to the tuple (absolute)
        """
        lenght = len(root)
        if lenght < 2:
            raise ChildError(f"require at least 2 children ({lenght} given)")
        left = cls.__from_tuple__(root[0])
        right = cls.__from_tuple__(root[1])
        return cls(left.weight + right.weight, left, right)

    def to_tuple(self) -> tuple[tuple | Any]:
        """Turn itself into a tuple

        Returns:
            tuple[tuple | Any]: Self but converted
        """
        return (self.left.to_tuple(), self.right.to_tuple())

    def code(self, call: Callable) -> None:
        """Get mapping code of binary tree

        Args:
            call (Callable): Something to call when ending into leaf
        """
        self.left.__code__(call, '0')
        self.right.__code__(call, '1')


# * Multi child tree


class __MulFragment(__Fragment):

    def __add__(self, fragment: __MulFragment) -> Node:
        """Sum 2 __MulFragment into a new parent Node

        Args:
            fragment (__MulFragment): A tree fragment

        Returns:
            Node: Parent Node
        """
        return Node(self.weight + fragment.weight, [self, fragment])


class Leaf(__LeafFragment, __MulFragment):
    ...


class Node(__MulFragment, __NodeFragment, list):

    """A node of a tree

    It can contain an open mount of child (from 1 to infinit)

    Args:
        weight (int): Weight of node
        childs (Iterable): Children of node
    """

    def __init__(self, weight: int, childs: Iterable):
        self.weight = weight
        self.extend(childs)

    def __len__(self) -> int:
        """Get total number of Node and Leaf

        Returns:
            int: Total number of __MulFragment of the tree
        """
        return sum(len(child) for child in self) + list.__len__(self)

    def __lshift__(self, child: __MulFragment) -> Node:
        """Insert a child from right

        Args:
            child (__MulFragment): A tree fragment

        Returns:
            Node: Self
        """
        self.append(child)
        self.weight += child.weight
        return self

    def __rshift__(self, child: __MulFragment) -> Node:
        """Insert a child from left

        Args:
            child (__MulFragment): A tree fragment

        Returns:
            Node: Self
        """
        self.insert(0, child)
        self.weight += child.weight
        return self

    def __or__(self, node: Node) -> Node:
        """Merge a node in self

        Args:
            node (Node): A tree Node

        Returns:
            Node: Self
        """
        self.extend(node)
        self.weight += node.weight
        return self

    def __tree__(self, offset: str) -> str:
        indent = offset + f"│\n{offset}" * Y_SPACE
        repr_ = f"┮ {self.weight}\n"
        for i in range(list.__len__(self) - 1):
            repr_ += f"""{indent}├{X_STROKE}{self[i].__tree__(f"{offset}│{X_INDENT}")}\n"""
        return repr_ + f"""{indent}└{X_STROKE}{self[-1].__tree__(f"{offset} {X_INDENT}")}"""

    def __code__(self, call: Callable, code: str) -> None:
        for i, child in enumerate(self):
            child.__code__(call, f"{code}{i}")

    def __depth__(self, offset: int) -> int:
        offset += 1
        return max(child.__depth__(offset) for child in self)

    def __layer__(self, layers: list[list], offset: int):
        layers[offset].append(self)
        offset += 1
        if offset == len(layers):
            layers.append([])
        for child in self:
            child.__layer__(layers, offset)

    @classmethod
    def __from_tuple__(cls, value: tuple | Any) -> Node | Leaf:
        if isinstance(value, tuple):
            node = cls(0, ())
            for child in value:
                node << cls.__from_tuple__(child)
            return node
        else:
            return Leaf(1, value)

    @classmethod
    def from_tuple(cls, root: tuple) -> Node:
        """Build itself from a tuple

        Args:
            root (tuple): A tuple version of a tree

        Raises:
            ChildError: If the tuple have less than 2 children

        Returns:
            Node: A node corresponding to the tuple (absolute)
        """
        lenght = len(root)
        if lenght < 2:
            raise ChildError(f"require at least 2 children ({lenght} given)")
        node = cls(0, ())
        for child in root:
            node << cls.__from_tuple__(child)
        return node

    def to_tuple(self) -> tuple[tuple | Any]:
        """Turn itself into a tuple

        Returns:
            tuple[tuple | Any]: Self but converted
        """
        return *(child.to_tuple() for child in self),

    def code(self, call: Callable) -> None:
        """Get mapping code of binary tree

        Args:
            call (Callable): Something to call when ending into leaf
        """
        for i, child in enumerate(self):
            child.__code__(call, str(i))


# * Tree build functions


def huff_tree(iterable: Iterable) -> BinNode:
    """Create an huffman binary tree

    Build an huffman binary tree based on frequency in a sequencable object

    Args:
        iterable (Iterable): Any sequence iterable

    Raises:
        ChildError: If you pass a sequence with less than 2 children

    Returns:
        BinNode: The root of the tree
    """
    entropy_map = defaultdict(int)
    for k in iterable:
        entropy_map[k] += 1

    lenght = len(entropy_map)
    if lenght < 2:
        raise ChildError(f"require at least 2 children ({lenght} given)")

    stack = [BinLeaf(v, k) for k, v in entropy_map.items()]
    # Sum every time the 2 lightest node / leaf
    heapify(stack)
    left = heappop(stack)
    for _ in range(2, lenght):
        left = heappushpop(stack, left + heappop(stack))  # That just an optimization
    return left + stack[0]  # return the root