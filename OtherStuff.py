import tkinter as tk
from tkinter import ttk, messagebox
import time
from GameBoard import GameBoard
from SearchToolBox import SearchToolBox

# ----- CONSTANTS -----
S_OPTIONS = ["Minimax", "Alpha-Beta", "Alpha-Beta + Ordering"]
T_OPTIONS = [1, 2, 3]
P_OPTIONS = [5, 6, 7, 8, 9]

# ----- STYLE -----
SQUARE_SIZE = 60
BOARD_COLOR_DARK = "#D18B47"
BOARD_COLOR_LIGHT = "#FFCE9E"
HIGHLIGHT_COLOR = "#7CFC00"
PIECE_COLORS = {'w': 'white', 'W': 'white', 'b': 'black', 'B': 'black'}
KING_OUTLINE = 'gold'


# ----- GUI CLASS -----
class CheckersGUI:
    """Graphical user interface for playing checkers against an AI opponent."""
    
    def __init__(self, Root):
        """Initialize the checkers GUI with all controls and canvas.
        
        Args:
            Root: The Tkinter root window.
        """
        self.Root = Root
        self.Root.title("Checkers - Human (White) vs AI (Black)")

        # ---- Top Controls ----
        ControlFrame = ttk.Frame(Root)
        ControlFrame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)

        ttk.Label(ControlFrame, text="Search Algorithm (S):").grid(row=0, column=0, sticky=tk.W)
        self.SVar = tk.StringVar(value=S_OPTIONS[1])
        self.SMenu = ttk.Combobox(ControlFrame, textvariable=self.SVar, values=S_OPTIONS, width=22, state='readonly')
        self.SMenu.grid(row=0, column=1, padx=6)

        ttk.Label(ControlFrame, text="Time Limit (T s):").grid(row=0, column=2, sticky=tk.W)
        self.TVar = tk.IntVar(value=2)
        self.TMenu = ttk.Combobox(ControlFrame, textvariable=self.TVar, values=T_OPTIONS, width=5, state='readonly')
        self.TMenu.grid(row=0, column=3, padx=6)

        ttk.Label(ControlFrame, text="Depth (P):").grid(row=0, column=4, sticky=tk.W)
        self.PVar = tk.IntVar(value=5)
        self.PMenu = ttk.Combobox(ControlFrame, textvariable=self.PVar, values=P_OPTIONS, width=5, state='readonly')
        self.PMenu.grid(row=0, column=5, padx=6)

        StartButton = ttk.Button(ControlFrame, text="Start Game", command=self.StartGame)
        StartButton.grid(row=0, column=6, padx=8)

        # ---- Board ----
        CanvasSize = SQUARE_SIZE * 8
        self.Canvas = tk.Canvas(Root, width=CanvasSize, height=CanvasSize, bg='white')
        self.Canvas.pack(padx=8, pady=8)
        self.Canvas.bind("<Button-1>", self.OnCanvasClick)

        # ---- Game State ----
        self.Game = None
        self.Search = None
        self.CurrentPlayer = 'w'
        self.HighlightedOrigins = set()
        self.HighlightedDests = set()
        self.SelectedOrigin = None
        self.HighlightIDs = set()

    # ---------------- GAME LOGIC ----------------

    def StartGame(self):
        """Initialize a new game with the selected algorithm and parameters.
        
        Creates a new GameBoard and SearchToolBox, resets the game state,
        and renders the initial board position.
        """
        AlgorithmName = self.SVar.get()
        AlgorithmIndex = S_OPTIONS.index(AlgorithmName)
        TimeLimit = int(self.TVar.get())
        Depth = int(self.PVar.get())

        self.Game = GameBoard()
        self.Search = SearchToolBox(AlgorithmIndex)
        self.TimeLimit = TimeLimit
        self.Depth = Depth
        self.CurrentPlayer = 'w'
        self.SelectedOrigin = None

        self.DrawBoard()
        self.UpdateHighlights()
        self.DrawPieces()

    def DrawBoard(self):
        """Draw the checkerboard pattern on the canvas.
        
        Clears the canvas and draws alternating dark and light squares
        in the standard 8x8 checkerboard pattern.
        """
        self.Canvas.delete("all")
        for Row in range(8):
            for Col in range(8):
                Color = BOARD_COLOR_DARK if (Row + Col) % 2 == 0 else BOARD_COLOR_LIGHT
                self.Canvas.create_rectangle(
                    Col * SQUARE_SIZE, Row * SQUARE_SIZE,
                    (Col + 1) * SQUARE_SIZE, (Row + 1) * SQUARE_SIZE,
                    fill=Color, outline=''
                )

    def DrawPieces(self):
        """Draw all checker pieces on the board.
        
        Renders circular pieces for each occupied square, with special
        king indicators (gold outline) for promoted pieces.
        """
        self.Canvas.delete("piece")
        for Row in range(8):
            for Col in range(8):
                Piece = self.Game.BoardGrid[Row][Col]
                if Piece != '.':
                    X = Col * SQUARE_SIZE + SQUARE_SIZE / 2
                    Y = Row * SQUARE_SIZE + SQUARE_SIZE / 2
                    R = SQUARE_SIZE * 0.36
                    self.Canvas.create_oval(
                        X - R, Y - R, X + R, Y + R,
                        fill=PIECE_COLORS[Piece], outline='black', tags="piece"
                    )
                    if Piece in ['W', 'B']:
                        self.Canvas.create_oval(
                            X - R + 6, Y - R + 6, X + R - 6, Y + R - 6,
                            outline=KING_OUTLINE, width=3, tags="piece"
                        )

    def CoordFromClick(self, Event):
        """Convert mouse click coordinates to board position.
        
        Args:
            Event: The Tkinter click event containing x, y coordinates.
            
        Returns:
            A tuple of (row, col) if valid, None otherwise.
        """
        Col, Row = int(Event.x // SQUARE_SIZE), int(Event.y // SQUARE_SIZE)
        return (Row, Col) if 0 <= Row < 8 and 0 <= Col < 8 else None

    def UpdateHighlights(self):
        """Update the board highlights to show all movable white pieces.
        
        Clears existing highlights and draws green outlines around
        all white pieces that have valid moves available.
        """
        for ID in self.HighlightIDs:
            self.Canvas.delete(ID)
        self.HighlightIDs.clear()

        self.HighlightedOrigins.clear()
        MovesDict, _ = self.Game.GetValidMoves('w')
        for Origin in MovesDict.keys():
            self.HighlightedOrigins.add(Origin)
            H = self.Canvas.create_rectangle(
                Origin[1] * SQUARE_SIZE, Origin[0] * SQUARE_SIZE,
                (Origin[1] + 1) * SQUARE_SIZE, (Origin[0] + 1) * SQUARE_SIZE,
                outline=HIGHLIGHT_COLOR, width=3
            )
            self.HighlightIDs.add(H)

    def HighlightDestsFor(self, Origin):
        """Highlight valid destination squares for a selected piece.
        
        Args:
            Origin: The (row, col) coordinates of the selected piece.
        """
        for ID in self.HighlightIDs:
            self.Canvas.delete(ID)
        self.HighlightIDs.clear()

        MovesDict, _ = self.Game.GetValidMoves('w')
        for Dest in MovesDict.get(Origin, []):
            H = self.Canvas.create_rectangle(
                Dest[1] * SQUARE_SIZE, Dest[0] * SQUARE_SIZE,
                (Dest[1] + 1) * SQUARE_SIZE, (Dest[0] + 1) * SQUARE_SIZE,
                outline=HIGHLIGHT_COLOR, width=3
            )
            self.HighlightIDs.add(H)

    def OnCanvasClick(self, event):
        """Handle mouse clicks on the game board for human player moves.
        
        Args:
            event: The Tkinter click event.
            
        Processes piece selection and move execution for the white player,
        including multi-jump capture sequences.
        """
        if self.Game is None or self.CurrentPlayer != 'w':
            return

        Coord = self.CoordFromClick(event)
        if Coord is None:
            return

        # Selecting one of the movable white pieces
        if Coord in self.HighlightedOrigins:
            self.SelectedOrigin = Coord
            self.HighlightDestsFor(Coord)
            return

        
        if self.SelectedOrigin:
            MovesDict, _ = self.Game.GetValidMoves('w')
            AllowedMoves = MovesDict.get(self.SelectedOrigin, [])
            if Coord in AllowedMoves:
                # Perform move
                WasCapture = abs(Coord[0] - self.SelectedOrigin[0]) == 2
                self.Game.ApplyMove(self.SelectedOrigin, Coord)
                self.DrawBoard()
                self.DrawPieces()

                # Check for multi-jump
                MovesDict, CanCapture = self.Game.GetValidMoves('w')
                if WasCapture and CanCapture and Coord in MovesDict:
                    # Stay in same turn
                    self.SelectedOrigin = Coord
                    self.HighlightDestsFor(Coord)
                    return

                # Otherwise, end player turn
                self.SelectedOrigin = None
                Winner = self.Game.IsGameOver('w')
                if Winner:
                    self.ShowGameOver(Winner)
                    return

                # Switch to AI turn
                self.CurrentPlayer = 'b'
                self.Root.after(200, self.PerformAIMove)
            else:
                # Reset hightlights if clicking on an invalid location
                self.SelectedOrigin = None
                self.UpdateHighlights()



    def PerformAIMove(self):
        """Execute the AI's turn using the selected search algorithm.
        
        Runs the search algorithm to find the best move for black,
        applies the move, handles multi-jump captures, and checks for game over.
        """
        if self.Game is None or self.CurrentPlayer != 'b':
            return

        Depth = self.Depth
        TimeLimit = self.TimeLimit

        # Run AI search algorithm
        StartTime = time.time()
        Result = self.Search.SelectedAlgorithm(self.Game.CopyBoard(), Depth, TimeLimit)
        Elapsed = time.time() - StartTime

        if Result is None or Result[1] is None or Result[2] is None:
            Winner = self.Game.IsGameOver('b')
            if Winner:
                self.ShowGameOver(Winner)
            else:
                if self.Search.SelectedAlgorithmFunction == self.Search.Minimax:
                    TimeComplexity = "O(b^d)"
                elif self.Search.SelectedAlgorithmFunction == self.Search.AlphaBetaPruning:
                    TimeComplexity = "O(b^{d/2}) – O(b^d)"
                else:
                    TimeComplexity = "O(b log(b) · b^{d/2})"
                    
                Stats = (
                    f"Winner: White\n\n"
                    f"States Visited: {self.Search.StateVisitedCount}\n"
                    f"Time Complexity: {TimeComplexity}\n"
                    f"Space Complexity: O(d)\n"
                    f"b = branching factor, d = search depth\n\n"
                    f"Branches Pruned: {self.Search.PrunedBranchCount}\n"
                    f"Ordered Moves: {self.Search.OrderedMoveCount}"
                )
                messagebox.showinfo("Game Over", Stats)
                self.Game = None
            return

        _, Origin, Move = Result
        WasCapture = abs(Move[0] - Origin[0]) == 2
        self.Game.ApplyMove(Origin, Move)
        self.DrawBoard()
        self.DrawPieces()

        # Check for chained captures (multi-jump)
        MovesDict, CanCapture = self.Game.GetValidMoves('b')
        if WasCapture and CanCapture and Move in MovesDict:
            # Continue capturing automatically
            ChainResult = self.Search.SelectedAlgorithm(self.Game.CopyBoard(), Depth, TimeLimit)
            if ChainResult and ChainResult[1] and ChainResult[2]:
                self.Game.ApplyMove(ChainResult[1], ChainResult[2])
                self.DrawBoard()
                self.DrawPieces()

        # Check if game ended
        Winner = self.Game.IsGameOver('b')
        if Winner:
            self.ShowGameOver(Winner)
            return

        # Back to human
        self.CurrentPlayer = 'w'
        self.UpdateHighlights()


    def ShowGameOver(self, Winner):
        """Display game over dialog with winner and algorithm statistics.
        
        Args:
            Winner: The winning player color name ('white' or 'black').
            
        Shows a message box with the winner, states visited, time/space complexity,
        branches pruned, and ordered moves count.
        """
        if self.Search.SelectedAlgorithmFunction == self.Search.Minimax:
            TimeComplexity = "O(b^d)"
        elif self.Search.SelectedAlgorithmFunction == self.Search.AlphaBetaPruning:
            TimeComplexity = "O(b^{d/2}) – O(b^d)"
        else:
            TimeComplexity = "O(b log(b) · b^{d/2})"
            
        Stats = (
            f"Winner: {Winner}\n\n"
            f"States Visited: {self.Search.StateVisitedCount}\n"
            f"Time Complexity: {TimeComplexity}\n"
            f"Space Complexity: O(d)\n"
            f"b = branching factor, d = search depth\n\n"
            f"Branches Pruned: {self.Search.PrunedBranchCount}\n"
            f"Ordered Moves: {self.Search.OrderedMoveCount}"
        )
        messagebox.showinfo("Game Over", Stats)
        self.Game = None



