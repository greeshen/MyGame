import arcade
import random
import math

XP_RATIO = 50
SILVER_RATIO = 2000


class Tank(arcade.Sprite):
    def __init__(self, name, picture, xp, cost, tank_type, health, damage, armor, accuracy, hit, cooldown, review, disguise, speed, breaking, stabilization, scale):
        super().__init__(picture, scale)
        self.sc = scale
        self.name = name
        self.tank_type = tank_type
        self.hit = hit
        self.health = health
        self.init_health = health
        self.damage = damage
        self.armor = armor
        self.accuracy = accuracy
        self.cooldown = cooldown
        self.review = review
        self.disguise = disguise
        self.xp = xp
        self.cost = cost
        self.upgraded = False
        self.speed = speed
        self.ismoving = False
        self.was_move = False
        self.was_attack = False
        self.tolko_attack = False
        self.recharge = cooldown
        self.dop_disguise = 1
        self.look = False
        self.breaking = breaking
        self.stabilization = stabilization

    def shot(self, other):
        if abs(self.row - other.row) <= 8 and abs(self.col - other.col) <= 7 and self.recharge >= self.cooldown and other.look:
            self.was_attack = True
            self.recharge = 0
            k = 0
            if self.was_move:
                k = self.stabilization
            self.was_move = True
            if random.random() >= other.hit + self.accuracy * max(abs(self.row - other.row), abs(self.col - other.col)) + k:
                if random.random() >= max(other.armor - self.breaking, 0):
                    dm = min(int(self.damage * (1 + random.randint(-25, 25) / 100)), other.health)
                    other.health -= dm
                    return (dm * XP_RATIO, dm * SILVER_RATIO, dm, f"Есть пробитие! Урон: {dm}")
                return ("Не пробил")
            return ("Нет попадания")
        if self.recharge < self.cooldown:
            self.was_attack = True
        return (False, False, False)

    def moving(self, grid):
        m = []
        for i in range(len(grid)):
            mas = []
            for j in range(len(grid[i])):
                if len(grid[i][j]) > 2:
                    mas.append(-2)
                else:
                    mas.append(-1)
            m.append(mas)
        m[self.row][self.col] = 0
        last = []
        while True:
            n = max([max(e) for e in m])
            for i in range(len(m)):
                for j in range(len(m[i])):
                    if m[i][j] == n:
                        mas = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1),
                               (i + 1, j - 1), (i - 1, j + 1), (i - 1, j - 1), (i + 1, j + 1)]
                        for x, y in mas:
                            if 0 <= x < len(m) and 0 <= y < len(m[x]):
                                if m[x][y] == -1:
                                    m[x][y] = n + 1
            if last == m:
                break
            last = [x[:] for x in m]
        ans = []
        for row in range(len(m)):
            for col in range(len(m[row])):
                if 0 < m[col][row] <= self.speed:
                    ans.append((row, col))
        return ans

    def move(self, row, col, k, grid):
        if (col, row) in self.moving(grid):
            m = []
            for i in range(len(grid)):
                mas = []
                for j in range(len(grid[i])):
                    if len(grid[i][j]) > 2:
                        mas.append(-2)
                    else:
                        mas.append(-1)
                m.append(mas)
            m[self.row][self.col] = 0
            path = self.find_path(self.row, self.col, row, col, m)
            self.row = path[-1][0]
            self.col = path[-1][1]
            if not (self.row == row and self.col == col):
                grid[row][col][-1].look = True
            self.center_x = self.row * k + k // 2
            self.center_y = self.col * k + k // 2
            self.was_move = True
            return True
        else:
            return False

    def detection(self, other):
        if other.was_attack:
            detec = self.review * (1 - other.disguise * other.dop_disguise * 0.1)
        elif other.was_move:
            detec = self.review * (1 - other.disguise * other.dop_disguise * 0.4)
        else:
            detec = self.review * (1 - other.disguise * other.dop_disguise)
        if detec >= abs(self.row - other.row) and detec >= abs(self.col - other.col):
            other.look = True
        return other.look

    def upd(self):
        self.recharge += 1
        self.look = False
        self.was_move = False
        self.was_attack = False

    def find_path(self, start_row, start_col, target_row, target_col, m):
        """Поиск пути с помощью Божей"""
        last = []
        while True:
            n = max([max(e) for e in m])
            for i in range(len(m)):
                for j in range(len(m[i])):
                    if m[i][j] == n:
                        mas = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1),
                               (i + 1, j - 1), (i - 1, j + 1), (i - 1, j - 1), (i + 1, j + 1)]
                        for x, y in mas:
                            if 0 <= x < len(m) and 0 <= y < len(m[x]):
                                if m[x][y] == -1:
                                    m[x][y] = n + 1
            if last == m:
                break
            last = [x[:] for x in m]
        it, jt = target_row, target_col
        path = [(target_row, target_col)]
        mi = 100000000000000
        while True:
            mas = [(it - 1, jt), (it + 1, jt), (it, jt - 1), (it, jt + 1),
                   (it + 1, jt - 1), (it - 1, jt + 1), (it - 1, jt - 1), (it + 1, jt + 1)]
            im, jm = 1000, 1000
            for x, y in mas:
                if 0 <= x < len(m) and 0 <= y < len(m[x]) and m[x][y] >= 0:
                    if m[x][y] < mi:
                        mi = m[x][y]
                        im, jm = x, y
            if m[im][jm] == -2:
                break
            path.append((im, jm))
            it, jt = im, jm
            if im == start_row and jm == start_col:
                break
        return path[::-1]