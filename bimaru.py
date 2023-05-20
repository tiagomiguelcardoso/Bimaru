# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 41:
# 99190 Catarina Neves Santos
# 103561 Tiago Miguel Santos Cardoso

import sys
import numpy as np 
#import cProfile
#import inspect
#import pstats
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


class Board:
    """Representação interna de um tabuleiro de Bimaru."""
    
    def __init__(self, positions, rows, columns):
        self.positions = np.copy(positions)
        self.positions_to_print = np.copy(positions)
        self.rows = rows
        self.columns = columns
        self.rows_data =[{"Parts": 0, "Nones": 0, "Water": 0} for _ in range(10)]
        self.cols_data =[{"Parts": 0, "Nones": 0, "Water": 0} for _ in range(10)]
        self.complete_rows = set()
        self.complete_cols = set()
        self.empty_positions = []
        self.boat_coordinates = []
        self.possible_values = []
        self.ships = {'Couraçado': 0, 'Cruzadores': 0, 'Contratorpedeiros': 0, 'Submarino': 0}
        self.parts = {"C": 0, "T": 0, "L": 0, "B": 0 ,"R": 0, "M":0}

    def calculate_state(self):
        '''Completa o board'''
        self.completed_board()

        '''Celulas Vazias'''
        self.empty_positions = [(row, col) for (row, col) in self.empty_positions if self.positions[row, col] is None and not self.check_if_water(row, col)]

        '''Procura açoes para cada posiçao'''
        size = self.get_board_level()


        occupied_positions = [(i, j) for i in range(10) for j in range(10) if self.get_value(i, j) != "W"]

        for (row, col) in occupied_positions:
                if[row, col] in self.boat_coordinates:
                    continue
                else:
                    val = self.get_value(row, col)
                    actions = self.maybe_boat_check(row, col, val ,size)
                    if type(actions) == list:
                        for action in actions:
                            if self.can_place_water_around(row, col, action[0][2], size):
                                self.possible_values.append(action)
        
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
            if i not in self.complete_rows and self.completed_rows(i):
                self.complete_rows.add(i)
            if i not in self.complete_cols and self.completed_cols(i):
                self.complete_cols.add(i)

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

    def get_value_s(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        if 0 <= row < 10 and 0 <= col < 10:
            return self.positions[row][col]
        else:
            return None

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.positions[row][col]

    def print_board(self):
        for row in self.positions_to_print:
            row_str = ''.join([str(element) if element not in (None, "w") else "." for element in row])
            print(row_str)
        
    def set_value(self, row, col, value):
        self.positions[row][col] = value
        self.positions_to_print[row][col] = value.lower()
        '''
        if value == "W":
            self.positions[row][col] = "W"
            self.positions_to_print[row][col] = "."
        else:
            self.positions[row][col] = value
            self.positions_to_print[row][col] = value.lower()
        '''

    def adjacent_values(self, row: int, col: int):
        adjacents = []
        adjacents.append(self.get_value_s(row-1,col-1))
        adjacents.append(self.get_value_s(row-1,col))
        adjacents.append(self.get_value_s(row-1,col+1))
        adjacents.append(self.get_value_s(row,col-1))
        adjacents.append(self.get_value_s(row,col+1))
        adjacents.append(self.get_value_s(row+1,col-1))
        adjacents.append(self.get_value_s(row+1,col))
        adjacents.append(self.get_value_s(row+1,col+1))
        return adjacents

    def is_boat(self, value):
        return value in ("C", "T", "M", "B", "L", "R")

    def maybe_boat_check(self, row, col, val, size):
        if val == "T":
            if size == 1:
                return False
            action = self.check_boat(row, col, "V", size)
            if len(action) != 0:
                return [action]

        elif val == "L":
            if size == 1:
                return False
            action = self.check_boat(row, col, "H", size)
            if len(action) != 0:
                return [action]

        elif val is None:
            if size == 1:
                if col in self.complete_cols or row in self.complete_rows:
                    return False
                else:
                    return [[[row, col, "C", size], [row, col, "C"]]]

            actionV = self.check_boat(row, col, "V", size)
            actionH = self.check_boat(row, col, "H", size)
            if len(actionV) != 0 and len(actionH) != 0:
                return [actionV, actionH]
            elif len(actionV) != 0:
                return [actionV]
            elif len(actionH) != 0:
                return [actionH]

        elif val == "C":
            self.add_boat_coordinates(row, col, 1)
            return False

        return False

  
    def check_boat(self, row, col, val, size):

        boat_types = {1: ["C"], 
            2:{"V":["T", "B"], "H": ["L", "R"]}, 
            3:{"V":["T", "M","B"], "H": ["L", "M", "R"]},
            4:{"V":["T", "M", "M", "B"], "H": ["L", "M", "M", "R"]}}

        if val == "V":
            if (row + size - 1) <= 9:
                action = [[row, col, val, size]]
                v = [self.get_value(row + i, col) for i in range(size)]
                if all(v[p] in (None, boat_types[size]["V"][p]) for p in range(size)):
                    [action.append([row + p, col, boat_types[size]["V"][p]]) for p in range(size) if v[p] == None]
                    if self.cant_place_boat("V", col, action):
                        return []
                    return action
            return []

        elif val == "H":
            if (col + size - 1) <= 9:
                action = [[row, col, val, size]]
                v = [self.get_value(row, col + i) for i in range(size)]
                if all(v[p] in (None, boat_types[size]["H"][p]) for p in range(size)):
                    [action.append([row, col+p, boat_types[size]["H"][p]]) for p in range(size) if v[p] == None]
                    if self.cant_place_boat("H", row, action):
                        return []
                    return action
            return []

    def get_board_level(self):
        if self.ships["Couraçado"] < 1:
            return 4
        elif self.ships["Cruzadores"] < 2:
            return 3
        elif self.ships["Contratorpedeiros"] < 3:
            return 2
        elif self.ships["Submarino"] < 4:
            return 1
        else:
            return 0
    
    def add_boat_coordinates(self, row, col, size):
        ship_mapping = {4: 'Couraçado', 3: 'Cruzadores', 2: 'Contratorpedeiros', 1: 'Submarino'}
        ship_name = ship_mapping.get(size)
        if ship_name:
            self.ships[ship_name] = self.ships.get(ship_name, 0) + 1
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
        return all(self.get_value_s(row, col) in [None, "W"] for (row, col) in positions)

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
        new_board.positions_to_print = np.copy(board.positions_to_print)
        new_board.complete_cols = set(item for item in board.complete_cols)
        new_board.complete_rows = set(item for item in board.complete_rows)
        new_board.rows = np.copy(board.rows)
        new_board.columns = np.copy(board.columns)
        new_board.boat_coordinates = np.copy(board.boat_coordinates).tolist()
        new_board.ships = self.deep_copy_dict(board.ships)
        new_board.empty_positions = np.copy(board.empty_positions)
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
        #print("-----------------------")
        #print("Actions")
        #print("Level: ", state.board.get_board_level())
        #print("Barcos: ", state.board.ships)
        #print("Coordenadas: ", state.board.boat_coordinates)
        #state.board.print_board()
        #[print(p) for p in possibilities]
        #print("-----------------------")

        #time.sleep(5)
        return state.board.possible_values

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        #print("-----------------------")
        #print("Result")

        new_board = state.board.copy_board(state.board)
        
        for part in action[1:]:
            (row, col, value) = part
            new_board.set_value(row, col, value)
        [row, col, value, size] = action[0]
        new_board.add_boat_coordinates(row, col, size)
        #new_board.print_board()
        #print("-----------------------")
        #state.board.print_board()
        #print("-----------------------")
        return BimaruState(new_board.calculate_state())

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        
        if state.board.ships['Couraçado'] != 1:
            return False
        elif state.board.ships['Cruzadores'] != 2:
            return False
        elif state.board.ships['Contratorpedeiros'] != 3:
            return False
        elif state.board.ships['Submarino'] != 4:
            return False
        
        #state.board.print_board()
        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        n = len(node.state.board.possible_values)
        return  n

    # TODO: outros metodos da classe


if __name__ == "__main__":
    #profiler = cProfile.Profile()
    # Start profiling
    #profiler.enable()

    # Call the main function or execute the code you want to profile
    board = Board.parse_instance()
    board.empty_positions = [(i, j) for i in range(10) for j in range(10)]
    bimaru = Bimaru(board)
    goal_node = depth_first_tree_search(bimaru)
    goal_node.state.board.print_board()
    # Stop profiling
    #profiler.disable()

    #profiler.print_stats()

    '''
    # Create a pstats.Stats object from the profiler
    stats = pstats.Stats(profiler)
    
    # Sort the statistics by the number of calls
    stats.sort_stats(pstats.SortKey.CALLS)

    # Print the function callers with the line number
    stats.print_callers()  # Adjust the number as per your requirement
    '''
    '''
    # Profile each function in bimaru.py
    functions = [m[1] for m in inspect.getmembers(bimaru) if inspect.isfunction(m[1])]
    for func in functions:
        print(f"Profiling function: {func.__name__}")
        profile_function(func)
    pass
    '''