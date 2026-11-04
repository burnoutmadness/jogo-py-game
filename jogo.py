import pygame
import random
import colorsys
import json
import os

# Initialize Pygame
pygame.init()

# Game Constants (Expanded Aspect Ratio Layout)
SCREEN_WIDTH = 600  
SCREEN_HEIGHT = 500
GRID_SIZE = 20
COLUMNS = 10
ROWS = 20
GAME_WIDTH = COLUMNS * GRID_SIZE
GAME_HEIGHT = ROWS * GRID_SIZE

# Stats & Settings File Persistence
STATS_FILE = "tetris_stats.json"

DEFAULT_CONTROLS = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "down": pygame.K_DOWN,
    "rotate": pygame.K_UP,
    "drop": pygame.K_SPACE
}

def load_stats():
    default_data = {
        "classic": {"high_score": 0, "max_time": 0},
        "dynamic": {"high_score": 0, "max_time": 0},
        "controls": DEFAULT_CONTROLS.copy(),
        "rainbow_mode": False,
        "bg_animation": True,
        "theme": "light"
    }
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                data = json.load(f)
                if "classic" not in data or "dynamic" not in data:
                    old_hs = data.get("high_score", 0)
                    old_mt = data.get("max_time", 0)
                    data = default_data.copy()
                    data["classic"]["high_score"] = old_hs
                    data["classic"]["max_time"] = old_mt
                if "controls" not in data:
                    data["controls"] = DEFAULT_CONTROLS.copy()
                if "rainbow_mode" not in data:
                    data["rainbow_mode"] = False
                if "bg_animation" not in data:
                    data["bg_animation"] = True
                if "theme" not in data:
                    data["theme"] = "light"
                return data
        except:
            pass
    return default_data

def save_stats(stats):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f)
    except:
        pass

# Expanded Vibrant Color Palette
COLORS = [
    (0, 229, 255),   # Bright Electric Cyan
    (255, 230, 0),   # Vivid Sunny Yellow
    (180, 50, 235),  # Electric Purple
    (0, 230, 118),   # Neon Mint Green
    (255, 45, 85),   # Hot Pink / Red
    (41, 121, 255),  # Deep Azure Blue
    (255, 145, 0),   # Vibrant Orange
    (255, 64, 129),  # Magenta Pink
    (100, 221, 23),  # Lime Green
    (140, 158, 255)  # Periwinkle Blue
]

# Theme Definitions
LIGHT_THEME = {
    "BG": (250, 250, 252),
    "TEXT": (40, 40, 50),
    "VAL_TEXT": (10, 10, 20),
    "GRID_LINE": (230, 230, 235),
    "BOARD_BORDER": (60, 60, 70),
    "CARD_BG": (255, 255, 255),
    "CARD_BORDER": (210, 210, 220),
    "SHADOW_FILL": (235, 235, 240),
    "SHADOW_BORDER": (160, 160, 170),
    "DECO": (240, 240, 245),
    "OUTLINE": (200, 200, 210),
    "NAME": "Light Mode"
}

DARK_THEME = {
    "BG": (20, 20, 25),
    "TEXT": (210, 210, 220),
    "VAL_TEXT": (255, 255, 255),
    "GRID_LINE": (35, 35, 45),
    "BOARD_BORDER": (140, 140, 150),
    "CARD_BG": (30, 30, 38),
    "CARD_BORDER": (55, 55, 70),
    "SHADOW_FILL": (45, 45, 55),
    "SHADOW_BORDER": (100, 100, 115),
    "DECO": (26, 26, 34),
    "OUTLINE": (10, 10, 15),
    "NAME": "Dark Mode"
}

current_theme = LIGHT_THEME

# Button styling colors for Settings
BUTTON_COLOR = (0, 150, 215)
BUTTON_HOVER = (0, 180, 245)

# Tetromino Shapes
SHAPES = [
    [[1, 1, 1, 1]], # I
    [[1, 1], [1, 1]], # O
    [[0, 1, 0], [1, 1, 1]], # T
    [[0, 1, 1], [1, 1, 0]], # S
    [[1, 1, 0], [0, 1, 1]], # Z
    [[1, 0, 0], [1, 1, 1]], # J
    [[0, 0, 1], [1, 1, 1]]  # L
]

def get_rainbow_color(offset=0):
    """Generates a dynamic RGB color based on current time."""
    hue = ((pygame.time.get_ticks() + offset) % 3000) / 3000.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
    return (int(r * 255), int(g * 255), int(b * 255))

