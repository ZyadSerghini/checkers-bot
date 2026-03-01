import copy

PossibleDirections = {'w': [(-1, -1), (-1, 1)], 
                       'b': [(1, -1), (1, 1)], 
                       'W': [(-1, -1), (-1, 1), (1, -1), (1, 1)], 
                       'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)]}

InitialBoard = [
['.', 'b', '.', 'b', '.', 'b', '.', 'b'],
['b', '.', 'b', '.', 'b', '.', 'b', '.'],
['.', 'b', '.', 'b', '.', 'b', '.', 'b'],
['.', '.', '.', '.', '.', '.', '.', '.'],
['.', '.', '.', '.', '.', '.', '.', '.'],
['w', '.', 'w', '.', 'w', '.', 'w', '.'],
['.', 'w', '.', 'w', '.', 'w', '.', 'w'],
['w', '.', 'w', '.', 'w', '.', 'w', '.']]

class GameBoard:
    """Represents an 8x8 checkers game board with piece management and move validation."""
    
    def __init__(self):
        """Initialize the game board with the standard checkers starting position."""
        self.BoardGrid = InitialBoard.copy()
    
    def __getitem__(self, RowIndex):
        """Enable indexed access to board rows using square bracket notation.
        
        Args:
            RowIndex: The row index to access (0-7).
            
        Returns:
            The list representing the specified row.
        """
        return self.BoardGrid[RowIndex]
    def __setitem__(self, IndexPair, NewValue):
        """Enable setting board cell values using square bracket notation.
        
        Args:
            IndexPair: A tuple of (RowIndex, ColIndex) coordinates.
            NewValue: The piece code to place at the specified position.
        """
        assert type(IndexPair) is tuple and len(IndexPair) == 2, "Two coordinates must be inputted."
        RowIndex, ColIndex  = IndexPair
        self.BoardGrid[RowIndex][ColIndex] = NewValue
    def __str__(self):
        """Convert the board to a human-readable string representation.
        
        Returns:
            A multi-line string showing the board state.
        """
        BoardString = ''
        for RowLine in self:
            BoardString += str(RowLine) + '\n'
        return BoardString
    def __len__(self):
        """Return the number of rows on the board.
        
        Returns:
            The board height (always 8 for standard checkers).
        """
        return len(self.BoardGrid)
    def IsInsideBoard(self, RowIndex, ColIndex):
        """Checks if a position is within board limits."""
        return 0 <= RowIndex < 8 and 0 <= ColIndex < 8

    def IsEnemyPiece(self, PieceCode, CurrentPlayer):
        """Checks if piece belongs to the opponent."""
        if PieceCode == '.':
            return False
        if CurrentPlayer == 'w':
            return PieceCode in ['b', 'B']
        else:
            return PieceCode in ['w', 'W']
    def IsPlayerPiece(self, PieceCode, CurrentPlayer):
        """Checks if piece belongs to the current player."""
        if CurrentPlayer == 'w':
            return PieceCode in ['w', 'W']
        else:
            return PieceCode in ['b', 'B']

    def GetPieceMoves(self, RowIndex, ColIndex, PieceCode):
        """Calculate all possible moves for a specific piece.
        
        Args:
            RowIndex: The row position of the piece.
            ColIndex: The column position of the piece.
            PieceCode: The piece type ('w', 'b', 'W', 'B').
            
        Returns:
            A tuple of (NormalMoves, CaptureMoves) where each is a list of coordinate tuples.
        """
        MoveDirections = PossibleDirections[PieceCode]
        
        NormalMoves = []
        CaptureMoves = []
        PieceCode = PieceCode.lower()
        
        for DeltaRow, DeltaCol in MoveDirections:
            NextRow, NextCol = RowIndex + DeltaRow, ColIndex + DeltaCol  # immediate diagonal square
            JumpRow, JumpCol = RowIndex + 2 * DeltaRow, ColIndex + 2 * DeltaCol

            if self.IsInsideBoard(NextRow, NextCol) and self.BoardGrid[NextRow][NextCol] == '.':
                NormalMoves.append((NextRow, NextCol))   
            
            elif (
                self.IsInsideBoard(JumpRow, JumpCol)
                and self.IsEnemyPiece(self.BoardGrid[NextRow][NextCol], PieceCode)
                and self.BoardGrid[JumpRow][JumpCol] == '.'
            ):
                CaptureMoves.append((JumpRow, JumpCol))
        
        return NormalMoves, CaptureMoves
    
    def GetValidMoves(self, CurrentPlayer):
        """Get all legal moves for the current player, enforcing mandatory capture rule.
        
        Args:
            CurrentPlayer: The player code ('w' or 'b').
            
        Returns:
            A tuple of (MoveDict, CaptureFlag) where MoveDict maps origin coordinates 
            to lists of destination coordinates, and CaptureFlag indicates if captures are available.
        """
        MoveDict = {}
        MustCaptureMoves = {}

        for RowIndex in range(8):
            for ColIndex in range(8):
                PieceCode = self.BoardGrid[RowIndex][ColIndex]
                if self.IsPlayerPiece(PieceCode, CurrentPlayer):
                    PieceMoves, PieceCaptures = self.GetPieceMoves(RowIndex, ColIndex, PieceCode)

                    if PieceCaptures:
                        MustCaptureMoves[(RowIndex, ColIndex)] = PieceCaptures
                    elif PieceMoves:
                        MoveDict[(RowIndex, ColIndex)] = PieceMoves

        if MustCaptureMoves:
            return MustCaptureMoves, True
        else:
            return MoveDict, False

    def CopyBoard(self):
        """Create a deep copy of the current board state.
        
        Returns:
            A new GameBoard instance with an independent copy of the board grid.
        """
        NewBoard = GameBoard()
        NewBoard.BoardGrid = copy.deepcopy(self.BoardGrid)
        return NewBoard
    
    def ApplyMove(self, OriginPos, DestPos):
        """Execute a move on the board, handling captures and king promotions.
        
        Args:
            OriginPos: The starting coordinate tuple (row, col).
            DestPos: The destination coordinate tuple (row, col).
            
        Returns:
            A boolean indicating whether a capture occurred.
        """
        FromRow, FromCol = OriginPos
        ToRow, ToCol = DestPos
        EatAction = False
        
        PieceCode = self.BoardGrid[FromRow][FromCol]
        
        # Move the piece
        self.BoardGrid[ToRow][ToCol] = PieceCode
        self.BoardGrid[FromRow][FromCol] = '.'
                
        # Check for capture
        if abs(ToRow - FromRow) == 2:
            MidRow = (FromRow + ToRow) // 2
            MidCol = (FromCol + ToCol) // 2
            self.BoardGrid[MidRow][MidCol] = '.'
            EatAction = True
        # Check for king promotion
        if PieceCode == 'w' and ToRow == 0:
            self.BoardGrid[ToRow][ToCol] = 'W'
        elif PieceCode == 'b' and ToRow == 7:
            self.BoardGrid[ToRow][ToCol] = 'B'
        
        return EatAction
    
    def PieceInBoard(self, PieceCode):
        """Check if at least one piece of the specified type exists on the board.
        
        Args:
            PieceCode: The piece type to search for ('w', 'b', 'W', 'B').
            
        Returns:
            True if the piece type is found, False otherwise.
        """
        for RowLine in self:
            for CellValue in RowLine:
                if CellValue == PieceCode:
                    return True
        return False
    
    def IsGameOver(self, CurrentPlayer = 'b'):
        """Determine if the game has ended and identify the winner.
        
        Args:
            CurrentPlayer: The player code ('w' or 'b') whose turn it is.
            
        Returns:
            The winner color name ('white' or 'black') if game is over, None otherwise.
        """
        if not self.PieceInBoard('w'):
            return 'black'
        if not self.PieceInBoard('b'):
            return 'white'
        
        if not self.GetValidMoves(CurrentPlayer):
            return 'black' if CurrentPlayer == 'w' else 'white'
    
    def CountPiece(self, PieceCode):
        """Count pieces of a given color, distinguishing regular pieces, kings, and center control.
        
        Args:
            PieceCode: The color code ('w' or 'b') to count.
            
        Returns:
            A tuple of (PieceCount, KingCount, CenterCount) representing regular pieces,
            kings, and pieces in the center 4x4 area respectively.
        """
        PieceCount = 0
        KingCount = 0
        CenterCount = 0
        for RowIndex in range(len(self)):
            for ColIndex in range(len(self[RowIndex])):
                CellValue = self[RowIndex][ColIndex]
                if CellValue.lower() == PieceCode:
                    if CellValue in ['W', 'B']:
                        KingCount += 1
                    else:
                        PieceCount += 1
                    if 2 <= RowIndex <= 5 and 2 <= ColIndex <= 5:
                        CenterCount += 1
        return PieceCount, KingCount, CenterCount
        
        
        
            
            