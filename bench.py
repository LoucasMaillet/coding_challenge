#!/usr/bin/env python3.10
# coding: utf-8

from pytree.pytree import BinNode, Node

if __name__ == "__main__":

    #     root = Leaf(1, "eeeuuh") + (Leaf(1, 5) + Leaf(1, 5) << Leaf(1, 88) << Leaf(5, "Hi"))
    #     root >> Leaf(4, "Hello world")
    #     root << Leaf(1, "aaa") + Leaf(1, "sdsdfdsf")
    #     print(root.tree)

    # t = (5, 6, 5, (4, ("hi", ), 2))
    t = ((('e', 'p'), ('a', 'k')), (('d', 'W'), 'i'))
    tree = BinNode.from_tuple(t)
    # tree = Leaf(1, "eeeuuh") + (Leaf(1, 5) + Leaf(1, 5) << Leaf(1, 88) << Leaf(5, "Hi"))
    # tree = huff_tree("Hello world")
    tree.code(print)
    print(tree.tree)
    print(tree.depth)
    print(tree.layers)
    print(tree.to_tuple())

#     t = (5, (6, (9, 2)))
#     print(BinNode.from_tuple(t).tree)

#     tree = huff_tree("Wikipedia")
#     print(tree.tree)

    def on_node(node, rmap, code):
        node.left.spread(rmap, code + '0')
        node.right.spread(rmap, code + '1')

    def on_leaf(leaf, code):
        print(leaf.value, code)

    tree.spread((on_node, on_leaf), '')
    print(tree.layers)