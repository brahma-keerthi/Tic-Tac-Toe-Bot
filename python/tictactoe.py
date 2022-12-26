from __future__ import annotations
from typing import Optional, Any, Union
import random
import copy
import game_tree as gt


################################################################################
# Tic Tac Toe game representation
################################################################################

def empty_board(side: int) -> list:
    """
    generate an empty game board (list of lists) with sidelength `side`

    >>> empty_board(3)
    [['', '', ''], ['', '', ''], ['', '', '']]
    """
    board = []
    for _ in range(side):
        row = [''] * side
        board.append(row)
    return board


class GameState():
    """
    Instance Attributes:
        - next_player: the player from {'p1', 'p2'} that will place the next game piece
        - empty_spots: a list of vacant spot on the game board available to be filled
        - move_history: a history of moves that occured in this game
    """
    next_player: str
    empty_spots: list[Optional[str]]
    move_history: list[Optional[str]]

    # Private Instance Attributes:
    #   - _board: a nested list representing a tictactoe board
    #   - _board_side: the side length of the board
    _board: list[list[str]]
    _board_side: int

    def __init__(
            self,
            board: list[list[str]],
            next_player: str = 'p1',
            move_hist: Optional[list] = None
    ) -> None:
        self._board = board
        self._board_side = len(self._board)  # calculate the side length of the game board
        self.move_history = move_hist if move_hist is not None else []
        self.next_player = next_player
        self.empty_spots = self._find_empty_spots()

    def _find_empty_spots(self) -> list[Optional[str]]:
        empty_spots = []
        for row_idx in range(self._board_side):
            for col_idx in range(self._board_side):
                if self._board[row_idx][col_idx] == '':
                    empty_spots.append(str(row_idx) + str(col_idx))
        return empty_spots

    def get_side_length(self) -> int:
        """
        return the board's side length
        """
        return self._board_side

    def place_piece(self, piece: str, spot: str) -> None:
        """
        place the given piece on the given spot on the game board, if the spot is empty;
        ensure that the spot given exists on the board (is not out of range)

        Preconditions:
            - `spot` must be a string of two integers, first representing the row, second
              representing the column in the board. `ValueError`s will be raised if this
              is not satisfied
            - the spot must be empty, or a `ValueError` will be raised
            - piece in {'x', 'o'}
        """
        row = int(spot[0])
        col = int(spot[1])

        if row > self._board_side or row < 0:
            raise ValueError(f"[!] Given row {row} in spot {spot} is out of range.")
        if col > self._board_side or col < 0:
            raise ValueError(f"[!] Given column {col} in spot {spot} is out of range.")

        if spot in self.empty_spots:  # check if the spot is empty
            self._board[row][col] = piece
            self.empty_spots.remove(spot)
            self.next_player = 'p2' if self.next_player == 'p1' else 'p1'
            self.move_history.append(spot)
        else:
            raise ValueError(f"[!] Given spot {spot} is not empty.")

    def copy_and_place_piece(self, piece: str, spot: str) -> Any:
        """
        make a copy of the current game state, make a move in the game state copy, and
        return the game state copy object
        """
        next_player = 'p2' if self.next_player == 'p1' else 'p1'
        new_board = copy.deepcopy(self._board)
        new_hist = copy.deepcopy(self.move_history)
        new_game = GameState(new_board, next_player, new_hist)
        new_game.place_piece(piece, spot)
        return new_game

    def get_winning_piece(self) -> str:
        """
        return 'x' or 'o' or `None` as the winner of the game in its current state
        """
        # check each row
        for row in self._board:
            if all(spot == 'x' for spot in row):
                return 'x'
            elif all(spot == 'o' for spot in row):
                return 'o'

        # grab the side length fo the game board
        side = self._board_side

        # if no winners in rows, check each column
        for col_num in range(side):
            if all(row2[col_num] == 'x' for row2 in self._board):
                return 'x'
            elif all(row2[col_num] == 'o' for row2 in self._board):
                return 'o'

        # if still no winners, check the two diagonals
        # top-left to bottom-right
        if all(self._board[i][i] == 'x' for i in range(side)):
            return 'x'
        elif all(self._board[i][i] == 'o' for i in range(side)):
            return 'o'
        # top-right to bottom-left
        if all(self._board[i][side - i - 1] == 'x' for i in range(side)):
            return 'x'
        elif all(self._board[i][side - i - 1] == 'o' for i in range(side)):
            return 'o'

        # if there are no empty spots in the board then it's a tie
        # [*] this can be improved by predicting early ties, but I won't implement it
        # right now
        if not self.empty_spots:
            return "tie"

        # otherwise there's no winner yet
        return None


################################################################################
# Player Classes
################################################################################

