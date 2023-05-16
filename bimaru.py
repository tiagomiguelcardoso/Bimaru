# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 41:
# 99190 Catarina Neves Santos
# 103561 Tiago Miguel Santos Cardoso

import sys
import numpy as np 

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


class Board:
    """Representação interna de um tabuleiro de Bimaru."""
    
    def __init__(self, positions, rows, columns):
        self.positions = positions
        self.rows = rows
        self.columns = columns
        self.complete_rows = set()
        self.complete_cols = set()

    def calculate_state(self):
        self.possible_values = ()
        self.possible_positions = [(col, row) for col in range(10) for row in range(10) 
                                if self.positions[row, col] == None]

        if self.completed_board():
            return self

        '''Coloca água nas posições livres-'''
        for row, col in self.possible_positions:
            if self.get_value(row, col) is None :
                if self.check_if_possible_water(row, col):
                    possible_positions.remove((row, col))

        '''Ver se é uma posição de interesse, percorre e ve se tem alguma ao lado'''

        for row, col in self.possible_positions:
            i = 0

        return self


    '''Falta adicionar água se o valor for diferente'''
    def completed_cols(self, col: int):
        count = 0
        for i in range(10):
            if self.get_value(i,col) != "W" and self.get_value(i,col) != None:
                count = count + 1
        
        if count == self.columns[col]:
            return True
        else:
            return False
        
    def completed_rows(self, row: int):
        count = 0
        for i in range(10):
            if self.get_value(row,i) != "W" and self.get_value(row,i) != None:
                count = count + 1
        
        if count == self.rows[row]:
            return True
        else:
            return False

    def completed_board(self):
        for i in range(10):
            if self.completed_rows(i):
                self.complete_rows.add(i)
            if self.completed_cols(i):
                self.complete_cols.add(i)

        if len(self.complete_cols) == 10 and len(self.complete_rows) == 10:
            return True
        else:
            return False

    def check_if_possible_water(self, row, col):
        #Inserts water if possible
        #Tipo se existir um valor ao lado direito que nao é Left e assim
        return

    def position_is_empty(self, row, col):
        return self.positions[row, col] == None

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        if 0 <= row < 10 and 0 <= col < 10:
            return self.positions[row][col]

    def set_value(self, row, col, value):
        self.positions[row][col] = value

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        return (self.get_value(row - 1, col), self.get_value(row + 1, col))

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        return (self.get_value(row, col - 1), self.get_value(row, col + 1))

    def get_position_possibilities(self, row: int , col: int):
        return self.possible_values[row][col]

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 bimaru.py < input_T01

            > from sys import stdin
            > line = stdin.readline().split()
        """


        positions = np.full((10, 10), None)

        line = sys.stdin.readline().strip("\n")
        rows = tuple(map(int, line.split("\t")[1:]))
        line = sys.stdin.readline().strip("\n")
        columns =  tuple(map(int, line.split("\t")[1:]))

        num_hints = int(sys.stdin.readline().strip("\n"))

        for i in range(num_hints):
            line = sys.stdin.readline().strip("\n")
            hint = line.split()
            row = int(hint[1])
            col = int(hint[2])
            value = hint[3]
            positions[row][col] = value
        
        return Board(positions, rows, columns).calculate_state()

    # TODO: outros metodos da classe


class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        state = TakuzuState(board)
        super().__init__(state)
        pass

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # TODO

        possibilities = []
        for row in range(10):
            for column in range(10):
                position_actions = state.board.get_position_possibilities(row, col)
                possibilities.extend(position_actions)
        return possibilities

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        (row, col, value) = action
        return BimaruState(state.board.set_value(row, col, value))

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        # TODO
        pass

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:
    board = Board.parse_instance()
    print(board.complete_rows)    
    print(board.complete_cols)
    print(board.adjacent_vertical_values(3, 3))
    print(board.adjacent_horizontal_values(3, 3))
    print(board.adjacent_vertical_values(1, 0))
    print(board.adjacent_horizontal_values(1, 0))
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    pass