class MenuPiece:
    def __init__(self, assigned_x):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = assigned_x
        self.y = random.randint(-350, -50)
        self.speed = random.uniform(0.06, 0.12)

    def update(self, delta_time):
        self.y += self.speed * delta_time
        if self.y > SCREEN_HEIGHT + 50:
            self.y = random.randint(-350, -50)
            self.shape = random.choice(SHAPES)
            self.color = random.choice(COLORS)
            self.speed = random.uniform(0.06, 0.12)

    def draw(self, surface):
        for r, row in enumerate(self.shape):
            for c, cell in enumerate(row):
                if cell:
                    px = self.x + c * 18
                    py = self.y + r * 18
                    if py > -30:
                        pygame.draw.rect(surface, self.color, (px, py, 18, 18), 0)
                        pygame.draw.rect(surface, current_theme["BOARD_BORDER"], (px, py, 18, 18), 1)

class Tetromino:
    def __init__(self, x, y, shape, rainbow_mode):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rainbow_mode = rainbow_mode

    def image(self):
        return self.shape

    def get_color(self):
        if self.rainbow_mode:
            return get_rainbow_color()
        return self.color

    def rotate(self):
        self.shape = [list(x) for x in zip(*self.shape[::-1])]

class Tetris:
    def __init__(self, is_dynamic=False, rainbow_mode=False):
        self.grid = [[current_theme["BG"] for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.score = 0
        self.lines_cleared_total = 0
        self.is_dynamic = is_dynamic
        self.rainbow_mode = rainbow_mode
        self.game_over = False
        self.game_over_animating = False
        self.anim_row = ROWS - 1
        self.anim_timer = 0
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        
        self.clearing_rows = []
        self.clear_anim_timer = 0
        self.combo_count = 0
        self.popup_text = ""
        self.popup_timer = 0

    def get_current_fall_speed(self):
        base_speed = 500
        if self.is_dynamic:
            speed = 500 - (self.lines_cleared_total * 35)
            return max(100, speed)
        return base_speed

    def new_piece(self):
        shape = random.choice(SHAPES)
        return Tetromino(COLUMNS // 2 - len(shape[0]) // 2, 0, shape, self.rainbow_mode)

    def intersects(self):
        for r, row in enumerate(self.current_piece.image()):
            for c, cell in enumerate(row):
                if cell:
                    next_r = r + self.current_piece.y
                    next_c = c + self.current_piece.x
                    if (next_r >= ROWS or next_c < 0 or next_c >= COLUMNS or 
                            (next_r >= 0 and self.grid[next_r][next_c] != current_theme["BG"])):
                        return True
        return False

    def get_shadow_y(self):
        orig_y = self.current_piece.y
        while not self.intersects():
            self.current_piece.y += 1
        shadow_y = self.current_piece.y - 1
        self.current_piece.y = orig_y
        return shadow_y

    def lock_piece(self):
        piece_color = self.current_piece.get_color()
        for r, row in enumerate(self.current_piece.image()):
            for c, cell in enumerate(row):
                if cell:
                    if self.current_piece.y + r < 0:
                        self.trigger_game_over()
                        return
                    self.grid[self.current_piece.y + r][self.current_piece.x + c] = piece_color
        self.check_lines()

    def trigger_game_over(self):
        self.game_over_animating = True
        self.anim_row = ROWS - 1
        self.anim_timer = pygame.time.get_ticks()

    def update_game_over_animation(self):
        if self.game_over_animating:
            if pygame.time.get_ticks() - self.anim_timer >= 30:
                if self.anim_row >= 0:
                    self.grid[self.anim_row] = [current_theme["BG"] for _ in range(COLUMNS)]
                    self.anim_row -= 1
                    self.anim_timer = pygame.time.get_ticks()
                else:
                    self.game_over_animating = False
                    self.game_over = True
            return True
        return False

    def check_lines(self):
        full_rows = []
        for r in range(ROWS):
            if all(cell != current_theme["BG"] for cell in self.grid[r]):
                full_rows.append(r)

        if full_rows:
            self.clearing_rows = full_rows
            self.clear_anim_timer = pygame.time.get_ticks()
        else:
            self.combo_count = 0
            self.spawn_next_piece()

    def update_clear_animation(self):
        if self.clearing_rows:
            if pygame.time.get_ticks() - self.clear_anim_timer >= 150:
                lines_cleared = len(self.clearing_rows)
                for r in self.clearing_rows:
                    del self.grid[r]
                    self.grid.insert(0, [current_theme["BG"] for _ in range(COLUMNS)])
                
                self.score += (lines_cleared ** 2) * 100
                self.lines_cleared_total += lines_cleared
                
                self.combo_count += 1
                if lines_cleared == 1:
                    self.popup_text = "single!"
                elif lines_cleared == 2:
                    self.popup_text = "double!"
                elif lines_cleared == 3:
                    self.popup_text = "triple!"
                elif lines_cleared >= 4:
                    self.popup_text = "tetris!"

                if self.combo_count > 1:
                    self.popup_text += f" (combo x{self.combo_count})"

                self.popup_timer = pygame.time.get_ticks()
                self.clearing_rows = []
                self.spawn_next_piece()
            return True
        return False

    def spawn_next_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if self.intersects():
            self.trigger_game_over()

    def clear_lines(self):
        pass

    def move_side(self, dx):
        self.current_piece.x += dx
        if self.intersects():
            self.current_piece.x -= dx

    def drop(self):
        self.current_piece.y += 1
        if self.intersects():
            self.current_piece.y -= 1
            self.lock_piece()

    def rotate(self):
        old_shape = self.current_piece.shape
        self.current_piece.rotate()
        if self.intersects():
            self.current_piece.shape = old_shape

def draw_grid(surface, grid, clearing_rows=[]):
    for r in range(ROWS):
        for c in range(COLUMNS):
            cell_color = (255, 255, 255) if r in clearing_rows else grid[r][c]
            pygame.draw.rect(surface, cell_color, (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
            pygame.draw.rect(surface, current_theme["GRID_LINE"], (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

def draw_outlined_text(surface, text, font, text_color, outline_color, center_x, center_y):
    """Helper to render text with an outline."""
    offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]
    for ox, oy in offsets:
        outline_surf = font.render(text, True, outline_color)
        outline_rect = outline_surf.get_rect(center=(center_x + ox, center_y + oy))
        surface.blit(outline_surf, outline_rect)
    
    main_surf = font.render(text, True, text_color)
    main_rect = main_surf.get_rect(center=(center_x, center_y))
    surface.blit(main_surf, main_rect)

def main():
    global current_theme
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("tetris")
    clock = pygame.time.Clock()

    game_state = "MENU"  # Can be "MENU", "MODE_SELECT", "STATS", "SETTINGS", "CONTROLS", or "PLAYING"
    game = None
    game_time = 0

    # Load saved stats and settings
    stats = load_stats()
    current_theme = DARK_THEME if stats.get("theme") == "dark" else LIGHT_THEME
    remapping_key = None

    # Distinct vertical lanes on the left and right margins
    lane_x_positions = [40, 90, 450, 500]
    menu_pieces = [MenuPiece(x) for x in lane_x_positions]

    fall_time = 0

    key_timers = {"left": 0, "right": 0, "down": 0}
    DAS_DELAY = 180      
    DAS_INTERVAL = 45    

    font = pygame.font.SysFont('Arial', 18, bold=True)
    font_small = pygame.font.SysFont('Arial', 16, bold=True)
    font_popup = pygame.font.SysFont('Arial', 18, bold=True)
    font_large = pygame.font.SysFont('Arial', 22, bold=True)
    font_title = pygame.font.SysFont('Arial', 60, bold=True)

    # Main Menu Buttons (4 buttons spaced evenly)
    play_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 180, 220, 36)
    stats_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 225, 220, 36)
    settings_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 270, 220, 36)
    quit_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 315, 220, 36)

    # Mode Select Buttons
    normal_mode_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 200, 220, 45)
    dynamic_mode_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 260, 220, 45)
    mode_back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 320, 220, 45)

    # Settings Buttons
    controls_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 135, 220, 36)
    theme_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 180, 220, 36)
    rainbow_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 225, 220, 36)
    bg_anim_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 270, 220, 36)
    back_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 325, 220, 36)

    # Controls Screen Action Rects
    control_action_rects = {
        "left": pygame.Rect(SCREEN_WIDTH // 2 + 10, 150, 140, 35),
        "right": pygame.Rect(SCREEN_WIDTH // 2 + 10, 195, 140, 35),
        "down": pygame.Rect(SCREEN_WIDTH // 2 + 10, 240, 140, 35),
        "rotate": pygame.Rect(SCREEN_WIDTH // 2 + 10, 285, 140, 35),
        "drop": pygame.Rect(SCREEN_WIDTH // 2 + 10, 330, 140, 35)
    }
    controls_back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 395, 220, 40)

    # Stats Back Button
    stats_back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, 435, 220, 40)

    running = True
    while running:
        delta_time = clock.tick(60)

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_btn_rect.collidepoint(event.pos):
                        game_state = "MODE_SELECT"
                    elif stats_btn_rect.collidepoint(event.pos):
                        game_state = "STATS"
                    elif settings_btn_rect.collidepoint(event.pos):
                        game_state = "SETTINGS"
                    elif quit_btn_rect.collidepoint(event.pos):
                        running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game_state = "MODE_SELECT"

            elif game_state == "MODE_SELECT":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if normal_mode_btn_rect.collidepoint(event.pos):
                        game = Tetris(is_dynamic=False, rainbow_mode=stats["rainbow_mode"])
                        game_time = 0
                        game_state = "PLAYING"
                    elif dynamic_mode_btn_rect.collidepoint(event.pos):
                        game = Tetris(is_dynamic=True, rainbow_mode=stats["rainbow_mode"])
                        game_time = 0
                        game_state = "PLAYING"
                    elif mode_back_rect.collidepoint(event.pos):
                        game_state = "MENU"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = "MENU"

            elif game_state == "STATS":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if stats_back_rect.collidepoint(event.pos):
                        game_state = "MENU"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = "MENU"

            elif game_state == "SETTINGS":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if controls_btn_rect.collidepoint(event.pos):
                        game_state = "CONTROLS"
                    elif theme_btn_rect.collidepoint(event.pos):
                        if current_theme == LIGHT_THEME:
                            current_theme = DARK_THEME
                            stats["theme"] = "dark"
                        else:
                            current_theme = LIGHT_THEME
                            stats["theme"] = "light"
                        save_stats(stats)
                    elif rainbow_btn_rect.collidepoint(event.pos):
                        stats["rainbow_mode"] = not stats["rainbow_mode"]
                        save_stats(stats)
                    elif bg_anim_btn_rect.collidepoint(event.pos):
                        stats["bg_animation"] = not stats["bg_animation"]
                        save_stats(stats)
                    elif back_btn_rect.collidepoint(event.pos):
                        game_state = "MENU"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = "MENU"

            elif game_state == "CONTROLS":
                if remapping_key is not None:
                    if event.type == pygame.KEYDOWN:
                        if event.key != pygame.K_ESCAPE:
                            stats["controls"][remapping_key] = event.key
                            save_stats(stats)
                        remapping_key = None
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if controls_back_rect.collidepoint(event.pos):
                            game_state = "SETTINGS"
                        else:
                            for action, rect in control_action_rects.items():
                                if rect.collidepoint(event.pos):
                                    remapping_key = action
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            game_state = "SETTINGS"

            elif game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if not game.game_over and not game.game_over_animating and not game.clearing_rows:
                        if event.key == stats["controls"]["rotate"]:
                            game.rotate()
                        elif event.key == stats["controls"]["drop"]:
                            while not game.intersects():
                                game.current_piece.y += 1
                            game.current_piece.y -= 1
                            game.lock_piece()
                    else:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE) and game.game_over:
                            is_dyn = game.is_dynamic
                            game = Tetris(is_dynamic=is_dyn, rainbow_mode=stats["rainbow_mode"])
                            game_time = 0
                        elif event.key == pygame.K_ESCAPE:
                            game_state = "MENU"

        # --- GAME UPDATE LOGIC ---
        if game_state in ("MENU", "MODE_SELECT"):
            if stats["bg_animation"]:
                for p in menu_pieces:
                    p.update(delta_time)

        elif game_state == "PLAYING":
            if game.game_over_animating:
                game.update_game_over_animation()
                if game.game_over:
                    mode_key = "dynamic" if game.is_dynamic else "classic"
                    updated = False
                    if game.score > stats[mode_key]["high_score"]:
                        stats[mode_key]["high_score"] = game.score
                        updated = True
                    if game_time > stats[mode_key]["max_time"]:
                        stats[mode_key]["max_time"] = game_time
                        updated = True
                    if updated:
                        save_stats(stats)
            elif not game.game_over:
                if game.update_clear_animation():
                    fall_time = 0
                else:
                    game_time += delta_time
                    fall_time += delta_time
                    current_fall_speed = game.get_current_fall_speed()
                    if fall_time >= current_fall_speed:
                        game.drop()
                        fall_time = 0

                    keys = pygame.key.get_pressed()
                    if not game.clearing_rows:
                        if keys[stats["controls"]["left"]]:
                            if key_timers["left"] == 0:
                                game.move_side(-1)
                            key_timers["left"] += delta_time
                            if key_timers["left"] >= DAS_DELAY:
                                if key_timers["left"] >= DAS_DELAY + DAS_INTERVAL:
                                    game.move_side(-1)
                                    key_timers["left"] = DAS_DELAY
                        else:
                            key_timers["left"] = 0

                        if keys[stats["controls"]["right"]]:
                            if key_timers["right"] == 0:
                                game.move_side(1)
                            key_timers["right"] += delta_time
                            if key_timers["right"] >= DAS_DELAY:
                                if key_timers["right"] >= DAS_DELAY + DAS_INTERVAL:
                                    game.move_side(1)
                                    key_timers["right"] = DAS_DELAY
                        else:
                            key_timers["right"] = 0

                        if keys[stats["controls"]["down"]]:
                            if key_timers["down"] == 0:
                                game.drop()
                                fall_time = 0
                            key_timers["down"] += delta_time
                            if key_timers["down"] >= DAS_INTERVAL:
                                game.drop()
                                fall_time = 0
                                key_timers["down"] = 0
                        else:
                            key_timers["down"] = 0

        # --- RENDERING ---
        screen.fill(current_theme["BG"])
        mouse_pos = pygame.mouse.get_pos()

        if game_state in ("MENU", "MODE_SELECT"):
            if stats["bg_animation"]:
                for p in menu_pieces:
                    p.draw(screen)

            draw_outlined_text(
                screen, "tetris", font_title, 
                current_theme["VAL_TEXT"], current_theme["OUTLINE"], 
                SCREEN_WIDTH // 2, 90
            )

            sub_label = font_small.render("A Classic Block Puzzle Experience", True, current_theme["TEXT"])
            sub_rect = sub_label.get_rect(center=(SCREEN_WIDTH // 2, 140))
            screen.blit(sub_label, sub_rect)

            if game_state == "MENU":
                rainbow_btn_color = get_rainbow_color()

                # Play Button
                pygame.draw.rect(screen, rainbow_btn_color, play_btn_rect, border_radius=12)
                pygame.draw.rect(screen, current_theme["TEXT"], play_btn_rect, 2, border_radius=12)
                play_text = font_large.render("PLAY", True, (255, 255, 255))
                screen.blit(play_text, play_text.get_rect(center=play_btn_rect.center))

                # Stats Button
                stats_color = BUTTON_HOVER if stats_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
                pygame.draw.rect(screen, stats_color, stats_btn_rect, border_radius=12)
                pygame.draw.rect(screen, current_theme["TEXT"], stats_btn_rect, 2, border_radius=12)
                stats_text = font.render("STATS", True, (255, 255, 255))
                screen.blit(stats_text, stats_text.get_rect(center=stats_btn_rect.center))

                # Settings Button
                settings_color = BUTTON_HOVER if settings_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
                pygame.draw.rect(screen, settings_color, settings_btn_rect, border_radius=12)
                pygame.draw.rect(screen, current_theme["TEXT"], settings_btn_rect, 2, border_radius=12)
                settings_text = font.render("SETTINGS", True, (255, 255, 255))
                screen.blit(settings_text, settings_text.get_rect(center=settings_btn_rect.center))

                # Quit Button
                quit_color = BUTTON_HOVER if quit_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
                pygame.draw.rect(screen, quit_color, quit_btn_rect, border_radius=12)
                pygame.draw.rect(screen, current_theme["TEXT"], quit_btn_rect, 2, border_radius=12)
                quit_text = font.render("QUIT", True, (255, 255, 255))
                screen.blit(quit_text, quit_text.get_rect(center=quit_btn_rect.center))

            elif game_state == "MODE_SELECT":
                normal_color = BUTTON_HOVER if normal_mode_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
                pygame.draw.rect(screen, normal_color, normal_mode_btn_rect, border_radius=12)
                pygame.draw.rect(screen, current_theme["TEXT"], normal_mode_btn_rect, 2, border_radius=12)
                normal_text = font.render("NORMAL MODE", True, (255, 255, 255))
                screen.blit(normal_text, normal_text.get_rect(center=normal_mode_btn_rect.center))

                dynamic_color = BUTTON_HOVER if dynamic_mode_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
                pygame.draw.rect(screen, dynamic_color, dynamic_mode_btn_rect, border_radius=12)
                pygame.draw.rect(screen, current_theme["TEXT"], dynamic_mode_btn_rect, 2, border_radius=12)
                dynamic_text = font.render("DYNAMIC MODE", True, (255, 255, 255))
                screen.blit(dynamic_text, dynamic_text.get_rect(center=dynamic_mode_btn_rect.center))

                back_color = BUTTON_HOVER if mode_back_rect.collidepoint(mouse_pos) else BUTTON_COLOR
                pygame.draw.rect(screen, back_color, mode_back_rect, border_radius=12)
                pygame.draw.rect(screen, current_theme["TEXT"], mode_back_rect, 2, border_radius=12)
                back_text = font.render("BACK", True, (255, 255, 255))
                screen.blit(back_text, back_text.get_rect(center=mode_back_rect.center))

        elif game_state == "STATS":
            draw_outlined_text(
                screen, "stats", font_title, 
                current_theme["VAL_TEXT"], current_theme["OUTLINE"], 
                SCREEN_WIDTH // 2, 50
            )

            # Classic Mode Card
            c_card = pygame.Rect(35, 95, 255, 325)
            pygame.draw.rect(screen, current_theme["CARD_BG"], c_card, border_radius=10)
            pygame.draw.rect(screen, current_theme["CARD_BORDER"], c_card, 1, border_radius=10)

            c_title = font.render("CLASSIC MODE", True, current_theme["TEXT"])
            screen.blit(c_title, (c_card.x + 20, c_card.y + 20))

            c_hs_label = font_small.render("High Score", True, current_theme["TEXT"])
            c_hs_val = font_large.render(str(stats["classic"]["high_score"]), True, current_theme["VAL_TEXT"])
            screen.blit(c_hs_label, (c_card.x + 20, c_card.y + 70))
            screen.blit(c_hs_val, (c_card.x + 20, c_card.y + 95))

            c_sec = stats["classic"]["max_time"] // 1000
            c_min = c_sec // 60
            c_s = c_sec % 60
            c_time_str = f"{c_min:02d}:{c_s:02d}"

            c_time_label = font_small.render("Max Play Time", True, current_theme["TEXT"])
            c_time_val = font_large.render(c_time_str, True, current_theme["VAL_TEXT"])
            screen.blit(c_time_label, (c_card.x + 20, c_card.y + 160))
            screen.blit(c_time_val, (c_card.x + 20, c_card.y + 185))

            # Dynamic Mode Card
            d_card = pygame.Rect(310, 95, 255, 325)
            pygame.draw.rect(screen, current_theme["CARD_BG"], d_card, border_radius=10)
            pygame.draw.rect(screen, current_theme["CARD_BORDER"], d_card, 1, border_radius=10)

            d_title = font.render("DYNAMIC MODE", True, current_theme["TEXT"])
            screen.blit(d_title, (d_card.x + 20, d_card.y + 20))

            d_hs_label = font_small.render("High Score", True, current_theme["TEXT"])
            d_hs_val = font_large.render(str(stats["dynamic"]["high_score"]), True, current_theme["VAL_TEXT"])
            screen.blit(d_hs_label, (d_card.x + 20, d_card.y + 70))
            screen.blit(d_hs_val, (d_card.x + 20, d_card.y + 95))

            d_sec = stats["dynamic"]["max_time"] // 1000
            d_min = d_sec // 60
            d_s = d_sec % 60
            d_time_str = f"{d_min:02d}:{d_s:02d}"

            d_time_label = font_small.render("Max Play Time", True, current_theme["TEXT"])
            d_time_val = font_large.render(d_time_str, True, current_theme["VAL_TEXT"])
            screen.blit(d_time_label, (d_card.x + 20, d_card.y + 160))
            screen.blit(d_time_val, (d_card.x + 20, d_card.y + 185))

            back_color = BUTTON_HOVER if stats_back_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, back_color, stats_back_rect, border_radius=12)
            pygame.draw.rect(screen, current_theme["TEXT"], stats_back_rect, 2, border_radius=12)
            back_text = font.render("BACK", True, (255, 255, 255))
            screen.blit(back_text, back_text.get_rect(center=stats_back_rect.center))

        elif game_state == "SETTINGS":
            draw_outlined_text(
                screen, "settings", font_title, 
                current_theme["VAL_TEXT"], current_theme["OUTLINE"], 
                SCREEN_WIDTH // 2, 75
            )

            # Controls Button
            controls_color = BUTTON_HOVER if controls_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, controls_color, controls_btn_rect, border_radius=12)
            pygame.draw.rect(screen, current_theme["TEXT"], controls_btn_rect, 2, border_radius=12)
            controls_text = font.render("CONTROLS", True, (255, 255, 255))
            screen.blit(controls_text, controls_text.get_rect(center=controls_btn_rect.center))

            # Theme Button
            theme_color = BUTTON_HOVER if theme_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, theme_color, theme_btn_rect, border_radius=12)
            pygame.draw.rect(screen, current_theme["TEXT"], theme_btn_rect, 2, border_radius=12)
            theme_text = font.render(current_theme["NAME"], True, (255, 255, 255))
            screen.blit(theme_text, theme_text.get_rect(center=theme_btn_rect.center))

            # Rainbow Toggle Button
            rainbow_status = "Rainbow: ON" if stats["rainbow_mode"] else "Rainbow: OFF"
            rainbow_color_btn = BUTTON_HOVER if rainbow_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, rainbow_color_btn, rainbow_btn_rect, border_radius=12)
            pygame.draw.rect(screen, current_theme["TEXT"], rainbow_btn_rect, 2, border_radius=12)
            rainbow_text = font.render(rainbow_status, True, (255, 255, 255))
            screen.blit(rainbow_text, rainbow_text.get_rect(center=rainbow_btn_rect.center))

            # Background Animation Toggle Button
            bg_status = "BG Anim: ON" if stats["bg_animation"] else "BG Anim: OFF"
            bg_color = BUTTON_HOVER if bg_anim_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, bg_color, bg_anim_btn_rect, border_radius=12)
            pygame.draw.rect(screen, current_theme["TEXT"], bg_anim_btn_rect, 2, border_radius=12)
            bg_text = font.render(bg_status, True, (255, 255, 255))
            screen.blit(bg_text, bg_text.get_rect(center=bg_anim_btn_rect.center))

            # Back Button
            back_color = BUTTON_HOVER if back_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, back_color, back_btn_rect, border_radius=12)
            pygame.draw.rect(screen, current_theme["TEXT"], back_btn_rect, 2, border_radius=12)
            back_text = font.render("BACK", True, (255, 255, 255))
            screen.blit(back_text, back_text.get_rect(center=back_btn_rect.center))

        elif game_state == "CONTROLS":
            draw_outlined_text(
                screen, "controls", font_title, 
                current_theme["VAL_TEXT"], current_theme["OUTLINE"], 
                SCREEN_WIDTH // 2, 85
            )

            labels = [
                ("Move Left", "left"),
                ("Move Right", "right"),
                ("Soft Drop", "down"),
                ("Rotate", "rotate"),
                ("Hard Drop", "drop")
            ]

            y_offset = 150
            for label_text, action in labels:
                lbl = font.render(label_text, True, current_theme["TEXT"])
                screen.blit(lbl, (SCREEN_WIDTH // 2 - 140, y_offset + 7))

                rect = control_action_rects[action]
                is_hovered = rect.collidepoint(mouse_pos)
                btn_col = (230, 80, 80) if remapping_key == action else (BUTTON_HOVER if is_hovered else BUTTON_COLOR)
                
                pygame.draw.rect(screen, btn_col, rect, border_radius=8)
                pygame.draw.rect(screen, current_theme["TEXT"], rect, 2, border_radius=8)

                key_val = stats["controls"][action]
                key_name = pygame.key.name(key_val).upper() if remapping_key != action else "PRESS KEY..."
                key_surf = font_small.render(key_name, True, (255, 255, 255))
                screen.blit(key_surf, key_surf.get_rect(center=rect.center))

                y_offset += 45

            back_color = BUTTON_HOVER if controls_back_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, back_color, controls_back_rect, border_radius=12)
            pygame.draw.rect(screen, current_theme["TEXT"], controls_back_rect, 2, border_radius=12)
            back_text = font.render("BACK", True, (255, 255, 255))
            screen.blit(back_text, back_text.get_rect(center=controls_back_rect.center))

        elif game_state == "PLAYING":
            game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
            draw_grid(game_surface, game.grid, game.clearing_rows)

            if not game.game_over and not game.game_over_animating and not game.clearing_rows:
                piece = game.current_piece
                piece_color = piece.get_color()
                
                shadow_y = game.get_shadow_y()
                for r, row in enumerate(piece.image()):
                    for c, cell in enumerate(row):
                        if cell:
                            pygame.draw.rect(
                                game_surface,
                                current_theme["SHADOW_FILL"],
                                ((piece.x + c) * GRID_SIZE, (shadow_y + r) * GRID_SIZE, GRID_SIZE, GRID_SIZE),
                                0
                            )
                            pygame.draw.rect(
                                game_surface,
                                current_theme["SHADOW_BORDER"],
                                ((piece.x + c) * GRID_SIZE, (shadow_y + r) * GRID_SIZE, GRID_SIZE, GRID_SIZE),
                                1
                            )

                for r, row in enumerate(piece.image()):
                    for c, cell in enumerate(row):
                        if cell:
                            pygame.draw.rect(
                                game_surface, 
                                piece_color, 
                                ((piece.x + c) * GRID_SIZE, (piece.y + r) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 
                                0
                            )
                            pygame.draw.rect(
                                game_surface, 
                                current_theme["BOARD_BORDER"], 
                                ((piece.x + c) * GRID_SIZE, (piece.y + r) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 
                                1
                            )

            screen.blit(game_surface, (40, 30))
            pygame.draw.rect(screen, current_theme["BOARD_BORDER"], (40, 30, GAME_WIDTH, GAME_HEIGHT), 2)

            if game.popup_text and pygame.time.get_ticks() - game.popup_timer < 900:
                if current_theme == LIGHT_THEME:
                    popup_col = (220, 110, 0)
                    popup_outline = (50, 50, 60)
                else:
                    popup_col = (255, 200, 0)
                    popup_outline = (10, 10, 15)

                draw_outlined_text(
                    screen, game.popup_text, font_popup,
                    popup_col, popup_outline,
                    40 + GAME_WIDTH // 2, 16
                )

            # --- UI Panel ---
            ui_x = 295

            score_card = pygame.Rect(ui_x, 30, 140, 70)
            pygame.draw.rect(screen, current_theme["CARD_BG"], score_card, border_radius=8)
            pygame.draw.rect(screen, current_theme["CARD_BORDER"], score_card, 1, border_radius=8)

            score_label = font.render("SCORE", True, current_theme["TEXT"])
            score_val = font_large.render(str(game.score), True, current_theme["VAL_TEXT"])
            screen.blit(score_label, (ui_x + 12, 38))
            screen.blit(score_val, (ui_x + 12, 63))

            total_seconds = game_time // 1000
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"

            time_card = pygame.Rect(ui_x, 110, 140, 70)
            pygame.draw.rect(screen, current_theme["CARD_BG"], time_card, border_radius=8)
            pygame.draw.rect(screen, current_theme["CARD_BORDER"], time_card, 1, border_radius=8)

            time_label = font.render("TIME", True, current_theme["TEXT"])
            time_val = font_large.render(time_str, True, current_theme["VAL_TEXT"])
            screen.blit(time_label, (ui_x + 12, 118))
            screen.blit(time_val, (ui_x + 12, 143))

            next_card = pygame.Rect(ui_x, 190, 140, 110)
            pygame.draw.rect(screen, current_theme["CARD_BG"], next_card, border_radius=8)
            pygame.draw.rect(screen, current_theme["CARD_BORDER"], next_card, 1, border_radius=8)

            next_label = font.render("NEXT", True, current_theme["TEXT"])
            screen.blit(next_label, (ui_x + 12, 198))

            if not game.game_over and not game.game_over_animating:
                next_shape = game.next_piece.image()
                next_color = game.next_piece.get_color()
                shape_w = len(next_shape[0])
                shape_h = len(next_shape)
                
                start_x = ui_x + (140 - (shape_w * 18)) // 2
                start_y = 222 + (78 - (shape_h * 18)) // 2

                for r, row in enumerate(next_shape):
                    for c, cell in enumerate(row):
                        if cell:
                            pygame.draw.rect(
                                screen,
                                next_color,
                                (start_x + c * 18, start_y + r * 18, 18, 18),
                                0
                            )
                            pygame.draw.rect(
                                screen,
                                current_theme["BOARD_BORDER"],
                                (start_x + c * 18, start_y + r * 18, 18, 18),
                                1
                            )

            if game.game_over:
                over_card = pygame.Rect(ui_x, 315, 140, 95)
                pygame.draw.rect(screen, current_theme["CARD_BG"], over_card, border_radius=8)
                pygame.draw.rect(screen, (220, 60, 60), over_card, 2, border_radius=8)

                game_over_label = font.render("GAME OVER", True, (220, 60, 60))
                restart_tip = font_small.render("Space: Retry", True, current_theme["TEXT"])
                menu_tip = font_small.render("Esc: Menu", True, current_theme["TEXT"])
                
                screen.blit(game_over_label, (ui_x + 12, 328))
                screen.blit(restart_tip, (ui_x + 12, 354))
                screen.blit(menu_tip, (ui_x + 12, 376))

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()