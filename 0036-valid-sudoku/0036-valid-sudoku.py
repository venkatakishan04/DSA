class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        def issafe(i,j):
            a=board[i][j]
            for k in range(9):
                if(k!=i and a==board[k][j]):
                    return False
                if(k!=j and a==board[i][k]):
                    return False
                if(board[3*(i//3)+k//3][3*(j//3)+k%3]==a and 3*(i//3)+k//3!=i and 3*(j//3)+k%3!=j):
                    return False
            return True
        for i in range(len(board)):
            for j in range(len(board[0])):
                if(board[i][j]!="."):
                    if(issafe(i,j)==False):
                        return False
        return True
        