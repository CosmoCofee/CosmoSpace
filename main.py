import pygame
import random
import math
import sys

pygame.init()

# ==================== ЗВУКИ И МУЗЫКА ====================
try:
    pygame.mixer.music.load("sounds/music.mp3")
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(-1)

    sound_laser = pygame.mixer.Sound("sounds/laser.mp3")
    sound_pistol = pygame.mixer.Sound("sounds/pistol.mp3")
    sound_laser.set_volume(0.5)
    sound_pistol.set_volume(0.5)
except Exception as e:
    print("Ошибка загрузки звуков:", e)
    sound_laser = None
    sound_pistol = None

# ==================== НАСТРОЙКИ ЭКРАНА ====================
WIDTH, HEIGHT = 800, 600
FPS = 60

INFO = pygame.display.Info()
SCREEN_W, SCREEN_H = INFO.current_w, INFO.current_h
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
pygame.display.set_caption("CosmoSpace: Absolute")

game_surface = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (180, 0, 255)
ORANGE = (255, 140, 0)
BLUE = (50, 100, 255)
DARK = (10, 10, 30)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

font_big = pygame.font.SysFont("couriernew", 48, bold=True)
font_mid = pygame.font.SysFont("couriernew", 28, bold=True)
font_small = pygame.font.SysFont("couriernew", 18, bold=True)
font_secret = pygame.font.SysFont("arial", 22, bold=True)

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def draw_text_center(surf, text, font, color, y_offset=0):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    surf.blit(render, rect)

def draw_hp_bar(surf, x, y, hp, max_hp, color):
    pygame.draw.rect(surf, (50, 50, 50), (x, y, 200, 20))
    pygame.draw.rect(surf, color, (x, y, int(200 * hp / max_hp), 20))
    pygame.draw.rect(surf, WHITE, (x, y, 200, 20), 2)

def draw_fps(surf):
    fps_text = font_small.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
    surf.blit(fps_text, (10, 10))

