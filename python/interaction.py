from browser import document as dom
from browser import html, DOMEvent, window, timer
import tictactoe as ttt


class ThemeColor:
    """
    selection of colors used in the UI design
    """
    sel: str = "#22263f"
    unsel: str = "#7399c6"
    blue: str = "#4c94df"
    green: str = "#1ea382"
    orange: str = "#f4a83e"
    purple: str = "#6145b2"
    disabled: str = "#b0b0b0"


# GLOBAL VARIABLES
class Config:
    """
    global configurations (a total of 8) to keep track of

    Class Attributes:
        - BOARD_SIDE_LENGTH: the side length of the game board
        - WINNING_STEP_LEN: the number of adjacent pieces that will result in a win;
          currently unused due to implementation complexity and timme constraint, will be
          used in the future
        - PLAYER_1_PIECE: the game piece used by player 1, either 'x' or 'o'
        - START_FIRST: which player starts first, either 'p1' or 'p2'
        - PLAYER_2_ROLE: whether player 2 is another human or some kind of AI player
        - PLAYER_1_COLOR: the color of player 1's game piece; always is Theme purple
        - PLAYER_2_COLOR: the color of player 2's game piece; is Theme orange if player 2
          is human, is Theme green if player 2 is an AI
        - GAME_OBJS: a dictionary containing the game object as well as the two player
          objects; can be obtained by any function that needs it
    """
    BOARD_SIDE_LENGTH: int = 3
    WINNING_STEP_LEN: int = 3  # currently unused but can be used when extended
    PLAYER_1_PIECE: str = 'x'
    START_FIRST: str = "p1"  # p1 -> player 1; p2 -> player 2; nd -> not determined
    PLAYER_2_ROLE: str = "ai_easy"
    PLAYER_1_COLOR: str = ThemeColor.purple
    PLAYER_2_COLOR: str = ThemeColor.green
    GAME_OBJS: dict = {}
    WIN_STATUS: bool = False


def draw_board(table: html.TABLE, side: int) -> None:
    """
    draw the game board of a given side-length onto te given `html.TABLE`
    """
    table.text = ""
    for i in range(side):
        tr = html.TR()
        for j in range(side):
            td = html.TD(html.SPAN(Class="cell", name=f"{i}{j}"))
            tr.append(td)
        table.attach(tr)

    # set table cell size according to side length
    dom["table_adjustments"].text = f"""
    /* set table cell size for side length of {side} */
    table td{{width: {90/side}%;}}  /* (90/{side})% */
    @media screen and (min-width: 1024px)
    {{
        table td{{width: {60/side}%;}}  /* (60/{side})% */
    }}
    @media screen and (min-width: 1500px)
    {{
        table td{{width: {45/side}%;}}  /* (45/{side})% */
    }}
    """

    # update the global side length winning step length
    Config.BOARD_SIDE_LENGTH = side
    Config.WINNING_STEP_LEN = side


def switch_selection(
    selected: html.BUTTON,
    button_class: str,
    colortype: str = "background-color"
) -> None:
    """
    helper function to remove darkened background from all buttons in the
    `button_class`, and darken the `selected` button
    changes the foreground or background collor based on the `colortype` option
    """
    # clear background color for all buttons in the `button_class`
    for b in dom.select(button_class):
        if b.name != selected.name:
            b.attrs["style"] = ""

    # darken `selected` button's background color
    selected.attrs["style"] = f"{colortype}: {ThemeColor.sel};"


def disable_button(button: html.BUTTON) -> None:
    """
    helper function to disable a specific button and set its style to show the
    disabled state
    """
    button.attrs["style"] = ""
    button.classList.add("btn-dis")
    button.disabled = True


def enable_button(button: html.BUTTON) -> None:
    """
    helper function to enable a specific button and set its style to show the
    enabled state
    """
    button.classList.remove("btn-dis")
    button.disabled = False


