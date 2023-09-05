import random


class BoardOutException(Exception):
    def __init__(self, massege="Выстрел за пределы игрового поля"):
        self.massege = massege
        super().__init__(self.massege)


class Dot:
    def __init__(self):
        self.dot = [[0 for i in range(6)] for j in range(6)]

    def print_dot(self):
        print(" 0 1 2 3 4 5 ")
        for i in range(6):
            print(str(i) + "|" + "|".join(str(self.dot[i][j])) for j in range(6))

    def set_ship(self, x, y):
        if self.dot[x][y] == 0:
           self.dot[x][y] = 1
           return True
        else:
            return False

    def shoot(self, x, y):
        if self.dot[x][y] == 0:
           self.dot[x][y] = -1
           return True
        else:
            return False


class Ship:
    def __init__(self, length, bow, direction):
        self.length = length
        self.bow = bow
        self.direction = direction
        self.lives = length

    def dots(self):
        ship_dots = []
        x, y = self.bow
        for i in range(self.length): ship_dots.append((x, y))
        if self.direction == 'vertical':
            y += 1
        else:
            x += 1
        return ship_dots


class User:
    def __init__(self, name):
        self.name = name
        self.board = []
        self.ships = []
        self.hits = []
        self.misses = []

    def piece_ship(self, ship, x, y, orientation): # проверяем что корабль помещается на доску
        if orientation == "horizontal":
            if x + ship.size > 10:
                return False
        else:
            if y + ship.size > 10:
                return False

# проверяем что корабль не пересекается с другими кораблями
        for other_ship in self.ships:
            for i in range(ship.size):
                if orientation == "horizontal":
                    if (x+i,y) in other_ship.cells:
                        return False
                else:
                    if (x,y+i) in other_ship.cells:
                        return False

# размещаем корабль на доске и сохраняем его
        ship.plece(x, y, orientation)
        self.ships.append(ship)
        for cell in ship.cells:
            self.board[cell[0]][cell[1]] = "O"

        return True

    def fire(self,x ,y):# проверяем что координаты в пределах доски
        if x < 0 or x > 9 or y < 0 or y > 9:
            return False

# проверяем что клетка еще не была атакована
        if(x, y) in self.hits or (x, y) in self.misses:
            return False

# обрабатываем выстрел
        hit = False
        for ship in self.ships:
            if (x, y) in ship.cells:
                hit = True
                ship.hit (x, y)
                self.hits.append((x, y))
                self.board[x][y] = "X"
                if ship.is_sunk():
                    return "sunk"
                else:
                    return "hit"

        if not hit:
            self.misses.append((x, y))
            self.board[x][y] = "-"
            return "miss"

class Board:
    def __init__(self, cells, ships, hid=True):
        self.cells = cells
        self.ships = ships
        self.hid = hid
        self.live_ships = len(ships)

    def __str__(self):
        board_str = ''
        for row in self.cells:
            for cell in row:
                if cell == '' or not self.hid:
                    board_str += cell
                else:
                    board_str += '-'
                board_str += ''
            board_str += '\n'
        return board_str

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or self.cells[dot.y][dot.x] != '':
                raise ValueError('не могу поставить корабль здесь')
            for dot in ship.dots:
                self.cells[dot.y][dot.x] = '.'
            self.ships.append(ship)

    def contour(self, ship):
        for dot in ship.dots:
            for i in range(dot.y -1,dot.y +2):
                for j in range(dot.x -1,dot.x +2):
                    if not self.out(Dot(j,i)) and self.cells[i][j] == '':
                        self.cells[i][j] = '.'

    def out(self, dot):
        return dot.x < 0 or dot.x >= len(self.cells[0]) or dot.y < 0 or dot.y >= len(self.cells)

    def shot(self, dot):
        if self.out(dot) or self.cells[dot.y][dot.x] in ['*','.']:
            raise ValueError ('неверный выстрел')
        elif self.cells[dot.y][dot.x] == '':
            self.cells [dot.y][dot.x] = '.'
        else:
            self.cells[dot.y][dot.x] = '*'
            for ship in self.ship:
                if dot in ship.dots :
                    ship.live_dots.remove(dot)
                    if not ship.live_dots:
                        self.live_ships -= 1
                        self.contour(ship)
                    break

    def game_over(self):
        return not self.live_ships