def smooth_fade_in(surface, duration_ms=1000):
    steps = max(1, duration_ms // 16)
    fade_surf = pygame.Surface((WIDTH, HEIGHT))
    fade_surf.fill(BLACK)
    for i in range(steps + 1):
        alpha = int(255 * (1 - i / steps))
        fade_surf.set_alpha(alpha)
        surface.blit(fade_surf, (0, 0))
        scaled = pygame.transform.scale(surface, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

# ==================== ЗАСТАВКА ====================
def show_splash_screen():
    timer = 180
    while timer > 0:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN:
                return
        
        game_surface.fill(BLACK)
        cx, cy = WIDTH // 2, HEIGHT // 2 - 100
        
        pygame.draw.rect(game_surface, WHITE, (cx - 60, cy - 40, 120, 100), border_radius=20)
        pygame.draw.ellipse(game_surface, BROWN, (cx - 50, cy - 30, 100, 40))
        pygame.draw.arc(game_surface, WHITE, (cx + 50, cy - 10, 60, 60), -math.pi/2, math.pi/2, 10)
        
        pygame.draw.line(game_surface, LIGHT_GRAY, (cx - 20, cy - 60), (cx - 30, cy - 90), 5)
        pygame.draw.line(game_surface, LIGHT_GRAY, (cx, cy - 70), (cx - 10, cy - 100), 5)
        pygame.draw.line(game_surface, LIGHT_GRAY, (cx + 20, cy - 60), (cx + 10, cy - 90), 5)
        
        draw_text_center(game_surface, "Игра компании", font_mid, WHITE, -20)
        draw_text_center(game_surface, "CosmoCofee", font_big, ORANGE, 40)
        
        draw_fps(game_surface)
        
        scaled = pygame.transform.scale(game_surface, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        timer -= 1

# ==================== ПАУЗА ====================
def pause_menu():
    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: return "continue"
                if e.key == pygame.K_2: return "menu"
                if e.key == pygame.K_3: pygame.quit(); sys.exit()
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        game_surface.blit(overlay, (0, 0))
        
        draw_text_center(game_surface, "ПАУЗА", font_big, WHITE, -150)
        draw_text_center(game_surface, "1 - Продолжить", font_mid, GREEN, 0)
        draw_text_center(game_surface, "2 - В главное меню", font_mid, YELLOW, 60)
        draw_text_center(game_surface, "3 - Выйти из игры", font_mid, RED, 120)
        
        scaled = pygame.transform.scale(game_surface, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

# ==================== УРОВЕНЬ 1: КОСМОБОЙ ====================
class SpaceShip:
    def __init__(self):
        self.w, self.h = 40, 40
        self.x, self.y = WIDTH // 2 - 20, HEIGHT - 80
        self.speed = 6; self.hp = 5; self.max_hp = 5; self.shoot_cd = 0; self.invuln = 0
    def update(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.x += self.speed
        self.x = max(0, min(WIDTH - self.w, self.x))
        if self.shoot_cd > 0: self.shoot_cd -= 1
        if self.invuln > 0: self.invuln -= 1
    def draw(self, surf):
        if self.invuln > 0 and (self.invuln // 4) % 2 == 0: return
        cx = self.x + 20
        pygame.draw.polygon(surf, CYAN, [(cx, self.y), (self.x, self.y + 40), (self.x + 40, self.y + 40)])
        pygame.draw.rect(surf, BLUE, (self.x + 10, self.y + 32, 20, 8))

class Bullet:
    def __init__(self, x, y, vy, color, size=6, owner="player"):
        self.x, self.y, self.vy, self.color, self.size, self.owner = x, y, vy, color, size, owner
    def update(self): self.y += self.vy
    def draw(self, surf): pygame.draw.rect(surf, self.color, (self.x, self.y, self.size, self.size * 2))
    def off_screen(self): return self.y < -20 or self.y > HEIGHT + 20

class SlowEnemy:
    def __init__(self, x, y):
        self.w, self.h = 40, 30
        self.x, self.y = x, y
        self.hp = 2
        self.speed_x = random.choice([-1.5, 1.5])
        self.speed_y = random.choice([-0.5, 0.5, 1])
        self.color = random.choice([GREEN, PURPLE, ORANGE])
        self.shoot_timer = random.randint(90, 180)
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x < 0 or self.x > WIDTH - self.w: self.speed_x *= -1
        if self.y < 60 or self.y > HEIGHT // 2: self.speed_y *= -1
        if self.shoot_timer > 0: self.shoot_timer -= 1
    def draw(self, surf):
        x, y = self.x, self.y
        pygame.draw.rect(surf, self.color, (x + 6, y, 28, 30))
        pygame.draw.rect(surf, self.color, (x, y + 6, 40, 18))
        pygame.draw.rect(surf, BLACK, (x + 10, y + 10, 6, 6))
        pygame.draw.rect(surf, BLACK, (x + 24, y + 10, 6, 6))

class SpaceBoss:
    def __init__(self):
        self.w, self.h = 160, 110
        self.x, self.y = WIDTH // 2 - 80, -150
        self.target_y = 80; self.hp = 50; self.max_hp = 50
        self.time = 0; self.shoot_timer = 90
    def update(self):
        self.time += 0.03
        if self.y < self.target_y: self.y += 2
        self.x = WIDTH // 2 - 80 + math.sin(self.time) * 120
    def draw(self, surf):
        x, y = self.x, self.y
        pygame.draw.ellipse(surf, PURPLE, (x, y + 20, 160, 90))
        pygame.draw.ellipse(surf, (100, 0, 150), (x + 30, y, 100, 110))
        pygame.draw.circle(surf, CYAN, (int(x + 80), int(y + 40)), 25)
        for i in range(4):
            pygame.draw.circle(surf, RED, (int(x + 25 + i * 35), int(y + 70)), 8)

def play_space_level():
    smooth_fade_in(game_surface)
    player = SpaceShip()
    bullets, enemy_bullets, enemies = [], [], []
    boss = None
    killed = 0
    misses = 0
    enemies_to_kill = 5
    
    max_ammo = 10
    ammo = max_ammo
    is_reloading = False
    reload_timer = 0
    
    for i in range(enemies_to_kill):
        enemies.append(SlowEnemy(80 + i * 130, 100 + (i%2)*50))

    running = True
    while running:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if pause_menu() == "menu": return "menu", False
                if e.key == pygame.K_SPACE and player.shoot_cd <= 0 and ammo > 0 and not is_reloading:
                    bullets.append(Bullet(player.x + 18, player.y, -10, YELLOW))
                    player.shoot_cd = 10
                    
                    if sound_laser:
                        sound_laser.play()
                        
                    ammo -= 1
                    if ammo == 0:
                        is_reloading = True
                        reload_timer = FPS * 5

        if is_reloading:
            reload_timer -= 1
            if reload_timer <= 0:
                ammo = max_ammo
                is_reloading = False

        keys = pygame.key.get_pressed()
        player.update(keys)

        for b in bullets[:]:
            b.update()
            if b.off_screen(): 
                bullets.remove(b)
                misses += 1
            else:
                for en in enemies[:]:
                    if en.x < b.x < en.x + en.w and en.y < b.y < en.y + en.h:
                        bullets.remove(b); en.hp -= 1
                        if en.hp <= 0: enemies.remove(en); killed += 1
                        break

        if killed >= enemies_to_kill and not boss:
            boss = SpaceBoss()
            enemy_bullets.clear()

        if boss:
            boss.update()
            if boss.shoot_timer > 0: boss.shoot_timer -= 1
            else:
                boss.shoot_timer = 60
                enemy_bullets.append(Bullet(boss.x + 40, boss.y + 90, 6, RED, 8))
                enemy_bullets.append(Bullet(boss.x + 120, boss.y + 90, 6, RED, 8))

            for b in bullets[:]:
                if boss.x < b.x < boss.x + boss.w and boss.y < b.y < boss.y + boss.h:
                    bullets.remove(b); boss.hp -= 1
                    if boss.hp <= 0: 
                        perfect = (misses == 0)
                        return "victory", perfect

        for en in enemies:
            en.update()
            if en.shoot_timer <= 0:
                enemy_bullets.append(Bullet(en.x + 18, en.y + 30, 5, RED, 6))
                en.shoot_timer = random.randint(100, 180)

        for b in enemy_bullets[:]:
            b.update()
            if b.off_screen(): enemy_bullets.remove(b)
            elif player.invuln <= 0 and player.x < b.x < player.x + player.w and player.y < b.y < player.y + player.h:
                enemy_bullets.remove(b)
                player.hp -= 1; player.invuln = 60
                if player.hp <= 0: return "gameover", False

        game_surface.fill(DARK)
        for _ in range(30): pygame.draw.rect(game_surface, WHITE, (random.randint(0, WIDTH), random.randint(0, HEIGHT), 1, 1))
        for en in enemies: en.draw(game_surface)
        for b in bullets: b.draw(game_surface)
        for b in enemy_bullets: b.draw(game_surface)
        if boss: 
            boss.draw(game_surface)
            draw_hp_bar(game_surface, WIDTH - 210, 40, boss.hp, boss.max_hp, RED)
        player.draw(game_surface)
        draw_hp_bar(game_surface, 10, 40, player.hp, player.max_hp, GREEN)
        
        if is_reloading:
            rt = font_small.render(f"ПЕРЕЗАРЯДКА: {reload_timer/FPS:.1f}с", True, RED)
            game_surface.blit(rt, (WIDTH - 200, 10))
        else:
            at = font_small.render(f"Патроны: {ammo}/{max_ammo}", True, YELLOW)
            game_surface.blit(at, (WIDTH - 150, 10))

        draw_fps(game_surface)
        
        scaled = pygame.transform.scale(game_surface, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

# ==================== УРОВЕНЬ 2: НАЙДИ ПРИШЕЛЬЦА ====================
class Hero:
    def __init__(self):
        self.w, self.h = 30, 40
        self.x, self.y = 100, 100
        self.speed = 5

    def update(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.y += self.speed

    def draw(self, surf, cam_x, cam_y):
        px, py = self.x - cam_x, self.y - cam_y
        pygame.draw.rect(surf, (255, 200, 150), (px + 5, py, 20, 15))
        pygame.draw.rect(surf, BLUE, (px, py + 15, 30, 25))
        pygame.draw.rect(surf, BLACK, (px + 10, py + 35, 10, 5))
        
        mx, my = pygame.mouse.get_pos()
        mx = mx * (WIDTH / SCREEN_W)
        my = my * (HEIGHT / SCREEN_H)
        
        angle = math.atan2(my - (py + 20), mx - (px + 15))
        pygame.draw.line(surf, GRAY, (px + 15, py + 20), (px + 15 + math.cos(angle)*20, py + 20 + math.sin(angle)*20), 5)

class DisguisedAlien:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = 50, 50
        self.alive = True
        self.type = random.choice(["box", "bush"])
    def draw(self, surf, cam_x, cam_y):
        if not self.alive: return
        rect = pygame.Rect(self.x - cam_x, self.y - cam_y, self.w, self.h)
        if self.type == "box":
            pygame.draw.rect(surf, BROWN, rect)
        else:
            pygame.draw.ellipse(surf, (0, 150, 0), rect)

def play_find_alien_level():
    smooth_fade_in(game_surface)
    hero = Hero()
    aliens = []
    killed = 0
    world_w, world_h = 2000, 1500
    cam_x, cam_y = 0, 0
    bullets = []
    
    max_ammo = 8
    ammo = max_ammo
    is_reloading = False
    reload_timer = 0
    
    for i in range(20):
        x = random.randint(100, world_w - 100)
        y = random.randint(100, world_h - 100)
        aliens.append(DisguisedAlien(x, y))

    running = True
    while running:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if pause_menu() == "menu": return "menu"
                if e.key == pygame.K_SPACE and ammo > 0 and not is_reloading:
                    mx, my = pygame.mouse.get_pos()
                    mx = mx * (WIDTH / SCREEN_W)
                    my = my * (HEIGHT / SCREEN_H)
                    
                    angle = math.atan2(my + cam_y - (hero.y + 20), mx + cam_x - (hero.x + 15))
                    bullets.append([hero.x + 15, hero.y + 20, math.cos(angle)*15, math.sin(angle)*15])
                    
                    if sound_pistol:
                        sound_pistol.play()
                        
                    ammo -= 1
                    if ammo == 0:
                        is_reloading = True
                        reload_timer = FPS * 5
            
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = pygame.mouse.get_pos()
                mx = mx * (WIDTH / SCREEN_W)
                my = my * (HEIGHT / SCREEN_H)
                wx, wy = mx + cam_x, my + cam_y
                
                for al in aliens:
                    if al.alive and al.x < wx < al.x + al.w and al.y < wy < al.y + al.h:
                        al.alive = False
                        killed += 1

        if is_reloading:
            reload_timer -= 1
            if reload_timer <= 0:
                ammo = max_ammo
                is_reloading = False

        keys = pygame.key.get_pressed()
        hero.update(keys)
        cam_x = max(0, min(world_w - WIDTH, hero.x - WIDTH // 2))
        cam_y = max(0, min(world_h - HEIGHT, hero.y - HEIGHT // 2))

        for b in bullets[:]:
            b[0] += b[2]
            b[1] += b[3]
            if b[0] < 0 or b[0] > world_w or b[1] < 0 or b[1] > world_h: 
                bullets.remove(b)
            else:
                for al in aliens:
                    if al.alive and al.x < b[0] < al.x + al.w and al.y < b[1] < al.y + al.h:
                        al.alive = False
                        killed += 1
                        bullets.remove(b)
                        break

        game_surface.fill((100, 160, 100))
        for rx in range(0, world_w, 400): pygame.draw.rect(game_surface, GRAY, (rx - cam_x, 0, 100, HEIGHT))
        for ry in range(0, world_h, 400): pygame.draw.rect(game_surface, GRAY, (0, ry - cam_y, WIDTH, 100))

        for al in aliens: al.draw(game_surface, cam_x, cam_y)
        
        for b in bullets: 
            pygame.draw.circle(game_surface, YELLOW, (int(b[0] - cam_x), int(b[1] - cam_y)), 5)
            pygame.draw.circle(game_surface, ORANGE, (int(b[0] - cam_x), int(b[1] - cam_y)), 2)
            
        hero.draw(game_surface, cam_x, cam_y)
        
        draw_hp_bar(game_surface, 10, 40, 5, 5, GREEN)
        draw_text_center(game_surface, f"Найдено: {killed} / 20", font_small, BLACK, -HEIGHT//2 + 30)
        
        if is_reloading:
            rt = font_small.render(f"ПЕРЕЗАРЯДКА: {reload_timer/FPS:.1f}с", True, RED)
            game_surface.blit(rt, (WIDTH - 200, 10))
        else:
            at = font_small.render(f"Патроны: {ammo}/{max_ammo}", True, BLACK)
            game_surface.blit(at, (WIDTH - 150, 10))

        draw_fps(game_surface)
        
        scaled = pygame.transform.scale(game_surface, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        
        if killed >= 20: return "victory"

# ==================== СПРАВКА / ТИТРЫ ====================
def show_credits():
    smooth_fade_in(game_surface, 800)
    
    scroll_y = HEIGHT
    scroll_speed = 1.5
    credits_height = 1500
    credits_surf = pygame.Surface((WIDTH, credits_height), pygame.SRCALPHA)
    
    draw_text_center(credits_surf, "СПРАВКА И ТИТРЫ", font_big, CYAN, 200)
    draw_text_center(credits_surf, "Разработчики:", font_mid, WHITE, 350)
    draw_text_center(credits_surf, "Плутенко Егор (Absolute)", font_mid, YELLOW, 400)
    draw_text_center(credits_surf, "Литвин Данил (Juo)", font_mid, YELLOW, 450)
    draw_text_center(credits_surf, "Спасибо за игру!", font_mid, WHITE, 600)
    
    cx, cy = WIDTH // 2, 800
    pygame.draw.rect(credits_surf, WHITE, (cx - 60, cy - 40, 120, 100), border_radius=20)
    pygame.draw.ellipse(credits_surf, BROWN, (cx - 50, cy - 30, 100, 40))
    pygame.draw.arc(credits_surf, WHITE, (cx + 50, cy - 10, 60, 60), -math.pi/2, math.pi/2, 10)
    
    pygame.draw.line(credits_surf, LIGHT_GRAY, (cx - 20, cy - 60), (cx - 30, cy - 90), 5)
    pygame.draw.line(credits_surf, LIGHT_GRAY, (cx, cy - 70), (cx - 10, cy - 100), 5)
    pygame.draw.line(credits_surf, LIGHT_GRAY, (cx + 20, cy - 60), (cx + 10, cy - 90), 5)
    
    draw_text_center(credits_surf, "CosmoCofee", font_big, ORANGE, 950)
    draw_text_center(credits_surf, "Спасибо, что играли!", font_mid, WHITE, 1050)
    
    running = True
    while running:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_RETURN:
                    return
        
        game_surface.fill(DARK)
        scroll_y -= scroll_speed
        game_surface.blit(credits_surf, (0, scroll_y))
        
        if scroll_y < -credits_height + HEIGHT:
            scroll_y = HEIGHT
            pygame.time.wait(1000)
            
        draw_fps(game_surface)
        scaled = pygame.transform.scale(game_surface, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

# ==================== КОНЦОВКИ ====================
def show_secret_ending():
    smooth_fade_in(game_surface)
    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN: return
        game_surface.fill(DARK)
        draw_text_center(game_surface, "ИДЕАЛЬНОЕ ПРОХОЖДЕНИЕ!", font_big, YELLOW, -100)
        draw_text_center(game_surface, "Секретка от Егора:", font_mid, WHITE, -20)
        draw_text_center(game_surface, "Даня Физик топ 1 кент", font_secret, GREEN, 40)
        draw_text_center(game_surface, "ENTER чтобы продолжить", font_small, GRAY, 120)
        
        scaled = pygame.transform.scale(game_surface, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

def show_meteor_ending():
    t = 0
    while t < 100:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        game_surface.fill((100, 160, 100))
        pygame.draw.rect(game_surface, GRAY, (0, HEIGHT-100, WIDTH, 100))
        pygame.draw.rect(game_surface, (50,50,50), (200, HEIGHT-200, 100, 100))
        
        mx = WIDTH//2 + math.sin(t*0.1)*100
        my = -200 + t * 7
        pygame.draw.circle(game_surface, ORANGE, (int(mx), int(my)), 50)
        pygame.draw.circle(game_surface, RED, (int(mx), int(my)), 30)
        pygame.draw.circle(game_surface, YELLOW, (int(mx), int(my)), 10)
        draw_text_center(game_surface, "МЕТЕОРИТ ЛЕТИТ НА ЗЕМЛЮ!", font_big, RED, -200)
        t += 1
        
        # Правильное масштабирование (без дублей)
        scaled = pygame.transform.scale(game_surface, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
    
    screen.fill(WHITE)
    pygame.display.flip()
    pygame.time.wait(800)
    
    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN: return
        game_surface.fill(DARK)
        draw_text_center(game_surface, "ПРИШЕЛЬЦЫ УНИЧТОЖЕНЫ!", font_big, ORANGE, -60)
        draw_text_center(game_surface, "Но ценой Земли...", font_mid, RED, 0)
        draw_text_center(game_surface, "ENTER чтобы продолжить", font_small, GRAY, 100)
        
        scaled = pygame.transform.scale(game_surface, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

def show_game_cleared_screen():
    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN: return
        game_surface.fill(DARK)
        draw_text_center(game_surface, "ИГРА ПРОЙДЕНА!", font_big, GREEN, -50)
        draw_text_center(game_surface, "ENTER - в главное меню", font_mid, WHITE, 50)
        scaled = pygame.transform.scale(game_surface, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

# ==================== МЕНЮ ====================
def show_menu(show_credits_btn, level1_done, level2_done):
    smooth_fade_in(game_surface)
    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: 
                    smooth_fade_in(game_surface, 500)
                    return 1
                if e.key == pygame.K_2: 
                    smooth_fade_in(game_surface, 500)
                    return 2
                if e.key == pygame.K_3 and show_credits_btn: 
                    return 3
                if e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
        
        game_surface.fill(DARK)
        draw_text_center(game_surface, "CosmoSpace: Absolute", font_big, CYAN, -230)
        draw_text_center(game_surface, "Выбери уровень:", font_mid, WHITE, -150)
        
        color1 = GREEN if level1_done else WHITE
        color2 = YELLOW if level2_done else WHITE
        draw_text_center(game_surface, "1 - Космобой", font_mid, color1, -50)
        draw_text_center(game_surface, "2 - Найди пришельца", font_mid, color2, 10)
        
        if show_credits_btn:
            draw_text_center(game_surface, "3 - Справка (Титры)", font_mid, PURPLE, 90)
            draw_text_center(game_surface, "Обе игры пройдены! Спасибо!", font_small, GREEN, 130)
        else:
            draw_text_center(game_surface, "3 - ???? (Пройди обе игры)", font_mid, GRAY, 90)
        
        draw_text_center(game_surface, "Разработчики: Absolute & Juo", font_small, ORANGE, 230)
        draw_fps(game_surface)
        
        scaled = pygame.transform.scale(game_surface, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    smooth_fade_in(game_surface, 1500)
    show_splash_screen()
    
    level1_done = False
    level2_done = False
    
    while True:
        show_credits_btn = level1_done and level2_done
        
        choice = show_menu(show_credits_btn, level1_done, level2_done)
        
        if choice == 1:
            res, perfect = play_space_level()
            if res == "victory":
                level1_done = True
                if perfect: show_secret_ending()
                else: show_game_cleared_screen()
        elif choice == 2:
            if play_find_alien_level() == "victory":
                level2_done = True
                show_meteor_ending()
        elif choice == 3 and show_credits_btn:
            show_credits() # <-- Добавлен вызов титров!
        