def ev_board_size(event: DOMEvent) -> None:
    """
    change the board size based on the given button event
    """
    target = event.target

    # change the button colors to reflect user selection
    switch_selection(target, ".btn-len")

    # grab new side length and redraw board
    new_side_len = int(target.name[-1])
    draw_board(dom['board'], new_side_len)

    # disable or enable winning step buttons as necessary
    for b in dom.select('.btn-win'):
        if int(b.name[-1]) > new_side_len:
            disable_button(b)
        elif int(b.name[-1]) == new_side_len:
            enable_button(b)
            b.attrs["style"] = f"background-color: {ThemeColor.sel};"
        else:
            enable_button(b)
            b.attrs["style"] = f"background-color: {ThemeColor.unsel};"

    # log the change in the broswer console
    print(f"Changed board side length to: {new_side_len}")


def ev_win_step(event: DOMEvent) -> None:
    """
    [!] this function is currently unused, but may be used in the future

    change the number of steps required to win the game based on the
    given button event; write the result into the configuration variable
    `Config.WINNING_STEP_LEN`
    """
    target = event.target

    # change the button colors to reflect user selection
    switch_selection(target, ".btn-win")

    # grab new winning length and set the global variable
    Config.WINNING_STEP_LEN = int(target.name[-1])

    # log the change in the broswer console
    print(f"Set winning step length to: {Config.WINNING_STEP_LEN}")


def ev_player1_piece(event: DOMEvent) -> None:
    """
    change the game piece (x/o) used by player 1 based on the given
    button event;
    write the result into the configuration variable `Config.PLAYER_1_PIECE`
    """
    target = event.target

    # change the button colors to reflect user selection
    switch_selection(target, ".btn-piece", colortype="color")

    # grab new player 1 game piece and set the global variable
    Config.PLAYER_1_PIECE = target.name[-1]

    # log the change in the broswer console
    print(f"Changed Player 1's game piece to: {Config.PLAYER_1_PIECE}")


def ev_who_starts_first(event: DOMEvent) -> None:
    """
    change the whether player 1 or player 2 starts first, or determine
    by a random draw, based on the given button event
    write the result into the configuration variable `Config.START_FIRST`
    """
    target = event.target

    # change the button colors to reflect user selection
    switch_selection(target, ".btn-st")

    # grab new starting player and set the global variable
    Config.START_FIRST = target.name[-2:]

    # log the change in the broswer console
    print(f"Player {Config.START_FIRST} will start first.")


def ev_player_2_role(event: DOMEvent) -> None:
    """
    change the role of player 2, between `another_human`, `ai_random`, `ai_easy`,
    and `ai_hard`
    write the result into the configuration variable `Config.PLAYER_2_ROLE`
    also adjust `Config.PLAYER_2_COLOR` to be green if player 2 is an AI, or orange if
    player 2 is a human
    """
    target = event.target

    # find the selected option
    selected = [option.value for option in target if option.selected]

    # grab new starting player and set the global variable
    Config.PLAYER_2_ROLE = selected[0]

    # change game piece color depending on player 2's role
    if Config.PLAYER_2_ROLE[:2] == "ai":
        Config.PLAYER_2_COLOR = ThemeColor.green
    else:
        Config.PLAYER_2_COLOR = ThemeColor.orange

    # log the change in the broswer console
    print(f"Player 2 will be {Config.PLAYER_2_ROLE}")


def bind_cells() -> None:
    """
    bind all cells on the game board UI to their event functions
    """
    for c in dom.select('.cell'):
        c.bind("mouseover", cell_hover)
        c.bind("mouseout", cell_unhover)
        c.bind("click", cell_click)


def cell_hover(event: DOMEvent) -> None:
    """
    event function that responds to a cell when a mouse cursor hovers
    displays a grayed out game piece on top of the hovered cell
    """
    target = event.target
    which_player = Config.GAME_OBJS["game"].next_player
    piece = Config.PLAYER_1_PIECE if which_player == "p1" else ttt.piece_not(Config.PLAYER_1_PIECE)
    target.text = piece