class Player:
    def __init__(self, name, own_board, enemy_board):
        self.name = name
        self.own_board = own_board
        self.enemy_board = enemy_board

    def move(self):
        while True:
            try:
                row, col = self.ask()
                result = self.enemy_board.shot(row, col)
                if result == "выстрел":
                    print("ты повредил вражеский корабль")
                    if self.enemy_board.is_game_over():
                        print(f"{self.name} wins")
                        return False
                    return True
                elif result == "miss":
                    print("вы пропустили!")
                    return False
                elif result == "sunk":
                    print("ты потопил вражеский корабль!")
                    if self.enemy_board.is_game_over():
                        print(f"{self.name} wins!")
                        return False
                    return True
            except ValueError as e:
                print(e)
                print("Неверный ввод. Попробуйте еще раз")

    def ask(self):
        pass


class AI(Player):
    def ask(self):
        row = int(input("введите номер строки: "))
        col = int(input("введите номер столбца: "))
        return row, col


class Board:
    SHIP_TYPES = [(5, "carrier"), (4, "battleship"), (3, "cruiser"), (3, "submarine"), (2, "destroyer")]

    def __init__(self):
        self.grid = [[None for x in range(10)] for y in range(10)]
        self.ships = []
        self.remaining_ships = len(self.SHIP_TYPES)
        self.place_ships()

    def place_ships(self):
        for size, name in self.SHIP_TYPES:
            while True:
                direction = random.choice(["horizontal", "vertical"])
                if direction == "horizontal":
                    row = random.randint(0, 9)
                    col = random.randint(0, 9 - size + 1)
                    coords = [(row, c) for c in range(col, col + size)]
                else:
                    row = random.randint(0, 9 - size + 1)
                    col = random.randint(0, 9)
                    coords = [(r, col) for r in range(row, row + size)]
                    if all(self.is_valid_coord(r, c) and self.grid[r][c]) is None for r, c in coords):
                        self.ships.append(coords) for r, c in coords:
                        self.grid[r][c] = name
                    break

    def is_valid_coord(self, row, col):
        return 0 <= row < 10 and 0 <= col < 10

    def shot(self, row, col):
        if not self.is_valid_coord(row, col):
            raise ValueError("Неверные координаты!")
        if self.grid[row][col] is None:
            self.grid[row][col] = "miss"
            return "miss"
        elif self.grid[row][col] == "miss" or self.grid[row][col] == "hit":
            raise ValueError("Ты уже там стрелял")
        else:
            ship_name = self.grid[row][col]
            self.grid[row][col] = "hit"
            for ship in self.ships:
                if (row, col) in ship:
                    ship.remove((row, col))
                    if len(ship) == 0:
                        print(f"Ты потопил {ship_name}!")
                        self.remaining_ships -= 1
                        if self.remaining_ships == 0:
                            return "game_over"
                        return "sunk"
                    else:
                        return "hit"

    def is_game_over(self):
        return self.remaining_ships == 0

    def get_random_coords(self):
        row = random.randint(0, 9)
        col = random.randint(0, 9)
        return row, col


class Game:
    def __init__(self):
        self.user_board = Board()
        self.ai_board = Board()
        self.user = User("User", self.user_board, self.ai_board)
        self.ai = AI("AI", self.ai_board, self.user_board)

    def random_board(self, board):
        attempts = 0
        while True:
            for size, name in board.SHIP_TYPES:
                direction = random.choice(["horizontal", "vertical"])
                if direction == "horizontal":
                    row = random.randint(0, 9)
                    col = random.randint(0, 9 - size + 1)
                    coords = [(row, c) for c in range(col, col + size)]
                else:
                    row = random.randint(0, 9 - size + 1)
                    col = random.randint(0, 9)
                    coords = [(r, col) for r in range(row, row + size)]
                if all(board.is_valid_coord(r, c) and board.grid[r][c] is None for r, c in coords):
                    board.append(coords)
                    for r, c in coords:
                        board.grid[r][c] = name
                else:
                    attempts += 1
                    if attempts > 10000:
                        print("Не удалось создать действительную доску")
                        return

                if len(board.ships) == len(board.SHIP_TYPES):
                    break

    def greet(self):
        print("Добро пожаловать в Морской бой")
        print("Чтобы сделать ход, введите номер строки (0-9) и номер столбца (0-9) отдельно ")

    def loop(self):
        while True:
            if self.user.move() == False:
                return
            if self.ai.move() == False:
                return

    def start(self):
        self.greet()
        self.random_board(self.user_board)
        self.random_board(self.ai_board)
        self.loop()


game = Game()
game.start()

