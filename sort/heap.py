#!/usr/bin/python3.10
# coding: utf-8

from typing import Any, Callable


class HeapBin(list):

    def __init__(self, *items: Any, key: Callable = lambda item: item):
        """Create a binary stack

        Args:
            items (Any): Some items to sort
            key (Callable, optional): A function to fetch the weight of each item to compare it after. Defaults to lambda item : item.
        """
        list.__init__(self, items)
        self.length: int = len(self)
        self.key: Callable = key
        self.weights: list[int] = [key(item) for item in items]
        self.__sort__()

    def __sort__(self):
        """Sort itself
        """
        for i in range(self.length // 2 - 1, -1, -1):
            self.__heapify__(self.length, i)
        for i in range(self.length - 1, 0, -1):
            self[i], self[0] = self[0], self[i]
            self.weights[i], self.weights[0] = self.weights[0], self.weights[i]
            self.__heapify__(i, 0)

    def __heapify__(self, n: int, i: int):
        """Heap itself (with recursivity)

        Args:
            n (int): Current top index
            i (int): Current item index
        """
        i_new = 0
        i_left = 2 * i + 1
        i_right = 2 * i + 2

        if i_right < n and self.weights[i] < self.weights[i_right]:
            i_new = i_right

        if i_left < n and self.weights[i_new] < self.weights[i_left]:
            i_new = i_left

        if i_new != 0:
            self[i], self[i_new] = self[i_new], self[i]
            self.weights[i], self.weights[i_new] = self.weights[i_new], self.weights[i]
            self.__heapify__(n, i_new)

    def append(self, item: Any):
        """Append an item

        Args:
            item (Any): Anything
        """
        list.append(self, item)
        self.weights.append(self.key(item))
        self.length += 1
        self.__sort__()

    def remove(self, index: int) -> Any:
        """Remove and return an item

        Args:
            index (int): Index of item

        Returns:
            Any: The item
        """
        item = list.pop(self, index)
        self.weights.pop(index)
        self.length -= 1
        self.__sort__()
        return item

    def shift(self) -> Any:
        """Remove and return the first item

        Returns:
            Any: First item
        """
        self.length -= 1
        self.weights.pop(0)
        return list.pop(self, 0)

    def pop(self) -> Any:
        """Remove and return the last item

        Returns:
            Any: Last item
        """
        self.length -= 1
        self.weights.pop(-1)
        return list.pop(self, -1)