def cell_unhover(event: DOMEvent) -> None:
    """
    event function that responds to a cell when a mouse cursor NO LONGER hovers
    removes the grayed out game piece on top of the hovered cell
    """
    target = event.target
    target.text = ''


def cell_click(event: DOMEvent) -> None:
    """
    event function that responds to a cell when being clicked
    permanently place the game piece in the cell with the correct color, unbinds all the
    event functions on this cell, and trigger a game round
    """
    target = event.target
    print(f"Clicked {target.attrs['name']}")

    # determine the player that clicked this cell, and its game piece
    which_player = Config.GAME_OBJS["game"].next_player
    piece = Config.PLAYER_1_PIECE if which_player == "p1" else ttt.piece_not(Config.PLAYER_1_PIECE)

    # place game piece and unbind event functions
    target.text = piece
    target.unbind("click", cell_click)
    target.unbind("mouseout", cell_unhover)
    target.unbind("mouseover", cell_hover)

    # set the correct color for the placed game piece
    if which_player == 'p1':
        target.attrs["style"] = f"color: {Config.PLAYER_1_COLOR};"
    else:
        target.attrs["style"] = f"color: {Config.PLAYER_2_COLOR};"

    # trigger a round of game
    timer.set_timeout(ev_game_round, 0, event)


def draw_piece(piece: str, spot: str):
    """
    helper function to draw a given game piece at the given spot on the game board UI
    """
    for c in dom.select('.cell'):
        if c.attrs["name"] == spot:
            c.text = piece

            # unbind event functions once the piece has been drawn
            c.unbind("click", cell_click)
            c.unbind("mouseout", cell_unhover)
            c.unbind("mouseover", cell_hover)

            # give the piece its correct color
            if piece == Config.PLAYER_1_PIECE:
                c.attrs["style"] = f"color: {Config.PLAYER_1_COLOR};"
            else:
                c.attrs["style"] = f"color: {Config.PLAYER_2_COLOR};"


def check_winner(game: ttt.GameState):
    """
    given the game state, check for winners;
    if a winner is found, announce it to the game status and set Config.WIN_STATUS to
    `True`;
    otherwise prompt the next player to play
    """
    # check for winners
    if winning_piece := game.get_winning_piece():

        # find out whether player 1 or 2 won the game
        if winning_piece not in {'x', 'o'}:
            announce_txt = "It's a tie!"
        else:
            winner_num = 1 if winning_piece == Config.PLAYER_1_PIECE else 2
            announce_txt = f"Player {winner_num} wins!"

        # announce the winner
        dom['game_status'].html = f"""
            <span style="color: #dd426e; display: inline;">
                {announce_txt}
            </span><br>
            <span style="font-size: 0.7em; display: inline;">
                Press the Reset button to start a new game.
            </span>
        """

        # disable game board cells
        for c in dom.select('.cell'):
            c.unbind("click", cell_click)
            c.unbind("mouseout", cell_unhover)
            c.unbind("mouseover", cell_hover)

        # log the winner in the browser console
        print(announce_txt)

        Config.WIN_STATUS = True

    # if no winners, announce the next player's turn
    else:
        print(f"Player {game.next_player[-1]}'s turn.")
        dom['game_status'].html = f"""
            Player {game.next_player[-1]}'s turn.
        """


def ai_make_move(player: ttt.Player, game: ttt.GameState, prev_move: str) -> None:
    """
    helper function to obtain the player's move, place the game piece, and draw it on the
    UI
    """
    piece, spot = player.return_move(game, prev_move)
    game.place_piece(piece, spot)
    draw_piece(piece, spot)


