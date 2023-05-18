# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 41:
# 99190 Catarina Neves Santos
# 103561 Tiago Miguel Santos Cardoso

import sys
import numpy as np 
import time

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
        self.rows_data =[{"Parts": 0, "Nones": 0, "Water": 0} for _ in range(10)]
        self.cols_data =[{"Parts": 0, "Nones": 0, "Water": 0} for _ in range(10)]
        self.complete_rows = set()
        self.complete_cols = set()
        self.possible_positions = []
        self.boat_coordinates = []
        
        self.ships = {'Current': {'Couraçado': 0, 'Cruzadores': 0, 'Contratorpedeiros': 0, 'Submarino': 4}
                        , 'Max': {'Couraçado': 1, 'Cruzadores': 2, 'Contratorpedeiros': 3, 'Submarino': 4}}
        self.parts = {'Current': {"C": 0, "T": 0, "L": 0, "B": 0 ,"R": 0, "M":0}
                        , 'Max': {"C": 0, "T": 0, "L": 0, "B": 0 ,"R": 0, "M":0}}

    def calculate_state(self):
        self.possible_values = [[[] for _ in range(10)] for _ in range(10)]
        
        if self.completed_board():
            return self

        self.possible_positions = [(row, col) for row in range(10) for col in range(10) 
            if self.positions[row, col] == None]


        '''Coloca água nas posições livres-'''
        for row, col in self.possible_positions[:]:
            if self.get_value(row, col) is None :
                if self.check_if_water(row, col):
                    self.possible_positions.remove((row, col))

        '''Ver se é uma posição de interesse, percorre e ve se tem alguma ao lado'''

        '''
        // Codigo de Teste
        for row, col in self.possible_positions:
            print("Row: ", row, col)
            self.possible_values[row][col].extend(["C", "T", "B", "L", "R", "M", "W"])
            print(self.possible_values[row][col])

        '''

        for row in range(10):
            for col in range(10):
                if (row, col) in self.boat_coordinates:
                    break
                val = self.get_value(row, col)
                size = self.get_board_level()
                action = self.maybe_boat_check(row, col, val ,size)
                if type(action) == list:
                    self.possible_values[row][col].append(action)

        return self

    def completed_cols(self, col: int):
        parts = 0
        empty = set()
        for i in range(10):
            value = self.get_value(i,col)
            
            if  value != "W" and value != None:
                parts = parts + 1

            if value == None:
                empty.add(i)
        
        if parts == self.columns[col]:
            for i in empty:
                if self.get_value(i,col) == None:
                    self.set_value(i,col,"W")
            self.cols_data[col]["Parts"] = parts
            self.cols_data[col]["Water"] = 10 - parts
            return True
        else:
            self.cols_data[col]["Parts"] = parts
            self.cols_data[col]["None"] = len(empty)
            self.cols_data[col]["Water"] = 10 - parts - len(empty)
            return False


        self.rows[rows] = 2
        empty = 4
        parts = 1

    def completed_rows(self, row: int):
        parts = 0
        empty = set()
        for i in range(10):
            value = self.get_value(row,i)
            
            if  value != "W" and value != None:
                parts = parts + 1

            if value == None:
                empty.add(i)

        
        if parts == self.rows[row]:
            for i in empty:
                if self.get_value(row,i) == None:
                    self.set_value(row,i,"W")
            self.rows_data[row]["Parts"] = parts
            self.rows_data[row]["Water"] = 10 - parts
            return True
        else:
            self.rows_data[row]["Parts"] = parts
            self.rows_data[row]["None"] = len(empty)
            self.rows_data[row]["Water"] = 10 - parts - len(empty)
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

    def check_if_water(self, row, col):
        #Inserts water if possible
        #Tipo se existir um valor ao lado direito que nao é Left e assim
        p = self.adjacent_values(row, col)
        if any(self.is_boat(p[i]) for i in [0, 2, 5, 7]):
            self.set_value(row, col, "W")
            return True

        elif p[1] in ("C", "B", "L", "R"):
            self.set_value(row, col, "W")
            return True
        elif p[3] in ("C", "R", "T", "B"):
            self.set_value(row, col, "W")
            return True
        elif p[4] in ("C", "L", "T", "B"):
            self.set_value(row, col, "W")
            return True
        elif p[6] in ("C", "T", "L", "R"):
            self.set_value(row, col, "W")
            return True
        else:
            return False

    def position_is_empty(self, row, col):
        return self.positions[row, col] == None

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        if 0 <= row < 10 and 0 <= col < 10:
            return self.positions[row][col]
        else:
            return None

    def print_board(self):
        for row in self.positions:
            row_str = ' '.join([str(element) if element != None else "." for element in row])
            print(row_str)

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

    def adjacent_values(self, row: int, col: int):
        adjacents = []
        if 0 <= row < 10 and 0 <= col < 10:
            adjacents.append(self.get_value(row-1,col-1))
            adjacents.append(self.get_value(row-1,col))
            adjacents.append(self.get_value(row-1,col+1))
            adjacents.append(self.get_value(row,col-1))
            adjacents.append(self.get_value(row,col+1))
            adjacents.append(self.get_value(row+1,col-1))
            adjacents.append(self.get_value(row+1,col))
            adjacents.append(self.get_value(row+1,col+1))
        return adjacents

    def get_position_possibilities(self, row: int , col: int):
        return self.possible_values[row][col]

    def is_boat(self, value):
        return value in ("C", "T", "M", "B", "L", "R")

    def calculate_parts(self):
        for row in range(10):
            for col in range(10):
                val = self.get_value(row, col)
                if self.is_boat(val):
                    self.parts["Current"][val] = self.parts["Current"][val] + 1
    
    def set_position_possible_values():
        b = ["C", "T", "B", "L", "R", "M", "W"]

    def maybe_boat_check(self, row, col , val, size):
        if val == "T":
            action = [[row, col, val, size]]
            if (row + size - 1) <= 9:
                if size == 4:
                    v1 = self.get_value(row + 1, col)
                    v2 = self.get_value(row + 2, col)
                    v3 = self.get_value(row + 3, col)
                    if v1 in (None, "M") and  v2 in (None, "M") and v3 in (None, "B"):
                        if v1 == None:
                            action.append([row + 1, col, "M"])
                        if v2 == None:
                            action.append([row + 2, col, "M"])
                        if v3 == None:
                            action.append([row + 3, col, "B"])
                        if self.cant_place_boat("V", col, action):
                            return False
                        return action
                
                if size == 3:
                    v1 = self.get_value(row + 1, col)
                    v2 = self.get_value(row + 2, col)
                    if v1 in (None, "M") and  v2 in (None, "B"):
                        if v1 == None:
                            action.append([row + 1, col, "M"])
                        if v2 == None:
                            action.append([row + 2, col, "B"])
                        if self.cant_place_boat("V", col, action):                     
                            return False
                        return action

                if size == 2:
                    v1 = self.get_value(row + 1, col)
                    if v1 in (None, "B"):
                        if v1 == None:
                            action.append([row + 1, col, "B"])
                        if self.cant_place_boat("V", col, action):                            
                            return False
                        return action
            return False

        elif val == "L":
            action = [[row, col, val, size]]
            if (col + size - 1) <= 9:
                if size == 4:
                    
                    v1 = self.get_value(row, col + 1)
                    v2 = self.get_value(row, col + 2)
                    v3 = self.get_value(row, col + 3)
                    if v1 in (None, "M") and  v2 in (None, "M") and v3 in (None, "R"):
                        if v1 == None:
                            action.append([row, col + 1, "M"])
                        if v2 == None:
                            action.append([row, col + 2, "M"])
                        if v3 == None:
                            action.append([row, col + 3, "R"])
                        if self.cant_place_boat("H", row, action):                            
                            return False
                        return action
                
                if size == 3:
                    
                    v1 = self.get_value(row, col + 1)
                    v2 = self.get_value(row, col + 2)
                    if v1 in (None, "M") and  v2 in (None, "R"):
                        if v1 == None:
                            action.append([row, col + 1, "M"])
                        if v2 == None:
                            action.append([row, col + 2, "R"])
                        if self.cant_place_boat("H", row, action):                            
                            return False
                        return action

                if size == 2:
                    
                    v1 = self.get_value(row, col + 1)
                    if v1 in (None, "R"):
                        if v1 == None:
                            action.append([row, col + 1, "R"])
                        if self.cant_place_boat("H", row, action):                            
                            return False    
                        return action

            return False

        elif val == None:
            if size == 1:
                if ((self.columns[col] - self.cols_data[col]["Parts"]) < size) and ((self.rows[row] - self.rows_data[row]["Parts"]) < size):
                    action = [[row, col, "C", size], [row, col, "C"]]
                    return action
            if (row + size - 1) <= 9:
                action = [[row, col, "T", size]]
                if size == 4:
                    v1 = self.get_value(row + 1, col)
                    v2 = self.get_value(row + 2, col)
                    v3 = self.get_value(row + 3, col)
                    if v1 in (None, "M") and  v2 in (None, "M") and v3 in (None, "B"):
                        action.append([row, col, "T"])
                        if v1 == None:
                            action.append([row + 1, col, "M"])
                        if v2 == None:
                            action.append([row + 2, col, "M"])
                        if v3 == None:
                            action.append([row + 3, col, "B"])
                        if not self.cant_place_boat("V", col, action):                            
                            return action
                        
                
                if size == 3:
                    v1 = self.get_value(row + 1, col)
                    v2 = self.get_value(row + 2, col)
                    if v1 in (None, "M") and  v2 in (None, "B"):
                        action.append([row, col, "T"])
                        if v1 == None:
                            action.append([row + 1, col, "M"])
                        if v2 == None:
                            action.append([row + 2, col, "B"])
                        if not self.cant_place_boat("V", col, action):                            
                            return action
                        

                if size == 2:
                    v1 = self.get_value(row + 1, col)
                    if v1 in (None, "B"):
                        action.append([row, col, "T"])
                        if v1 == None:
                            action.append([row + 1, col, "B"])
                        if not self.cant_place_boat("V", col, action):                            
                            return action           

            if (col + size - 1) <= 9:
                action = [[row, col, "L", size]]
                if size == 4:
                    v1 = self.get_value(row, col + 1)
                    v2 = self.get_value(row, col + 2)
                    v3 = self.get_value(row, col + 3)
                    if v1 in (None, "M") and  v2 in (None, "M") and v3 in (None, "R"):
                        action.append([row, col, "L"])
                        if v1 == None:
                            action.append([row, col + 1, "M"])
                        if v2 == None:
                            action.append([row, col + 2, "M"])
                        if v3 == None:
                            action.append([row, col + 3, "R"])
                        if self.cant_place_boat("H", row, action):                            
                            return False
                        return action
                
                if size == 3:
                    
                    v1 = self.get_value(row, col + 1)
                    v2 = self.get_value(row, col + 2)
                    if v1 in (None, "M") and  v2 in (None, "R"):
                        action.append([row, col, "L"])
                        if v1 == None:
                            action.append([row, col + 1, "M"])
                        if v2 == None:
                            action.append([row, col + 2, "R"])
                        if self.cant_place_boat("H", row, action):
                                                    
                            return False
                        return action

                if size == 2:
                    v1 = self.get_value(row, col + 1)
                    if v1 in (None, "R"):
                        action.append([row, col, "L"])
                        if v1 == None:
                            action.append([row, col + 1, "R"])
                        if self.cant_place_boat("H", row, action):
                            return False
                        return action
            return False

        #elif val == "C":
            #self.add_boat_coordinates(row, col, 1)
            #return False
    
    def get_board_level(self):
        if self.ships["Current"]["Couraçado"] < self.ships["Max"]["Couraçado"]:
            return 4
        
        elif self.ships["Current"]["Cruzadores"] < self.ships["Max"]["Cruzadores"]:
            return 3

        elif self.ships["Current"]["Contratorpedeiros"] < self.ships["Max"]["Contratorpedeiros"]:
            return 2
        elif self.ships["Current"]["Submarino"] < self.ships["Max"]["Submarino"]:
            return 1
        else:
            return 0
    
    def add_boat_coordinates(self, row, col, size):
        if size == 4:
            self.ships['Current']['Couraçado'] = 1
        elif size == 3:
            self.ships['Current']['Cruzadores'] = self.ships['Current']['Cruzadores'] + 1
        elif size == 2:
            self.ships['Current']['Contratorpedeiros'] = self.ships['Current']['Contratorpedeiros'] + 1
        elif size == 1:
            self.ships['Current']['Submarino'] = self.ships['Current']['Submarino'] + 1
            
        self.boat_coordinates.append([row, col])

    def can_place_water_around(self, row, col, value, size):
        positions = []
        
        # Verifica se o barco está na posição "T" (para baixo)
        if value == "T":
            for i in range(row - 1, row + size):
                positions.append((i, col-1))
                positions.append((i, col+1))
            positions.extend([(row-1, col), (row+size, col)])
                
        # Verifica se o barco está na posição "L" (lado)
        elif value == "L":
            for j in range(col - 1, col + size):
                positions.append((row-1, j))
                positions.append((row+1, j))
            positions.extend([(row, col-1), (row, col+size)])
    
        # Verifica se as posições ao redor do barco são "W" ou None
        valid = all(self.get_value(row, col) in [None, "W"] for (row, col) in positions)
        return valid

    def cant_place_boat(self, tipo, place, action):
        if tipo == "V":
            try:
                if any(r[0] in self.complete_rows for r in (action[1:])) or ((self.columns[place] - self.cols_data[place]["Parts"]) < (len(action)-1)):
                    return True
                else:
                    return False
            except:
                return False
        elif tipo == "H":
            try:
                if any(r[1] in self.complete_cols for r in (action[1:])) or ((self.rows[place] - self.rows_data[place]["Parts"]) < (len(action)-1)):
                    return True
                else:
                    return False
            except:
                return False



    def copy_board(self, board):
        new_board = Board([], [], [])
        new_board.positions = np.copy(board.positions)
        new_board.rows = np.copy(board.rows)
        new_board.columns = np.copy(board.columns)
        new_board.boat_coordinates = np.copy(board.boat_coordinates).tolist()
        new_board.ships = self.deep_copy_dict(board.ships)
        return new_board

    def deep_copy_dict(self, original_dict):
        copied_dict = {}
        for key, value in original_dict.items():
            if isinstance(value, dict):
                copied_dict[key] = self.deep_copy_dict(value)
            else:
                copied_dict[key] = value
        return copied_dict

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
        state = BimaruState(board)
        super().__init__(state)
        pass

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        print("-----------------------")
        print("Actions")
        print("Level: ", state.board.get_board_level())
        print("Barcos: ", state.board.ships)
        state.board.print_board()
        possibilities = []
        for row in range(10):
            for col in range(10):
                position_actions = state.board.get_position_possibilities(row, col)
                possibilities.extend(position_actions)
        [print(p) for p in possibilities]
        print("-----------------------")
        return possibilities

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        print("-----------------------")
        print("Result")

        new_board = state.board.copy_board(state.board)
        
        for part in action[1:]:
            (row, col, value) = part
            new_board.set_value(row, col, value)
        [row, col, value, size] = action[0]
        new_board.add_boat_coordinates(row, col, size)
        new_board.print_board()
        print("-----------------------")
        state.board.print_board()
        print("-----------------------")
        return BimaruState(new_board.calculate_state())

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        
        if len(state.board.complete_cols) != 10 :
            return False
        elif len(state.board.complete_rows) != 10 :
            return False
        elif state.board.ships['Current']['Couraçado'] != state.board.ships['Max']['Couraçado']:
            return False
        elif state.board.ships['Current']['Cruzadores'] != state.board.ships['Max']['Cruzadores']:
            return False
        elif state.board.ships['Current']['Contratorpedeiros'] != state.board.ships['Max']['Contratorpedeiros']:
            return False
        elif state.board.ships['Current']['Submarino'] != state.board.ships['Max']['Submarino']:
            return False
        
        print("-----------------------")
        print("Goal Test")
        state.board.print_board()
        print("-----------------------")
        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:
    board = Board.parse_instance()
    bimaru = Bimaru(board)
    goal_node = depth_first_tree_search(bimaru)
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    pass