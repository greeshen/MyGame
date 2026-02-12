import arcade
import random
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UIFlatButton, UITextureButton, UILabel, UIInputText, \
    UITextArea, UISlider, UIDropdown, UIMessageBox  # Это разные виджеты

from pyglet.event import EVENT_HANDLE_STATE
from pyglet.graphics import Batch

import tanks

# Параметры экрана
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Клетчатое поле"
TANKS = {"name": (
"images/tank_prototype.bmp", 250000, 5900000, "tank_type", 2100, 370, 0.14, 0.02, 0.15, 1, 5, 0.50, 5, 0.13, 0.34, 1),
         "heavy": (
         "images/prototype_heavy_tank.bmp", 220987, 6700000, "tank_type", 3100, 755, 0.4, 0.057, 0.05, 3, 3, 0.1, 3,
         0.09, 0.1, 1),
         "tank1": (
         "images/tank1.bmp", 267987, 6120000, "tank_type", 2400, 1055, 0.35, 0.1, 0.05, 4, 4, 0.1, 3, 0.2, 0.5, 1),
         "tank2": (
         "images/tank2.bmp", 220000, 5120000, "tank_type", 1500, 220, 0.15, 0.02, 0.3, 1, 7, 0.5, 6, 0.14, 0.1, 1),
         "tank3": (
         "images/tank3.bmp", 280000, 7770000, "tank_type", 2500, 520, 0.1, 0.06, 0.15, 1, 3, 0.12, 3, 0.11, 0.2, 1),
         "tank4": (
         "images/tank6.bmp", 310000, 8770000, "tank_type", 3500, 720, 0.4, 0.071, 0.15, 3, 2, 0.01, 2, 0.11, 0.2, 1),
         "tank5": (
         "images/tank4.bmp", 256000, 4990000, "tank_type", 2300, 450, 0.1, 0.011, 0.25, 1, 4, 0.01, 5, 0.11, 0.2, 0.25)}
SCALE = 1