def ai_move_if_not_won(game: ttt.GameState) -> None:
    """
    schedule the next AI move if the game is not won and the next player is not human
    """
    if not Config.WIN_STATUS:
        player_next = Config.GAME_OBJS[game.next_player]
        if player_next != "human":
            # obtain the player's move, place the game piece, and draw it on the UI
            dom['game_status'].text = dom['game_status'].text + ".."
            timer.set_timeout(ai_make_move, 0, player_next, game, game.move_history[-1])

        # check for winners again
        timer.set_timeout(check_winner, 0, game)


def ev_game_round(event: DOMEvent) -> None:
    """
    advance a round of the game based on the current game state
    can be triggered by the start_game function or a player making a move
    """
    target = event.target

    # fetch the game object as well as the next player's object
    game = Config.GAME_OBJS["game"]
    player = Config.GAME_OBJS[game.next_player]

    # use the check winner function to show which player's turn it is
    check_winner(game)

    # when we start a fresh game and AI starts first
    if target.attrs['name'] == "start" and player != "human":
        # obtain the player's move, place the game piece, and draw it on the UI
        dom['game_status'].text = dom['game_status'].text + ".."
        timer.set_timeout(ai_make_move, 0, player, game, None)

    # when getting called by a human player, place the piece for the human
    elif "cell" in target.classList:
        spot = target.attrs['name']
        if game.next_player == "p1":
            piece = Config.PLAYER_1_PIECE
        else:
            piece = ttt.piece_not(Config.PLAYER_1_PIECE)
        game.place_piece(piece, spot)

    # check for winners and announce who's turn
    timer.set_timeout(check_winner, 0, game)

    # make the next move if the game is not won and the next player is not human
    timer.set_timeout(ai_move_if_not_won, 0, game)


def ev_start_game(event: DOMEvent) -> None:
    """
    start the game by calling the initializer and calling the first round
    """
    # log the start of the game in the browser console
    print("Game started.")

    # initialize the game by calling the initializer in the tictactoe module
    game, p1, p2 = ttt.init_game(
        Config.BOARD_SIDE_LENGTH,
        Config.PLAYER_1_PIECE,
        Config.START_FIRST,
        Config.PLAYER_2_ROLE,
        p1_role="human"
    )

    # update the game objects store according to the newly initialized game
    Config.GAME_OBJS["game"] = game
    Config.GAME_OBJS["p1"] = p1
    Config.GAME_OBJS["p2"] = p2

    # bind trigger functions for each cell of the game board UI
    bind_cells()

    # replace the start button with the reset button
    event.target.attrs["style"] = "display: none;"
    dom["btn_reset"].attrs["style"] = ""

    # trigger the first round in the game
    # timer.set_timeout(ev_game_round, 0, event)
    ev_game_round(event)


def ev_reset_game(event) -> None:
    """
    this function gets triggered by the reset button, and it refershes the browser page
    """
    window.location.reload()


if __name__ == '__main__':
    # just for testing ;)
    print("https://sammdu.com")

    # draw a 3x3 board by default
    draw_board(dom['board'], 3)

    # indicate that the game is ready
    dom['game_status'].html = """
    Please select your options,
    <span style="display: inline-block;">and click "Start" to begin!</span>
    """

    # show the start button once game has loaded
    dom["btn_start"].attrs["style"] = ""

    # enforce a deafult value for the player 2 role select menu
    dom["player_2_role"].value = Config.PLAYER_2_ROLE

    # bind functions to buttons
    for b in dom.select('.btn-len'):
        b.bind("click", ev_board_size)
    # for b in dom.select('.btn-win'):
    #     b.bind("click", ev_win_step)
    for b in dom.select('.btn-piece'):
        b.bind("click", ev_player1_piece)
    for b in dom.select('.btn-st'):
        b.bind("click", ev_who_starts_first)
    dom["player_2_role"].bind("change", ev_player_2_role)
    dom["btn_start"].bind("click", ev_start_game)
    dom["btn_reset"].bind("click", ev_reset_game)
