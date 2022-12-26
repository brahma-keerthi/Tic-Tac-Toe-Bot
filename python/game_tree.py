from __future__ import annotations
from typing import Optional, Any


class GameTree:
    placement: Optional[str]
    is_x_move: bool
    x_win_score: int

    # Private Instance Attributes:
    #  - _subtrees:
    #      the subtrees of this tree, which represent the game trees after a possible
    #      placement by the current player
    _subtrees: list

    def __init__(
            self,
            placement: Optional[str] = None,
            is_x_move: bool = True,
            x_win_score: int = 0
    ) -> None:
        """
        initialize a new game tree

        >>> gt = GameTree()
        >>> gt.placement is None
        True
        >>> gt.is_x_move
        True
        >>> gt.x_win_score
        0
        """
        self.placement = placement
        self.is_x_move = is_x_move
        self._subtrees = []
        self.x_win_score = x_win_score

    def get_subtrees(self) -> list:
        """
        return all subtrees under the current game tree
        """
        return self._subtrees

    def find_subtree_by_spot(self, spot: str) -> Any:
        """
        find a particular subtree whose node contains the given spot

        this is only a depth-1 enumeration of the subtrees of the given node, and not an
        exhausive search in the entire game tree
        """
        for subtree in self._subtrees:
            if subtree.placement == spot:
                return subtree
        return None

    def add_subtree(self, subtree: Any) -> None:
        """
        append the given subtree to the current game tree's list of subtrees
        """
        self._subtrees.append(subtree)

    def __str__(self, depth: int = 0) -> str:
        """
        return a string representation of the current game tree
        """
        piece = 'x' if self.is_x_move else 'o'
        string = ('    ' * depth) + "  `---" + \
            f"[{piece} -> ({self.placement})]:" + \
            f" {self.x_win_score} \n"
        if self._subtrees == []:
            return string
        else:
            for subtree in self._subtrees:
                string += subtree.__str__(depth + 1)
            return string


if __name__ == '__main__':
    import doctest
    doctest.testmod()