class Player:
    """
    An abstract class representing a Tic Tac Toe player.

    [c] This class and its subclasses took inspiration from "CSC111 Winter 2021 Assignment
        2: Trees, Chess, and Artificial Intelligence (Game Tree)", by David Liu and Isaac
        Waller
    """
    # Private Instance Attributes:
    #   - _piece: game piece of the current player, either `x` or `o`
    _piece: str

    def __init__(self, piece: str) -> None:
        assert piece in {'x', 'o'}
        self._piece = piece

    def return_move(self, game: GameState, prev_move: str) -> tuple[str, str]:
        """
        return the game piece {'x', 'o'} and a move in the given game state

        `prev_move` is the opponent player's most recent move, or `None` if no moves
        have been made
        """
        raise NotImplementedError


class AIRandomPlayer(Player):
    """
    An 'AI' player that simply makes random moves that are available in the game state.
    """

    def return_move(self, game: GameState, prev_move: str) -> tuple[str, str]:
        """
        return the game piece {'x', 'o'} and a move in the given game state;
        for this player, the move will be chosen at random from the available empty spots

        `prev_move` is the opponent player's most recent move, or `None` if no moves
        have been made; not used by `AIRandomPlayer`
        """
        return self._piece, random.choice(game.empty_spots)


class AIMinimaxPlayer(Player):
    """
    An 'AI' player that employs a MiniMax algorithm on a game tree to make moves in the
    game state.

    Instance Attributes:
        - `difficulty`: "easy" or "hard"; used to determine search depth of the algorithm
        - `is_x`: True if my piece is 'x', False if my piece is 'o'
    """
    difficulty: str
    is_x: bool

    # Private Instance Attributes:
    #   - _tree: game tree generated by the current player
    _tree: gt.GameTree
    _depth: int

    def __init__(self, piece: str, difficulty: str) -> None:
        super().__init__(piece)
        self.difficulty = difficulty
        self.is_x = True if piece == 'x' else False
        # initialize an empty game tree with my piece, and a 0 x win score
        self._tree = gt.GameTree(None, self.is_x, 0)

    @staticmethod
    def _score_node(game: GameState) -> int:
        """
        return a Minimax utility score based on the given game state

        There is a scoring constant of '1' when 'x' wins, '-1' when 'x' loses, or '0'
        otherwise; this constant is multiplied by the number of empty spots left in the
        game, to incentivize victory in the fewest steps

        The idea of multiplying the number of empty spots with the scoring constant
        {1, -1, 0} to reward wins made in fewer steps came from this video:
            https://youtu.be/fT3YWCKvuQE
        NO OTHER IDEAS OR CODE CAME FROM THE ABOVE SOURCE
        """
        piece = game.get_winning_piece()
        if piece == 'x':
            return 1 * len(game.empty_spots)
        elif piece == 'o':
            return -1 * len(game.empty_spots)
        else:
            return 0

    def _gen_subtrees(self, node: gt.GameTree, game: GameState) -> None:
        """
        generate subtrees for a given node based on the available moves in the game
        """
        assert node.get_subtrees() == []
        for spot in game.empty_spots:
            piece = 'o' if node.is_x_move else 'x'
            mock_game = game.copy_and_place_piece(piece, spot)
            score = self._score_node(mock_game)
            node.add_subtree(gt.GameTree(spot, not node.is_x_move, score))

    def _minimax(
            self,
            tree: gt.GameTree,
            game: GameState,
            depth: int,
            piece: str,
            alpha: Union[float, int],
            beta: Union[float, int]
    ) -> None:
        """
        perform the minimax algorithm with Alpha-Beta pruning recursively to a given depth
        each subtree to to the given gepth will contain a calculated minimax score as a
        result
        see `_score_node` for the scoring scheme
        """
        assert piece in {'x', 'o'}

        # if we get a winner, or reach the depth limit, or reach a tie, return score;
        # static evaluation
        if depth == 0 or game.get_winning_piece():
            tree.x_win_score = self._score_node(game)

        # maximizer, 'x'
        elif piece == 'x':
            max_score = -1 * (game.get_side_length() ** 2) - 1
            subtrees = tree.get_subtrees()

            # generate subtrees if depth is not reached but no more subtrees are available
            if depth != 0 and subtrees == []:
                self._gen_subtrees(tree, game)

            # iterate through each subtree, compute the sub score, and maximize
            for subtree in subtrees:
                # if the placement recorded in teh current subtree has not been played in
                # the game yet, create a mock game to facilitate with minimax
                if subtree.placement not in game.move_history:
                    mock_game = game.copy_and_place_piece('x', subtree.placement)
                    self._minimax(subtree, mock_game, depth - 1, 'o', alpha, beta)
                # if the placement has been played alraedy, directly recurse
                else:
                    self._minimax(subtree, game, depth - 1, 'o', alpha, beta)

                max_score = max(max_score, subtree.x_win_score)
                # update the alpha score, and prune if possible
                alpha = max(alpha, subtree.x_win_score)
                if beta <= alpha:
                    break

            tree.x_win_score = max_score

        # minimizer, 'o'
        else:
            min_score = 1 * (game.get_side_length() ** 2) + 1
            subtrees = tree.get_subtrees()

            # generate subtrees if depth is not reached but no more subtrees are available
            if depth != 0 and subtrees == []:
                self._gen_subtrees(tree, game)

            # iterate through each subtree, compute the sub score, and minimize
            for subtree in subtrees:
                if subtree.placement not in game.move_history:
                    mock_game = game.copy_and_place_piece('o', subtree.placement)
                    self._minimax(subtree, mock_game, depth - 1, 'x', alpha, beta)
                else:
                    self._minimax(subtree, game, depth - 1, 'x', alpha, beta)

                min_score = min(min_score, subtree.x_win_score)
                # update the beta score, and prune if possible
                beta = min(beta, subtree.x_win_score)
                if beta <= alpha:
                    break

            tree.x_win_score = min_score

    def return_move(self, game: GameState, prev_move: Optional[str]) -> tuple[str, str]:
        """
        return the game piece {'x', 'o'} and a move in the given game state by the Minimax
        algorithm

        `prev_move` is the opponent player's most recent move, or `None` if no moves
        have been made
        """
        # set the search depth
        if self.difficulty == "easy":
            # easy mode will let the algorithm only search 3 steps ahead
            self._depth = 2
        else:
            # hard mode depends onthe board side length, due to computational complexity
            # side length to search depth mapping recorded in `depthmap`
            side = game.get_side_length()
            depthmap = {3: 5, 4: 4, 5: 3}
            self._depth = depthmap[side]

        if prev_move is None:
            for spot in game.empty_spots:
                self._tree.add_subtree(gt.GameTree(spot, self.is_x, 0))
        else:
            # update the game tree to start from the previous move made
            prevtree = self._tree.find_subtree_by_spot(prev_move)
            if prevtree is None:
                prevtree = gt.GameTree(prev_move, not self.is_x, 0)
                self._tree.add_subtree(prevtree)
            self._tree = prevtree

        # print(f"Initial subtrees:\n{self._tree}")

        # calculate the minimax score for each subtree
        subtrees = self._tree.get_subtrees()
        self._minimax(
            tree=self._tree,
            game=game,
            depth=self._depth,
            piece=self._piece,
            alpha=float("-inf"),
            beta=float("inf")
        )

        # return the max score placement or min score placement based on my piece
        if self._piece == 'x':
            spot_choice = max(subtrees, key=lambda s: s.x_win_score).placement
        else:
            spot_choice = min(subtrees, key=lambda s: s.x_win_score).placement

        # advance the tree after having made the placement decision
        self._tree = self._tree.find_subtree_by_spot(spot_choice)

        return self._piece, spot_choice


