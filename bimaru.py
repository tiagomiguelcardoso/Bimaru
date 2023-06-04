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

''' Todos os hashs para boards já pesquisados '''
visited_boards = {}

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
        self.rows_data = []
        self.cols_data = []
        self.complete_rows = set()
        self.complete_cols = set()
        self.empty_positions = []
        self.boat_coordinates = []
        self.possible_values = []
        self.level = 0
        self.ships = {'Couraçado': 0, 'Cruzadores': 0, 'Contratorpedeiros': 0, 'Submarino': 0}

    def calculate_state(self):
        '''Procura açoes para cada posiçao'''

        ''' Procura o hash ou adiciona caso este board ainda n tenha sido avaliado '''
        hash_code = self.codificar()
        if hash_code in visited_boards:
            return self

        visited_boards[hash_code] = True
        
        size = self.get_board_level()
        self.level = size
        '''Completa o board caso uma linha/colunas ja esteja cheia de parts'''
        self.completed_board()

        '''Vai a todas as celulas que podem ser ocupadas e ve se um barco pode ser colocado ali'''
        for (row, col) in self.empty_positions:
            if (row, col) in self.boat_coordinates:
                continue
            else:
                actions = self.maybe_boat_check(row, col, size)
                if actions is not False:
                    for action in actions:
                        value = action["Inicio"][2]
                        water = self.can_place_water_around(row, col, value, size)
                        if water["Valid"]:
                            action["Water"] = water["Posiçoes"]
                            self.possible_values.append(action)
        
        '''Verifica que este board tem o minimo de açoes necessarias para este nivel '''
        ship_mapping = {4: 'Couraçado', 3: 'Cruzadores', 2: 'Contratorpedeiros', 1: 'Submarino'}
        ship_name = ship_mapping.get(size)
        if ship_name:
            if (5 - size) > (len(self.possible_values) + self.ships[ship_name]):
                self.possible_values = []
        return self

    #########################
    #    BASIC FUNCTIONS    #
    #########################

    def codificar(self):
        '''Transforma um board num hashcode'''
        positions_tuple = tuple(map(tuple, self.positions))
        return hash(positions_tuple)

    def completed_cols(self, col: int):
        '''Preenche uma column se tiver o maximo de parts'''
        if self.cols_data[col] == self.columns[col]:
            [self.set_value(i,col,"W") for i in range(10) if self.get_value(i,col) is None]
            return True
        else:
            return False

    def completed_rows(self, row: int):
        '''Preenche uma row se tiver o maximo de parts'''
        if self.rows_data[row] == self.rows[row]:
            [self.set_value(row,i,"W") for i in range (10) if self.get_value(row, i) is None]
            return True
        else:
            return False

    def completed_board(self):
        '''Adiciona as rows/columns completas'''
        for i in range(10):
            if i not in self.complete_rows and self.completed_rows(i):
                self.complete_rows.add(i)
            if i not in self.complete_cols and self.completed_cols(i):
                self.complete_cols.add(i)

    def get_value_s(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro (verifica se está in-bounds)"""
        if 0 <= row < 10 and 0 <= col < 10:
            return self.positions[row][col]
        else:
            return None

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.positions[row][col]

    def print_board(self):
        '''Dá print ao board'''
        for row in self.positions_to_print:
            row_str = ''.join([str(element) if element not in (None, "w") else "." for element in row])
            print(row_str)
        
    def set_value(self, row, col, value):
        '''Coloca um valor na posição'''
        self.positions[row][col] = value
        self.positions_to_print[row][col] = value.lower()
        self.empty_positions.remove((row, col))

        if value != "W":
            self.rows_data[row] += 1
            self.cols_data[col] += 1

    def adjacent_values(self, row: int, col: int):
        '''Devolve os valores adjacentes'''
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
        '''Verifica de é parte de um barco'''
        return value in ("C", "T", "M", "B", "L", "R")

    def get_board_level(self):
        '''Retorna o tamanho do barco que estamos à procura'''
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

    def increase_boat_count(self, row, col, size):
        '''Adiciona o barco ao self.ships e às self.boat_coordinates'''
        ship_mapping = {4: 'Couraçado', 3: 'Cruzadores', 2: 'Contratorpedeiros', 1: 'Submarino'}
        ship_name = ship_mapping.get(size)
        if ship_name:
            self.ships[ship_name] = self.ships.get(ship_name, 0) + 1
        self.boat_coordinates.append((row, col))

    def check_if_water(self, row, col):
        '''Verifica se um valor é obrigatoriamente agua'''
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

    #########################
    #     BOAT FUNCTIONS    #
    #########################

    def maybe_boat_check(self, row, col, size):
        '''Verifica se pode ser a ponta de um barco ('C', 'T', 'L')'''
        val = self.get_value(row, col)
        action = {}
        if val == "T":
            if size == 1:
                return False
            action = self.check_boat(row, col, "T", size)
            if action != False:
                return [action]

        elif val == "L":
            if size == 1:
                return False
            action = self.check_boat(row, col, "L", size)
            if action != False:
                return [action]

        elif val is None:
            if size == 1:
                if col in self.complete_cols or row in self.complete_rows:
                    return False
                else:
                    action["Inicio"] = [row, col, "C", size]
                    action["Parts"] = [[row, col, "C"]]
                    return [action]

            actionT = self.check_boat(row, col, "T", size)
            actionL = self.check_boat(row, col, "L", size)
            if actionT != False and actionL != False:
                return [actionT, actionL]
            elif actionT != False:
                return [actionT]
            elif actionL != False:
                return [actionL]

        elif val == "C":
            self.increase_boat_count(row, col, 1)
            return False

        return False

    def check_boat(self, row, col, val, size):
        '''Verifica se o barco pode ser de facto colocado ali'''
        boat_types = {1: ["C"], 
            2:{"T":["T", "B"], "L": ["L", "R"]}, 
            3:{"T":["T", "M","B"], "L": ["L", "M", "R"]},
            4:{"T":["T", "M", "M", "B"], "L": ["L", "M", "M", "R"]}}

        action = {}

        if val == "T":
            '''Verifica se não sai das bounds'''
            if (row + size - 1) <= 9:
                action["Inicio"] = [row, col, val, size]
                v = [self.get_value(row + i, col) for i in range(size)]
                '''Verifica que as posiçoes onde vao ser colocados os barcos já tem a posição ou então está vazio'''
                if all(v[p] in (None, boat_types[size]["T"][p]) for p in range(size)):
                    '''Adiciona posiçoes onde vao ser colocados valores'''
                    action["Parts"] = [[row + p, col, boat_types[size]["T"][p]] for p in range(size) if v[p] == None]
                    '''Verifica se há espaço suficiente para as peças que são preciso colocar'''
                    if self.cant_place_boat("T", col, action):
                        return False
                    return action
            return False

        elif val == "L":
            if (col + size - 1) <= 9:
                action["Inicio"] = [row, col, val, size]
                v = [self.get_value(row, col + i) for i in range(size)]
                if all(v[p] in (None, boat_types[size]["L"][p]) for p in range(size)):
                    action["Parts"] = [[row, col+p, boat_types[size]["L"][p]] for p in range(size) if v[p] == None]
                    if self.cant_place_boat("L", row, action):
                        return False
                    return action
            return False
 
    def can_place_water_around(self, row, col, value, size):
        '''Verifica se agua pode ser colocada à volta do barco'''
        water = {}
        positions = []
        if value == "T":
            for i in range(row - 1, row + size + 1):
                positions.append((i, col-1))
                positions.append((i, col+1))
            positions.extend([(row-1, col), (row+size, col)])
                
        elif value == "L":
            for j in range(col - 1, col + size + 1):
                positions.append((row-1, j))
                positions.append((row+1, j))
            positions.extend([(row, col-1), (row, col+size)])

        elif value == "C":
            positions = []
            positions.append((row-1,col-1))
            positions.append((row-1,col))
            positions.append((row-1,col+1))
            positions.append((row,col-1))
            positions.append((row,col+1))
            positions.append((row+1,col-1))
            positions.append((row+1,col))
            positions.append((row+1,col+1))
    
        ''' Verifica se as posições ao redor do barco são "W" ou None '''
        water["Posiçoes"] = [(row, col) for (row, col) in positions if self.get_value_s(row, col) is None and row in range(0, 10) and col in range(0,10)]
        water["Valid"] = all(self.get_value_s(row, col) in [None, "W", "w"] for (row, col) in positions)
        return water

    def cant_place_boat(self, tipo, place, action):
        '''Retorna se há peças para o barco ser colocado'''
        if tipo == "T":
            try:
                if any(r[0] in self.complete_rows for r in (action["Parts"])) or ((self.columns[place] - self.cols_data[place]) < len(action["Parts"])):
                    return True
                else:
                    return False
            except:
                return False
        elif tipo == "L":
            try:
                if any(r[1] in self.complete_cols for r in (action["Parts"])) or ((self.rows[place] - self.rows_data[place]) < len(action["Parts"])):
                    return True
                else:
                    return False
            except:
                return False

    #########################
    #    BOARD FUNCTIONS    #
    #########################

    def copy_board(self, board):
        '''Copia um board'''
        new_board = Board([], [], [])
        new_board.positions = np.copy(board.positions)
        new_board.positions_to_print = np.copy(board.positions_to_print)
        new_board.complete_cols = set(item for item in board.complete_cols)
        new_board.complete_rows = set(item for item in board.complete_rows)
        new_board.rows = np.copy(board.rows)
        new_board.columns = np.copy(board.columns)
        new_board.boat_coordinates = np.copy(board.boat_coordinates).tolist()
        new_board.boat_coordinates = [tuple(pos) for pos in new_board.boat_coordinates]
        new_board.ships = self.deep_copy_dict(board.ships)
        new_board.empty_positions = np.copy(board.empty_positions).tolist()
        new_board.empty_positions = [tuple(pos) for pos in new_board.empty_positions]
        new_board.rows_data = np.copy(board.rows_data)
        new_board.cols_data = np.copy(board.cols_data)
        return new_board

    def deep_copy_dict(self, original_dict):
        '''Cria uma deep copy de um dicionario'''
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
        e retorna uma instância da classe Board. """

        positions = np.full((10, 10), None)

        line = sys.stdin.readline().strip("\n")
        rows = tuple(map(int, line.split("\t")[1:]))
        line = sys.stdin.readline().strip("\n")
        columns =  tuple(map(int, line.split("\t")[1:]))

        num_hints = int(sys.stdin.readline().strip("\n"))

        board = Board(positions, rows, columns)

        board.empty_positions = [(row, col) for row in range(10) for col in range(10) if positions[row][col] != "W"]
        board.rows_data = [0 for _ in range(10)]
        board.cols_data = [0 for _ in range(10)]

        for i in range(num_hints):
            line = sys.stdin.readline().strip("\n")
            hint = line.split()
            row = int(hint[1])
            col = int(hint[2])
            value = hint[3]
            board.positions[row][col] = value
            board.positions_to_print[row][col] = value
            if value != "W":
                board.rows_data[row] += 1
                board.cols_data[col] += 1
        
        board.empty_positions = [(row, col) for (row, col) in board.empty_positions[:] if board.get_value(row, col) != "W"]
        board.empty_positions = [(row, col) for (row, col) in board.empty_positions[:] if board.positions[row, col] is not board.check_if_water(row, col)]
        return board.calculate_state()

class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        state = BimaruState(board)
        super().__init__(state)
        pass

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""

        possible_values = state.board.possible_values
        if len(possible_values) >1:
            shift_amount = np.random.randint(len(possible_values))
            shifted_values = possible_values[shift_amount:] + possible_values[:shift_amount]
            return shifted_values
        else:
            return possible_values

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        new_board = state.board.copy_board(state.board)

        for part in action["Parts"]:
            (row, col, value) = part
            new_board.set_value(row, col, value)
        [row, col, value, size] = action["Inicio"]
        new_board.increase_boat_count(row, col, size)

        for (row, col) in action["Water"]:
            new_board.set_value(row, col, "W")
    
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
        
        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        n = len(node.state.board.empty_positions)
        return  n

if __name__ == "__main__":

    board = Board.parse_instance()
    bimaru = Bimaru(board)
    goal_node = depth_first_tree_search(bimaru)
    goal_node.state.board.print_board()