class GameWindow(arcade.View):
    def __init__(self):
        super().__init__()
        self.cell_size = 40
        self.rows = 40
        self.cols = 40
        self.grass_texture = arcade.load_texture(":resources:images/tiles/grassCenter.png")
        self.water_texture = arcade.load_texture(":resources:images/tiles/water.png")
        self.all_sprites = arcade.SpriteList()
        self.base = arcade.SpriteList()
        self.ismoving = False
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.batch = Batch()
        self.texts = []
        self.team1 = arcade.SpriteList()
        self.team2 = arcade.SpriteList()
        self.buttons = arcade.SpriteList()
        mark = arcade.Sprite("images/check_mark.bmp", scale=0.05)
        mark.center_x = self.width // 2 - 50
        mark.center_y = mark.height // 2 + 10
        self.buttons.append(mark)
        mark = arcade.Sprite("images/research.bmp", scale=1)
        mark.center_x = self.width // 2 + 30
        mark.center_y = mark.height // 2 + 10
        self.buttons.append(mark)
        self.team1_par = {"silver": 42000000, "xp": 0, "capture": 0}
        self.team2_par = {"silver": 42000000, "xp": 0, "capture": 0}
        self.par = arcade.SpriteList()
        self.turn = 0
        self.turn_sl = {0: [self.team1, self.team1_par], 1: [self.team2, self.team2_par]}
        self.team1_up = random.choices(list(TANKS.keys()), k=3)
        self.team2_up = random.choices(list(TANKS.keys()), k=3)
        self.world_camera = arcade.camera.Camera2D()  # Камера для игрового мира
        self.gui_camera = arcade.camera.Camera2D()
        # Создаём пустую сетку нужного размера
        self.setup()
        self.red_capture = False
        self.green_capture = False

    def setup(self):
        # Заполняем сетку случайными значениями
        self.world_width = self.cols * self.cell_size * SCALE
        self.world_height = self.rows * self.cell_size * SCALE
        red_base = arcade.Sprite("images/red_base.bmp", scale=0.3)
        red_base.center_x = self.cell_size * SCALE * 5 + self.cell_size * SCALE // 2
        red_base.center_y = self.cell_size * SCALE * 5 + self.cell_size * SCALE // 2
        self.red_row, self.red_col = 5, 5
        red_base.row = self.red_row
        red_base.col = self.red_col
        red_base.sc = 0.3
        green_base = arcade.Sprite("images/green_base.bmp", scale=0.35)
        green_base.center_x = 25 * self.cell_size * SCALE + self.cell_size * SCALE // 2
        green_base.center_y = 25 * self.cell_size * SCALE + self.cell_size * SCALE // 2
        green_base.sc = 0.35
        self.green_row, self.green_col = 25, 25
        green_base.row = self.green_row
        green_base.col = self.green_col
        self.grid = [[random.choice([0] * 9 + [1]) for _ in range(self.rows)] for _ in
                     range(self.cols)]  # Сначала генерим чиселки
        for row in range(self.rows):  # Потом создаём спрайтики и заменяем чиселки на спрайтики
            for col in range(self.cols):
                x = col * self.cell_size * SCALE + self.cell_size * SCALE // 4 * 3 + 2 * SCALE
                y = row * self.cell_size * SCALE + self.cell_size * SCALE // 4 * 3 + 2 * SCALE
                if (row == self.red_row and col == self.red_col) or (row == self.red_row and col == self.red_col):
                    self.grid[row][col] = 0
                    grass_sprite = arcade.Sprite(self.grass_texture, scale=0.5)
                    grass_sprite.position = (x, y)
                    grass_sprite.sc = 0.5
                    grass_sprite.row = row
                    grass_sprite.col = col
                    self.grid[row][col] = [grass_sprite]
                    self.grid[row][col].append(0)
                    self.all_sprites.append(grass_sprite)
                elif self.grid[row][col] == 0:
                    self.grid[row][col] = 0
                    grass_sprite = arcade.Sprite(self.grass_texture, scale=0.5)
                    grass_sprite.position = (x, y)
                    grass_sprite.sc = 0.5
                    grass_sprite.row = row
                    grass_sprite.col = col
                    self.grid[row][col] = [grass_sprite]
                    self.grid[row][col].append(0)
                    self.all_sprites.append(grass_sprite)
                elif self.grid[row][col] == 1:
                    water_sprite = arcade.Sprite(self.water_texture, scale=0.5)
                    water_sprite.position = (x, y)
                    water_sprite.sc = 0.5
                    water_sprite.row = row
                    water_sprite.col = col
                    self.grid[row][col] = [water_sprite]
                    self.grid[row][col].append(1)
                    self.all_sprites.append(water_sprite)
        s1 = arcade.Sprite("images/silver.bmp", scale=0.08)
        s1.center_x = 13
        s1.center_y = SCREEN_HEIGHT - 13
        self.par.append(s1)
        xp1 = arcade.Sprite("images/xp.bmp", scale=0.21)
        xp1.center_x = 13
        xp1.center_y = SCREEN_HEIGHT - 43
        self.par.append(xp1)
        self.base.append(green_base)
        self.base.append(red_base)

    def angar(self):
        if self.turn == 0:
            if len(self.grid[self.red_row][self.red_col]) > 2:
                game_view = UpgradeOrBuyTank(self.team1_up, self.team1_par["silver"], self.team1_par["xp"], False,
                                             arcade.color.RED, self)
            else:
                game_view = UpgradeOrBuyTank(self.team1_up, self.team1_par["silver"], self.team1_par["xp"], True,
                                             arcade.color.RED, self)
        else:
            if len(self.grid[self.green_row][self.green_col]) > 2:
                game_view = UpgradeOrBuyTank(self.team2_up, self.team2_par["silver"], self.team2_par["xp"], False,
                                             arcade.color.BOTTLE_GREEN, self)
            else:
                game_view = UpgradeOrBuyTank(self.team2_up, self.team2_par["silver"], self.team2_par["xp"], True,
                                             arcade.color.BOTTLE_GREEN, self)
        self.window.show_view(game_view)

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        for sp in self.all_sprites:
            sp.scale = sp.sc * SCALE
            sp.center_x = sp.row * SCALE * self.cell_size + self.cell_size * SCALE // 4 * 3 + 2 * SCALE
            sp.center_y = sp.col * SCALE * self.cell_size + self.cell_size * SCALE // 4 * 3 + 2 * SCALE
        self.all_sprites.draw()
        for sp in self.base:
            sp.scale = sp.sc * SCALE
            sp.center_x = sp.row * SCALE * self.cell_size + self.cell_size * SCALE // 2
            sp.center_y = sp.col * SCALE * self.cell_size + self.cell_size * SCALE // 2
        self.base.draw()
        t = arcade.SpriteList()
        if self.turn == 0:
            for tank1 in self.team1:
                tank1.scale = tank1.sc * SCALE
                tank1.center_x = tank1.row * SCALE * self.cell_size + SCALE * self.cell_size // 2
                tank1.center_y = tank1.col * SCALE * self.cell_size + SCALE * self.cell_size // 2
                for tank2 in self.team2:
                    if tank1.detection(tank2):
                        if tank2 not in t:
                            tank2.scale = tank2.sc * SCALE
                            tank2.center_x = tank2.row * SCALE * self.cell_size + SCALE * self.cell_size // 2
                            tank2.center_y = tank2.col * SCALE * self.cell_size + SCALE * self.cell_size // 2
                            t.append(tank2)
            self.team1.draw()
        else:
            for tank1 in self.team2:
                tank1.scale = tank1.sc * SCALE
                tank1.center_x = tank1.row * SCALE * self.cell_size + SCALE * self.cell_size // 2
                tank1.center_y = tank1.col * SCALE * self.cell_size + SCALE * self.cell_size // 2
                for tank2 in self.team1:
                    if tank1.detection(tank2):
                        if tank2 not in t:
                            tank2.scale = tank2.sc * SCALE
                            tank2.center_x = tank2.row * SCALE * self.cell_size + SCALE * self.cell_size // 2
                            tank2.center_y = tank2.col * SCALE * self.cell_size + SCALE * self.cell_size // 2
                            t.append(tank2)
            self.team2.draw()
        t.draw()
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.cell_size * SCALE + self.cell_size * SCALE // 2
                y = row * self.cell_size * SCALE + self.cell_size * SCALE // 2
                arcade.draw_rect_outline(arcade.rect.XYWH(x, y,
                                                          self.cell_size * SCALE - 1,
                                                          self.cell_size * SCALE - 1),
                                         arcade.color.BLACK, 1)
        if self.ismoving:
            tank = self.grid[self.x1][self.y1][-1]
            mas = tank.moving(self.grid)
            if not tank.was_move:
                for row, col in mas:
                    if 0 <= row < len(self.grid) and 0 <= col < len(self.grid[row]):
                        if not len(self.grid[col][row]) > 2:
                            arcade.draw_circle_filled(col * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                      row * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                      15 * SCALE, arcade.color.SKY_BLUE)
                            arcade.draw_circle_filled(col * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                      row * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                      10 * SCALE, arcade.color.WHITE)
                            arcade.draw_circle_filled(col * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                      row * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                      5 * SCALE, arcade.color.SKY_BLUE)
                        else:
                            if not self.grid[col][row][-1].look and self.grid[col][row][-1] in \
                                    self.turn_sl[(self.turn + 1) % 2][0]:
                                arcade.draw_circle_filled(col * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                          row * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                          15 * SCALE,
                                                          arcade.color.SKY_BLUE)
                                arcade.draw_circle_filled(col * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                          row * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                          10 * SCALE,
                                                          arcade.color.WHITE)
                                arcade.draw_circle_filled(col * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                          row * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                          5 * SCALE,
                                                          arcade.color.SKY_BLUE)
            mas = [(y, x) for x in range(self.x1 - 7, self.x1 + 7 + 1) for y in
                   range(self.y1 - 7, self.y1 + 7 + 1)]
            if tank.recharge >= tank.cooldown:
                for row, col in mas:
                    if 0 <= row < len(self.grid) and 0 <= col < len(self.grid[row]):
                        if len(self.grid[col][row]) > 2 and not (tank.row == col and tank.col == row) and \
                                self.grid[col][row][-1] not in self.turn_sl[self.turn][0] and self.grid[col][row][
                            -1].look:
                            arcade.draw_circle_filled(col * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                      row * self.cell_size * SCALE + self.cell_size * SCALE // 2, 15,
                                                      arcade.color.RED)
                            arcade.draw_circle_filled(col * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                      row * self.cell_size * SCALE + self.cell_size * SCALE // 2, 10,
                                                      arcade.color.WHITE)
                            arcade.draw_circle_filled(col * self.cell_size * SCALE + self.cell_size * SCALE // 2,
                                                      row * self.cell_size * SCALE + self.cell_size * SCALE // 2, 5,
                                                      arcade.color.RED)
        self.batch = Batch()
        self.batch2 = Batch()
        if self.turn == 0:
            self.silver1 = arcade.Text(f"{self.team1_par["silver"]}",
                                       26,
                                       SCREEN_HEIGHT - 13,
                                       arcade.color.SILVER, 18,
                                       anchor_x="left", anchor_y="center", batch=self.batch2)
            self.xp1 = arcade.Text(f"{self.team1_par["xp"]}",
                                   26,
                                   SCREEN_HEIGHT - 43,
                                   arcade.color.GOLD, 18,
                                   anchor_x="left", anchor_y="center", batch=self.batch2)
        else:
            self.silver2 = arcade.Text(f"{self.team2_par["silver"]}",
                                       26,
                                       SCREEN_HEIGHT - 13,
                                       arcade.color.SILVER, 18,
                                       anchor_x="left", anchor_y="center", batch=self.batch2)
            self.xp2 = arcade.Text(f"{self.team2_par["xp"]}",
                                   26,
                                   SCREEN_HEIGHT - 43,
                                   arcade.color.GOLD, 18,
                                   anchor_x="left", anchor_y="center", batch=self.batch2)
        for i, k in enumerate(self.texts):
            text, r, c = k
            tank = self.grid[r][c][-1]
            if tank in self.turn_sl[self.turn][0]:
                text = arcade.Text(f"{tank.health}/{tank.init_health}",
                                   tank.center_x,
                                   tank.center_y + self.cell_size * SCALE // 4,
                                   text.color, 7 * SCALE,
                                   anchor_x="center", batch=self.batch)
                self.texts[i] = (text, r, c)
            else:
                if tank.look:
                    text = arcade.Text(f"{tank.health}/{tank.init_health}",
                                       tank.center_x,
                                       tank.center_y + self.cell_size * SCALE // 4,
                                       text.color, 7 * SCALE,
                                       anchor_x="center", batch=self.batch)
                    self.texts[i] = (text, r, c)
        self.batch.draw()
        self.gui_camera.use()
        self.par.draw()
        self.buttons.draw()
        cy = self.height // 10 * 9
        cx = self.width // 2
        if self.red_capture:
            arcade.draw_rect_filled(arcade.rect.XYWH(cx, cy, 300, 20), arcade.color.GRAY)
            arcade.draw_rect_filled(arcade.rect.LBWH(cx - 150, cy - 10, 300 * self.team1_par["capture"] // 100, 20), arcade.color.RED)
            cy = self.height // 8 * 7 - 20
        if self.green_capture:
            arcade.draw_rect_filled(arcade.rect.XYWH(cx, cy, 300, 20), arcade.color.GRAY)
            arcade.draw_rect_filled(arcade.rect.LBWH(cx - 150, cy - 10, 300 * self.team2_par["capture"] // 100, 20), arcade.color.BOTTLE_GREEN)
        self.batch2.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if arcade.get_sprites_at_point((x, y), self.buttons):
            b = arcade.get_sprites_at_point((x, y), self.buttons)
            if self.buttons[1] in b:
                self.angar()
            elif self.buttons[0] in b:
                t = True
                self.turn_sl[self.turn][1]["silver"] += 300000
                self.turn_sl[self.turn][1]["xp"] += 10000
                self.turn = (self.turn + 1) % 2
                if self.turn == 0:
                    for tank in self.team1:
                        tank.upd()
                    if self.team2_par["capture"] >= 100:
                        game_view = Menu()
                        self.window.show_view(game_view)
                        t = False
                    if self.red_capture:
                        self.team1_par["capture"] += 20
                else:
                    for tank in self.team2:
                        tank.upd()
                    if self.team1_par["capture"] >= 100:
                        game_view = Menu()
                        self.window.show_view(game_view)
                        t = False
                    if self.green_capture:
                        self.team2_par["capture"] += 20
                self.ismoving = False
                if t:
                    game_view = NextTurn(f"Игрок {self.turn + 1}", self)
                    self.window.show_view(game_view)
        else:
            row, col = (int((x + self.world_camera.position[0] - self.width // 2) // (self.cell_size * SCALE)),
                        int((y + self.world_camera.position[1] - self.height // 2) // (self.cell_size * SCALE)))
            m = self.grid[row][col]
            if len(m) > 2:
                if not self.ismoving:
                    if self.grid[row][col][-1] in self.turn_sl[self.turn][0]:
                        if not self.grid[row][col][-1].was_attack:
                            self.x1, self.y1 = row, col
                            self.ismoving = True
                elif self.ismoving and not (row == self.x1 and col == self.y1):
                    if self.grid[row][col][-1] in self.turn_sl[(self.turn + 1) % 2][0] and self.grid[row][col][-1].look:
                        if not self.grid[self.x1][self.y1][-1].was_attack:
                            self.ismoving = False
                            tank1 = self.grid[self.x1][self.y1][-1]
                            tank2 = self.grid[row][col][-1]
                            k = tank1.shot(tank2)
                            if len(k) == 4:
                                if tank1 in self.team1:
                                    self.team1_par["silver"] += k[1]
                                    self.team1_par["xp"] += k[0]
                                if tank1 in self.team2:
                                    self.team2_par["silver"] += k[1]
                                    self.team2_par["xp"] += k[0]
                                if tank2.health == 0:
                                    self.grid[tank2.row][tank2.col].pop()
                                    texts = []
                                    for text, r, c in self.texts:
                                        if not (r == row and c == col):
                                            texts.append((text, r, c))
                                    self.texts = texts[:]
                                    tank2.remove_from_sprite_lists()
                                print(k[3])
                            else:
                                if k != (False, False, False):
                                    print(k)
                                else:
                                    self.ismoving = True
                    elif self.grid[row][col][-1] in self.turn_sl[(self.turn + 1) % 2][0] and not self.grid[row][col][-1].look:
                        if not self.grid[self.x1][self.y1][-1].was_move:
                            self.ismoving = False
                            tank = self.grid[self.x1][self.y1][-1]
                            if not tank.was_move:
                                res = tank.move(row, col, self.cell_size * SCALE, self.grid)
                                if res:
                                    for i, k in enumerate(self.texts):
                                        text, r, c = k
                                        if r == self.x1 and c == self.y1:
                                            text = arcade.Text(f"{tank.health}/{tank.init_health}",
                                                               tank.center_x,
                                                               tank.center_y + self.cell_size * SCALE // 4,
                                                               text.color, 7 * SCALE,
                                                               anchor_x="center", batch=self.batch)
                                            c = tank.col
                                            r = tank.row
                                        self.texts[i] = (text, r, c)
                                    self.grid[tank.row][tank.col].append(self.grid[self.x1][self.y1].pop())
                                self.ismoving = False
                                if not self.ismoving:
                                    if self.grid[tank.row][tank.col][-1] in self.turn_sl[self.turn][0]:
                                        if not self.grid[tank.row][tank.col][-1].was_attack:
                                            self.x1, self.y1 = tank.row, tank.col
                                            self.ismoving = True
                    else:
                        self.x1, self.y1 = row, col
                else:
                    self.ismoving = False
            else:
                if self.ismoving:
                    tank = self.grid[self.x1][self.y1][-1]
                    if not tank.was_move:
                        res = tank.move(row, col, self.cell_size * SCALE, self.grid)
                        if res:
                            for i, k in enumerate(self.texts):
                                text, r, c = k
                                if r == self.x1 and c == self.y1:
                                    text = arcade.Text(f"{tank.health}/{tank.init_health}",
                                                       tank.center_x,
                                                       tank.center_y + self.cell_size * SCALE // 4,
                                                       text.color, 7 * SCALE,
                                                       anchor_x="center", batch=self.batch)
                                    c = tank.col
                                    r = tank.row
                                self.texts[i] = (text, r, c)
                            self.grid[tank.row][tank.col].append(self.grid[self.x1][self.y1].pop())
                        self.ismoving = False
                        if not self.ismoving:
                            if self.grid[tank.row][tank.col][-1] in self.turn_sl[self.turn][0]:
                                if not self.grid[tank.row][tank.col][-1].was_attack:
                                    self.x1, self.y1 = tank.row, tank.col
                                    self.ismoving = True

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        global SCALE
        SCALE += scroll_y / 10
        SCALE = min(max(1, SCALE), 4)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x1 = max(self.width // 2,
                 min(self.world_camera.position[0] - dx, self.cell_size * SCALE * self.rows - self.width // 2))
        y1 = max(self.height // 2,
                 min(self.world_camera.position[1] - dy, self.cell_size * SCALE * self.cols - self.height // 2))
        self.world_camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
            self.world_camera.position,
            (x1, y1),
            0.7  # Плавность следования камеры
        )

    def on_update(self, delta_time):
        x1 = max(self.width // 2,
                 min(self.world_camera.position[0], self.cell_size * SCALE * self.rows - self.width // 2))
        y1 = max(self.height // 2,
                 min(self.world_camera.position[1], self.cell_size * SCALE * self.cols - self.height // 2))
        self.world_camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
            self.world_camera.position,
            (x1, y1),
            0.7  # Плавность следования камеры
        )
        if len(self.grid[self.green_row][self.green_col]) > 2:
            tank = self.grid[self.green_row][self.green_col][-1]
            if tank in self.team1:
                self.green_capture = True
        else:
            self.green_capture = False
            self.team2_par["capture"] = 0
        if len(self.grid[self.red_row][self.red_col]) > 2:
            tank = self.grid[self.red_row][self.red_col][-1]
            if tank in self.team2:
                self.red_capture = True
        else:
            self.red_capture = False
            self.team1_par["capture"] = 0


class UpgradeOrBuyTank(arcade.View):
    def __init__(self, team_upg, silver, xp, svoboda, color, game_view):
        super().__init__()
        self.team_upg = team_upg
        self.color = color
        self.silver = silver
        self.xp = xp
        self.texture = arcade.load_texture("images/angar1.jpg")
        self.game_view = game_view
        self.button = arcade.SpriteList()
        self.krest = arcade.Sprite("images/krest.png", scale=0.04)
        self.krest.center_x = SCREEN_WIDTH - self.krest.width // 2 - 3
        self.krest.center_y = SCREEN_HEIGHT - self.krest.height // 2 - 3
        self.button.append(self.krest)
        self.left = arcade.Sprite("images/next_button.bmp")
        self.left.center_x = self.left.width // 2 + 3
        self.left.center_y = SCREEN_HEIGHT // 2
        self.button.append(self.left)
        self.left = arcade.Sprite("images/next_button.bmp", angle=180)
        self.left.center_x = SCREEN_WIDTH - self.left.width // 2 - 3
        self.left.center_y = SCREEN_HEIGHT // 2
        self.button.append(self.left)
        self.svoboda = svoboda
        self.index = 0
        self.balance = arcade.SpriteList()
        self.batch = Batch()
        s1 = arcade.Sprite("images/silver.bmp", scale=0.08)
        s1.center_x = 13
        s1.center_y = SCREEN_HEIGHT - 13
        self.balance.append(s1)
        xp1 = arcade.Sprite("images/xp.bmp", scale=0.21)
        xp1.center_x = 13
        xp1.center_y = SCREEN_HEIGHT - 43
        self.balance.append(xp1)

    def on_draw(self):
        arcade.draw_texture_rect(self.texture,
                                 arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height))
        self.button.draw()
        sp_l = arcade.SpriteList()
        m = TANKS[list(TANKS.keys())[self.index % len(TANKS)]]
        sp_l.append(arcade.Sprite(m[0], scale=m[-1] * 10))
        sp_l[0].center_x = self.width // 2
        sp_l[0].center_y = self.height // 2
        sp_l.draw()
        arcade.draw_rect_filled(arcade.rect.XYWH(SCREEN_WIDTH // 2, 30, 200, 40), arcade.color.DIM_GRAY)
        arcade.draw_rect_outline(arcade.rect.XYWH(SCREEN_WIDTH // 2, 30, 200, 40), arcade.color.BLACK, 2)
        tank = tanks.Tank(list(TANKS.keys())[self.index % len(TANKS)],
                          *TANKS[list(TANKS.keys())[self.index % len(TANKS)]])
        cost = tank.cost
        xp = tank.xp
        self.par = arcade.SpriteList()
        if list(TANKS.keys())[self.index % len(TANKS)] in self.team_upg:
            self.batch = Batch()
            text = arcade.Text(f"{cost}",
                               SCREEN_WIDTH // 2, 30,
                               arcade.color.LIGHT_GRAY, 17,
                               anchor_x="center", anchor_y="center", batch=self.batch)
            s1 = arcade.Sprite("images/silver.bmp", scale=0.08)
            s1.center_x = SCREEN_WIDTH // 2 + 100 - 33
            s1.center_y = 30
            self.par.append(s1)
        else:
            self.batch = Batch()
            text = arcade.Text(f"{xp}", SCREEN_WIDTH // 2, 30,
                               arcade.color.GOLD, 17,
                               anchor_x="center", anchor_y="center", batch=self.batch)
            xp1 = arcade.Sprite("images/xp.bmp", scale=0.21)
            xp1.center_x = SCREEN_WIDTH // 2 + 100 - 33
            xp1.center_y = 30
            self.par.append(xp1)
        silver1 = arcade.Text(f"{self.silver}",
                              26,
                              SCREEN_HEIGHT - 13,
                              arcade.color.SILVER, 18,
                              anchor_x="left", anchor_y="center", batch=self.batch)
        xp1 = arcade.Text(f"{self.xp}",
                          26,
                          SCREEN_HEIGHT - 43,
                          arcade.color.GOLD, 18,
                          anchor_x="left", anchor_y="center", batch=self.batch)
        self.batch.draw()
        self.par.draw()
        self.balance.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if arcade.get_sprites_at_point((x, y), self.button):
            b = arcade.get_sprites_at_point((x, y), self.button)
            if self.button[0] in b:
                self.game_view.turn_sl[self.game_view.turn][1]["silver"] = self.silver
                self.game_view.turn_sl[self.game_view.turn][1]["xp"] = self.xp
                self.window.show_view(self.game_view)
            if self.button[1] in b:
                self.index -= 1
            if self.button[2] in b:
                self.index += 1
        else:
            if SCREEN_WIDTH // 2 - 100 <= x <= SCREEN_WIDTH // 2 + 100 and 10 <= y <= 50:
                if list(TANKS.keys())[self.index % len(TANKS)] in self.team_upg:
                    tank = tanks.Tank(list(TANKS.keys())[self.index % len(TANKS)],
                                      *TANKS[list(TANKS.keys())[self.index % len(TANKS)]])
                    tank.was_move = True
                    tank.was_attack = True
                    if self.silver >= tank.cost and self.svoboda:
                        self.silver -= tank.cost
                        self.svoboda = False
                        if self.game_view.turn == 0:
                            tank.center_x = self.game_view.cell_size // 2 * SCALE + self.game_view.red_row * self.game_view.cell_size * SCALE
                            tank.center_y = self.game_view.cell_size // 2 * SCALE + self.game_view.red_col * self.game_view.cell_size * SCALE
                            tank.row = self.game_view.red_row
                            tank.col = self.game_view.red_col
                            self.game_view.texts.append((arcade.Text(f"{tank.init_health}/{tank.health}",
                                                                     self.game_view.cell_size * SCALE // 2 * self.game_view.red_row,
                                                                     self.game_view.cell_size * SCALE // 2 * self.game_view.red_col,
                                                                     self.color, 7 * SCALE,
                                                                     anchor_x="center", batch=self.batch),
                                                         self.game_view.red_row, self.game_view.red_col))
                            self.game_view.team1.append(tank)
                            self.game_view.grid[self.game_view.red_row][self.game_view.red_col].append(tank)
                        else:
                            tank.center_x = self.game_view.cell_size // 2 * SCALE + self.game_view.green_row * self.game_view.cell_size * SCALE
                            tank.center_y = self.game_view.cell_size // 2 * SCALE + self.game_view.green_col * self.game_view.cell_size * SCALE
                            tank.row = self.game_view.green_row
                            tank.col = self.game_view.green_col
                            self.game_view.texts.append((arcade.Text(f"{tank.init_health}/{tank.health}",
                                                                     self.game_view.cell_size // 2 * SCALE + self.game_view.green_row * self.game_view.cell_size * SCALE,
                                                                     self.game_view.cell_size // 2 * SCALE + self.game_view.green_col * self.game_view.cell_size * SCALE,
                                                                     self.color, 7 * SCALE,
                                                                     anchor_x="center", batch=self.batch),
                                                         self.game_view.green_row, self.game_view.green_col))
                            self.game_view.team2.append(tank)
                            self.game_view.grid[self.game_view.green_row][self.game_view.green_col].append(tank)
                else:
                    tank = tanks.Tank(list(TANKS.keys())[self.index % len(TANKS)],
                                      *TANKS[list(TANKS.keys())[self.index % len(TANKS)]])
                    if self.xp >= tank.xp:
                        self.xp -= tank.xp
                        if self.game_view.turn == 0:
                            self.game_view.team1_up.append(tank.name)
                        else:
                            self.game_view.team2_up.append(tank.name)


class NextTurn(arcade.View):
    def __init__(self, button_text, game_view):
        self.game_view = game_view
        super().__init__()
        self.texture = arcade.load_texture(f"images/texture{random.randint(1, 4)}.jpg")
        self.button_text = button_text
        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout()  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)  # Вертикальный стек

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager

    def setup_widgets(self):
        flat_button = UIFlatButton(text=self.button_text, width=200, height=50, color=arcade.color.BLUE)
        flat_button.on_click = lambda event: self.ret()  # Не только лямбду, конечно
        self.box_layout.add(flat_button)

    def on_draw(self):
        arcade.draw_texture_rect(self.texture,
                                 arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height))
        self.manager.draw()

    def ret(self):  # Создаём игровой вид
        self.window.show_view(self.game_view)


class Menu(arcade.View):
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture(f"images/menu{random.randint(1, 2)}.jpg")
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout()  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=True, space_between=10, align="top")  # Вертикальный стек

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager

    def setup_widgets(self):
        flat_button = UIFlatButton(text="В БОЙ", width=200, height=50, color=arcade.color.RED)
        flat_button.on_click = lambda event: self.fight()  # Не только лямбду, конечно
        self.box_layout.add(flat_button)

    def fight(self):
        game_view = GameWindow()
        self.window.show_view(game_view)

    def on_draw(self):
        arcade.draw_texture_rect(self.texture,
                                 arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height))
        self.manager.draw()


class WinView(arcade.View):
    pass


def main():
    window = arcade.Window(1200, 800, "My game")
    game_view = Menu()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
