import time

# ----- Heuristic Factors -----
WeightPieceValue = 10
WeightKingValue = 15
WeightMovesValue = 2
WeightCenterValue = 1

class SearchToolBox:
    """Provides adversarial search algorithms for checkers AI decision making."""
    
    def __init__(self, AlgorithmIndexValue):
        """Initialize the search toolbox with a specific algorithm.
        
        Args:
            AlgorithmIndexValue: Index of the algorithm to use (0=Minimax, 1=AlphaBeta, 2=NodeOrdering).
        """
        AlgorithmFunctionList = [self.Minimax, self.AlphaBetaPruning, self.NodeOrdering]
        self.SelectedAlgorithmFunction = AlgorithmFunctionList[AlgorithmIndexValue]
        
        self.StateVisitedCount = 0
        self.PrunedBranchCount = 0
        self.OrderedMoveCount = 0  
    
    def SelectedAlgorithm(self, BoardStateObject, SearchDepthValue, TimeLimitSeconds):
        """Execute the selected search algorithm on the given board state.
        
        Args:
            BoardStateObject: The current GameBoard instance.
            SearchDepthValue: Maximum search depth (number of plies).
            TimeLimitSeconds: Time limit in seconds for the search.
            
        Returns:
            A tuple of (EvalScore, BestOrigin, BestMove) representing the evaluation score
            and the best move coordinates.
        """
        return self.SelectedAlgorithmFunction(BoardStateObject, SearchDepthValue, TimeLimitSeconds)      
    
    def HeuristicEval(self, BoardStateObject):
        """Evaluate the board state using a weighted heuristic function.
        
        Args:
            BoardStateObject: The GameBoard instance to evaluate.
            
        Returns:
            A numeric score (positive favors black, negative favors white).
        """
        WhitePieceCount, WhiteKingCount, WhiteCenterCount = BoardStateObject.CountPiece('w')
        WhiteMoveCount = len(BoardStateObject.GetValidMoves('w')[0])
        BlackPieceCount, BlackKingCount, BlackCenterCount = BoardStateObject.CountPiece('b')
        BlackMoveCount = len(BoardStateObject.GetValidMoves('b')[0])
        
        return WeightPieceValue * (BlackPieceCount - WhitePieceCount) + WeightKingValue * (BlackKingCount - WhiteKingCount) + WeightMovesValue * (BlackMoveCount - WhiteMoveCount) + WeightCenterValue * (BlackCenterCount - WhiteCenterCount)



    def Minimax(self, BoardStateObject, SearchDepthValue=5, TimeLimitSeconds=3, StartTimeStamp=None, MaximizingPlayerFlag=True):
        """Perform Minimax search to find the optimal move.
        
        Args:
            BoardStateObject: The current GameBoard state.
            SearchDepthValue: Maximum depth to search (default 5).
            TimeLimitSeconds: Time limit in seconds (default 3).
            StartTimeStamp: Start time for tracking elapsed time (default None).
            MaximizingPlayerFlag: True if maximizing (black), False if minimizing (white).
            
        Returns:
            A tuple of (EvalScore, BestOrigin, BestMove).
        """
        if StartTimeStamp is None:
            StartTimeStamp = time.time()
        
        if time.time() - StartTimeStamp >= TimeLimitSeconds:
            return self.HeuristicEval(BoardStateObject), None, None

        if SearchDepthValue == 0 or BoardStateObject.IsGameOver():
            return self.HeuristicEval(BoardStateObject), None, None

        PlayerCodeValue = 'b' if MaximizingPlayerFlag else 'w'
        ValidMovesDict = BoardStateObject.GetValidMoves(PlayerCodeValue)[0]

        if not ValidMovesDict:
            return self.HeuristicEval(BoardStateObject), None, None

        if MaximizingPlayerFlag:
            MaxEvalScore = -float('inf')
            BestMoveCoord = None
            BestOriginCoord = None

            for OriginCoord, MoveList in ValidMovesDict.items():
                for MoveCoord in MoveList:
                    if time.time() - StartTimeStamp >= TimeLimitSeconds:
                        return MaxEvalScore, BestOriginCoord, BestMoveCoord

                    NextBoardState = BoardStateObject.CopyBoard()
                    NextBoardState.ApplyMove(OriginCoord, MoveCoord)
                    self.StateVisitedCount += 1
                    EvalScore, _, _ = self.Minimax(NextBoardState, SearchDepthValue-1, TimeLimitSeconds, StartTimeStamp, False)
                    if EvalScore > MaxEvalScore:
                        MaxEvalScore = EvalScore
                        BestMoveCoord = MoveCoord
                        BestOriginCoord = OriginCoord
            return MaxEvalScore, BestOriginCoord, BestMoveCoord

        else:
            MinEvalScore = float('inf')
            BestMoveCoord = None
            BestOriginCoord = None

            for OriginCoord, MoveList in ValidMovesDict.items():
                for MoveCoord in MoveList:
                    if time.time() - StartTimeStamp >= TimeLimitSeconds:
                        return MinEvalScore, BestOriginCoord, BestMoveCoord

                    NextBoardState = BoardStateObject.CopyBoard()
                    NextBoardState.ApplyMove(OriginCoord, MoveCoord)
                    self.StateVisitedCount += 1
                    EvalScore, _, _ = self.Minimax(NextBoardState, SearchDepthValue-1, TimeLimitSeconds, StartTimeStamp, True)
                    if EvalScore < MinEvalScore:
                        MinEvalScore = EvalScore
                        BestMoveCoord = MoveCoord
                        BestOriginCoord = OriginCoord
            return MinEvalScore, BestOriginCoord, BestMoveCoord


    def AlphaBetaPruning(self, BoardStateObject, SearchDepthValue=9, TimeLimitSeconds=3, StartTimeStamp=None, AlphaBoundValue=-float('inf'), BetaBoundValue=float('inf'), MaximizingPlayerFlag=True):
        """Perform Alpha-Beta pruning search for improved efficiency.
        
        Args:
            BoardStateObject: The current GameBoard state.
            SearchDepthValue: Maximum depth to search (default 9).
            TimeLimitSeconds: Time limit in seconds (default 3).
            StartTimeStamp: Start time for tracking elapsed time (default None).
            AlphaBoundValue: Alpha value for pruning (default -infinity).
            BetaBoundValue: Beta value for pruning (default infinity).
            MaximizingPlayerFlag: True if maximizing (black), False if minimizing (white).
            
        Returns:
            A tuple of (EvalScore, BestOrigin, BestMove).
        """
        if StartTimeStamp is None:
            StartTimeStamp = time.time()
        
        if time.time() - StartTimeStamp >= TimeLimitSeconds:
            return self.HeuristicEval(BoardStateObject), None, None

        if SearchDepthValue == 0 or BoardStateObject.IsGameOver():
            return self.HeuristicEval(BoardStateObject), None, None

        PlayerCodeValue = 'b' if MaximizingPlayerFlag else 'w'
        ValidMovesDict = BoardStateObject.GetValidMoves(PlayerCodeValue)[0]

        if not ValidMovesDict:
            return self.HeuristicEval(BoardStateObject), None, None

        StopLoopFlag = False

        if MaximizingPlayerFlag:
            MaxEvalScore = -float('inf')
            BestMoveCoord = None
            BestOriginCoord = None

            for OriginCoord, MoveList in ValidMovesDict.items():
                for MoveCoord in MoveList:
                    if time.time() - StartTimeStamp >= TimeLimitSeconds:
                        return MaxEvalScore, BestOriginCoord, BestMoveCoord

                    NextBoardState = BoardStateObject.CopyBoard()
                    NextBoardState.ApplyMove(OriginCoord, MoveCoord)
                    self.StateVisitedCount += 1
                    EvalScore, _, _ = self.AlphaBetaPruning(NextBoardState, SearchDepthValue-1, TimeLimitSeconds, StartTimeStamp, AlphaBoundValue, BetaBoundValue, False)
                    if EvalScore > MaxEvalScore:
                        MaxEvalScore = EvalScore
                        BestMoveCoord = MoveCoord
                        BestOriginCoord = OriginCoord
                    AlphaBoundValue = max(AlphaBoundValue, EvalScore)
                    if BetaBoundValue <= AlphaBoundValue:
                        self.PrunedBranchCount += 1
                        StopLoopFlag = True
                        break
                if StopLoopFlag:
                    break
            return MaxEvalScore, BestOriginCoord, BestMoveCoord

        else:
            MinEvalScore = float('inf')
            BestMoveCoord = None
            BestOriginCoord = None

            for OriginCoord, MoveList in ValidMovesDict.items():
                for MoveCoord in MoveList:
                    if time.time() - StartTimeStamp >= TimeLimitSeconds:
                        return MinEvalScore, BestOriginCoord, BestMoveCoord

                    NextBoardState = BoardStateObject.CopyBoard()
                    NextBoardState.ApplyMove(OriginCoord, MoveCoord)
                    self.StateVisitedCount += 1
                    EvalScore, _, _ = self.AlphaBetaPruning(NextBoardState, SearchDepthValue-1, TimeLimitSeconds, StartTimeStamp, AlphaBoundValue, BetaBoundValue, True)
                    if EvalScore < MinEvalScore:
                        MinEvalScore = EvalScore
                        BestMoveCoord = MoveCoord
                        BestOriginCoord = OriginCoord
                    BetaBoundValue = min(AlphaBoundValue, EvalScore)
                    if BetaBoundValue <= AlphaBoundValue:
                        self.PrunedBranchCount += 1
                        StopLoopFlag = True
                        break
                if StopLoopFlag:
                    break
            return MinEvalScore, BestOriginCoord, BestMoveCoord


    def NodeOrdering(self, BoardStateObject, SearchDepthValue=9, TimeLimitSeconds=3, StartTimeStamp=None, AlphaBoundValue=-float('inf'), BetaBoundValue=float('inf'), MaximizingPlayerFlag=True):
        """Perform Alpha-Beta pruning with move ordering for optimal pruning.
        
        Args:
            BoardStateObject: The current GameBoard state.
            SearchDepthValue: Maximum depth to search (default 9).
            TimeLimitSeconds: Time limit in seconds (default 3).
            StartTimeStamp: Start time for tracking elapsed time (default None).
            AlphaBoundValue: Alpha value for pruning (default -infinity).
            BetaBoundValue: Beta value for pruning (default infinity).
            MaximizingPlayerFlag: True if maximizing (black), False if minimizing (white).
            
        Returns:
            A tuple of (EvalScore, BestOrigin, BestMove).
        """
        if StartTimeStamp is None:
            StartTimeStamp = time.time()
        
        if time.time() - StartTimeStamp >= TimeLimitSeconds:
            return self.HeuristicEval(BoardStateObject), None, None

        if SearchDepthValue == 0 or BoardStateObject.IsGameOver():
            return self.HeuristicEval(BoardStateObject), None, None

        PlayerCodeValue = 'b' if MaximizingPlayerFlag else 'w'
        ValidMovesDict = BoardStateObject.GetValidMoves(PlayerCodeValue)[0]

        if not ValidMovesDict:
            return self.HeuristicEval(BoardStateObject), None, None

        OrderedMoveList = []
        for OriginCoord, MoveList in ValidMovesDict.items():
            for MoveCoord in MoveList:
                if time.time() - StartTimeStamp >= TimeLimitSeconds:
                    break
                NextBoardState = BoardStateObject.CopyBoard()
                self.StateVisitedCount += 1
                HeuristicScoreValue = self.HeuristicEval(NextBoardState)
                OrderedMoveList.append((OriginCoord, MoveCoord, HeuristicScoreValue))
                self.OrderedMoveCount += 1

        OrderedMoveList.sort(key=lambda x: x[1], reverse=MaximizingPlayerFlag)

        if MaximizingPlayerFlag:
            MaxEvalScore = -float('inf')
            BestMoveCoord = None
            BestOriginCoord = None

            for OriginCoord, MoveCoord, _ in OrderedMoveList:
                if time.time() - StartTimeStamp >= TimeLimitSeconds:
                    return MaxEvalScore, BestOriginCoord, BestMoveCoord

                NextBoardState = BoardStateObject.CopyBoard()
                NextBoardState.ApplyMove(OriginCoord, MoveCoord)
                self.StateVisitedCount += 1
                EvalScore, _, _ = self.AlphaBetaPruning(NextBoardState, SearchDepthValue-1, TimeLimitSeconds, StartTimeStamp, AlphaBoundValue, BetaBoundValue, False)
                if EvalScore > MaxEvalScore:
                    MaxEvalScore = EvalScore
                    BestMoveCoord = MoveCoord
                    BestOriginCoord = OriginCoord
                AlphaBoundValue = max(AlphaBoundValue, EvalScore)
                if BetaBoundValue <= AlphaBoundValue:
                    self.PrunedBranchCount += 1
                    break
            return MaxEvalScore, BestOriginCoord, BestMoveCoord

        else:
            MinEvalScore = float('inf')
            BestMoveCoord = None
            BestOriginCoord = None

            for OriginCoord, MoveCoord, _ in OrderedMoveList:
                if time.time() - StartTimeStamp >= TimeLimitSeconds:
                    return MinEvalScore, BestOriginCoord, BestMoveCoord

                NextBoardState = BoardStateObject.CopyBoard()
                NextBoardState.ApplyMove(OriginCoord, MoveCoord)
                self.StateVisitedCount += 1
                EvalScore, _, _ = self.AlphaBetaPruning(NextBoardState, SearchDepthValue-1, TimeLimitSeconds, StartTimeStamp, AlphaBoundValue, BetaBoundValue, True)
                if EvalScore < MinEvalScore:
                    MinEvalScore = EvalScore
                    BestMoveCoord = MoveCoord
                    BestOriginCoord = OriginCoord
                BetaBoundValue = min(AlphaBoundValue, EvalScore)
                if BetaBoundValue <= AlphaBoundValue:
                    self.PrunedBranchCount += 1
                    break
            return MinEvalScore, BestOriginCoord, BestMoveCoord