def role_to_player(role: str, piece: str) -> Player:
    """
    helper function to convert the string representation of a player's role and return a
    `Player` object accordingly; set the `Player` object's piece attribute as given
    """
    if role == "ai_random":
        return AIRandomPlayer(piece)
    elif role[:2] == "ai":
        return AIMinimaxPlayer(piece, role[-4:])  # role[-4:] is either "easy" or "hard"
    else:
        return "human"


def piece_not(piece: str) -> str:
    """
    helper function to return the other game piece that is not the current game piece

    Preconditions:
        - piece in {'x', 'o'}

    >>> piece_not('x')
    'o'
    >>> piece_not('o')
    'x'
    """
    return 'x' if piece == 'o' else 'o'


def init_game(
        board_side: int,
        p1_piece: str,
        start_first: str,
        p2_role: str,
        p1_role: str = 'human'
) -> tuple[GameState, Player, Player]:
    """
    initialize a Tic Tac Toe game on a board of given side length `board_side`;
    return the game object and the two player objects
    """
    assert start_first in {'p1', 'p2', 'nd'}

    # create a new game with the board's side lengtn given by `board_side`
    game = GameState(empty_board(board_side))

    # set player 2's game piece
    p2_piece = piece_not(p1_piece)

    # initialize players' classes
    player1 = role_to_player(p1_role, p1_piece)
    player2 = role_to_player(p2_role, p2_piece)

    # determine which player starts first if left up to random
    start_first = random.choice(['p1', 'p2']) if start_first == 'nd' else start_first
    # set the next player in the game state to be the first player
    game.next_player = start_first

    return game, player1, player2


if __name__ == '__main__':
    import doctest
    doctest.testmod()
