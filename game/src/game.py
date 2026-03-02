# src/game.py
import pygame
import random
from engine.level_manager import LevelManager
from engine.player import Player
from engine.enemy import Enemy
from engine.collision import bullets_hit_enemies, enemy_bullets_hit_player
from engine.skills import SkillEffect, SkillManager, BossSkill
from ui.ui_profile import ProfileUI
from core.database import Database

WIDTH, HEIGHT = 1280, 720

class Game:
    def __init__(self, screen, player_name, level=1):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.player_name = player_name
        self.level = level
        self.font = pygame.font.Font(None, 36)
        self.paused = False
        self.game_ended = False

        # Database
        self.db = Database()
        self.player_data = self.db.get_player()  # lưu dữ liệu người chơi

        # Starfield
        self.stars = [[random.randint(0, WIDTH),
                       random.randint(0, HEIGHT),
                       random.randint(1, 3),
                       random.uniform(0.5, 2)] for _ in range(120)]

        # Planets
        self.planets = []
        for _ in range(3):
            surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(surf, (random.randint(50, 255),
                                      random.randint(50, 255),
                                      random.randint(50, 255)), (40, 40), 40)
            x = random.randint(0, WIDTH - 80)
            y = random.randint(-HEIGHT, 0)
            speed = random.uniform(0.2, 1)
            self.planets.append([surf, x, y, speed])

        self.all_sprites = pygame.sprite.Group()
        self.boss_skills = pygame.sprite.Group()

        # Load level
        self.load_level(self.level)

        # Skill manager
        self.skill_manager = SkillManager(
            player=self.player,
            all_sprites=self.all_sprites,
            enemies=self.enemies,
            enemy_bullets=self.enemy_bullets,
            width=WIDTH,
            height=HEIGHT
        )

        # Profile UI
        self.profile_ui = ProfileUI(self.screen, self.db, self.player_name)

    # -----------------------------
    # Load Level
    # -----------------------------
    def load_level(self, level):
        self.level = level
        self.win = False
        self.game_over = False
        self.running = True

        cfg = LevelManager.get_level_config(level)
        self.level_config = cfg

        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()

        player_cfg = cfg.get("player", {})
        self.player = Player(WIDTH // 2, HEIGHT - 100, self.player_bullets, config=player_cfg)

        # Tạo enemies
        for e_cfg in cfg.get("enemies", []):
            etype = e_cfg.get("type", "bat")
            if etype == "boss":
                x = WIDTH // 2
                y = -100
                enemy_cfg = e_cfg.copy()
                enemy_cfg["pattern"] = "drop_then_stationary"
                enemy = Enemy(x, y, enemy_cfg, self.enemy_bullets)
                enemy.max_hp = enemy_cfg.get("hp", 1000)
                enemy.hp = enemy.max_hp
                self.enemies.add(enemy)
                # ---- Thêm skill cho boss ----
                shoot_skill = BossSkill(enemy, self.all_sprites, self.enemy_bullets, cooldown=1500, skill_type="shoot")
                wide_skill = BossSkill(enemy, self.all_sprites, self.enemy_bullets, cooldown=5000, skill_type="wide")
                self.boss_skills.add(shoot_skill, wide_skill)
                continue
            rows = e_cfg.get("rows", 1)
            cols = e_cfg.get("cols", 1)
            spacing_x = 120
            spacing_y = 100
            group_width = (cols - 1) * spacing_x
            start_x = e_cfg.get("x") or (WIDTH - group_width) // 2
            start_y = e_cfg.get("y") or 0

            for r in range(rows):
                for c in range(cols):
                    x = start_x + c * spacing_x
                    y = start_y + r * spacing_y
                    enemy_cfg = e_cfg.copy()
                    enemy_cfg["speed"] = enemy_cfg.get("speed", 2) * 0.7
                    enemy = Enemy(x, y, enemy_cfg, self.enemy_bullets)
                    enemy.max_hp = enemy_cfg.get("hp", 100)
                    enemy.hp = enemy.max_hp
                    self.enemies.add(enemy)

        # Score của level hiện tại
        self.score_holder = {"score": 0}

    # -----------------------------
    # Main Loop
    # -----------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            self.handle_events()
            if not self.paused:
                self.update()
            self.draw()
            pygame.display.flip()

    # -----------------------------
    # Event Handling
    # -----------------------------
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False
                elif e.key == pygame.K_z:
                    self.paused = not self.paused
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                # Win button
                if getattr(self, "win", False):
                    if self.next_btn_rect.collidepoint(mx, my):

                        # Nếu đã hết level thì hiện màn game_ended
                        if self.level >= LevelManager.get_max_level():
                            self.win = False
                            self.game_ended = True
                            return

                        # Ngược lại: sang level tiếp theo
                        self.level += 1
                        self.load_level(self.level)
                        self.win = False
                        return

                # Retry button
                if getattr(self, "game_over", False):
                    if self.retry_btn_rect.collidepoint(mx, my):
                        self.load_level(self.level)

    # -----------------------------
    # Update
    # -----------------------------
    def update(self):
        keys_pressed = pygame.key.get_pressed()
        self.player.update(keys_pressed)
        self.player_bullets.update()
        self.enemies.update()
        self.enemy_bullets.update()
        self.explosions.update()
        self.skill_manager.handle_input()
        self.all_sprites.update()
        self.boss_skills.update()

        bullets_hit_enemies(self.player_bullets, self.enemies, self.score_holder)
        shield_active = any(isinstance(e, SkillEffect) and e.skill_type == 1 for e in self.all_sprites)
        if not shield_active:
            enemy_bullets_hit_player(self.enemy_bullets, self.player)

        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                if not shield_active:
                    self.player.hp -= 50
                enemy.hp = 0
                enemy.kill()

        for skill_eff in self.all_sprites:
            if isinstance(skill_eff, SkillEffect) and skill_eff.skill_type in [2,3]:
                for enemy in self.enemies:
                    self.skill_manager.apply_damage(enemy, skill_eff)

        if getattr(self.player, "hp", 0) <= 0:
            self.game_over = True

        # Kiểm tra win condition
        enemies_left = [e for e in self.enemies if getattr(e, "pattern","") != "drop_then_stationary"]
        if len(enemies_left) == 0:
            bosses = [e for e in self.enemies if getattr(e, "pattern","") == "drop_then_stationary"]
            if not bosses or all(b.hp <= 0 for b in bosses):
                self.win = True


                # ==========================
                # Lưu điểm vào DB khi win
                player_id = self.player_data["id"]
                level_score = self.score_holder['score']

                # 1. Lưu điểm level
                self.db.update_level_score(player_id, self.level, level_score)

                # 2. Cập nhật tổng điểm
                total_score = self.player_data["total_score"] + level_score
                self.db.update_total_score(player_id, total_score)

                # 3. Cập nhật highest_level nếu vượt
                if self.level >= self.player_data["highest_level"]:
                    self.db.update_highest_level(player_id, self.level)

    # -----------------------------
    # Draw
    # -----------------------------
    def draw(self):
        # Background gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(30*(1-ratio) + 100*ratio)
            g = int(0*(1-ratio) + 50*ratio)
            b = int(50*(1-ratio) + 200*ratio)
            pygame.draw.line(self.screen, (r,g,b), (0,y), (WIDTH,y))

        # Stars
        for star in self.stars:
            pygame.draw.circle(self.screen, (255,255,255), (int(star[0]), int(star[1])), star[2])
            star[1] += star[3]
            if star[1] > HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, WIDTH)
                star[2] = random.randint(1,3)
                star[3] = random.uniform(0.5,2)

        # Planets
        for planet in self.planets:
            self.screen.blit(planet[0], (planet[1], planet[2]))
            planet[2] += planet[3]
            if planet[2] > HEIGHT:
                planet[2] = -planet[0].get_height()
                planet[1] = random.randint(0, WIDTH - planet[0].get_width())

        # Draw objects
        self.player.draw(self.screen)
        self.enemies.draw(self.screen)
        for b in self.player_bullets: b.draw(self.screen)
        for b in self.enemy_bullets: b.draw(self.screen)
        self.explosions.draw(self.screen)
        self.all_sprites.draw(self.screen)

        # Draw HP bars
        for enemy in self.enemies:
            if hasattr(enemy, "hp") and hasattr(enemy, "max_hp"):
                hp_ratio = max(0, enemy.hp / enemy.max_hp)
                bar_w = enemy.rect.width
                bar_h = 5
                bar_x = enemy.rect.x
                bar_y = enemy.rect.y - 10
                pygame.draw.rect(self.screen, (80,80,80), (bar_x, bar_y, bar_w, bar_h))
                pygame.draw.rect(self.screen, (255,0,0), (bar_x, bar_y, int(bar_w*hp_ratio), bar_h))

        # HUD
        self.screen.blit(self.font.render(f"HP: {self.player.hp}", True, (255,255,255)), (10,10))
        self.screen.blit(self.font.render(f"Score: {self.score_holder['score']}", True, (0,255,255)), (10,50))
        self.screen.blit(self.font.render(self.player_name, True, (0,255,255)), (self.screen.get_width()-200,10))

        # Skill icons
        self.skill_manager.draw_skill_icons(self.screen)

        # Pause
        if self.paused:
            pause_text = self.font.render("PAUSED", True, (255,255,0))
            self.screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2))

        # Win / Game Over / Ended
        if getattr(self, "win", False):
            self.draw_win_screen()
        if getattr(self, "game_over", False):
            self.draw_game_over_screen()
        if getattr(self, "game_ended", False):
            self.draw_game_ended()

    # -----------------------------
    # WIN SCREEN
    # -----------------------------
    def draw_win_screen(self):
        self.screen.fill((0,0,0))
        text = self.font.render("YOU WIN!", True, (0,255,0))
        self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 80))

        btn_text = self.font.render("NEXT LEVEL", True, (0,0,0))
        btn_w, btn_h = 220, 60
        btn_x = WIDTH//2 - btn_w//2
        btn_y = HEIGHT//2

        self.next_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, (0,255,0), self.next_btn_rect)
        self.screen.blit(btn_text, (btn_x + btn_w//2 - btn_text.get_width()//2,
                                    btn_y + btn_h//2 - btn_text.get_height()//2))

    # -----------------------------
    # GAME OVER SCREEN
    # -----------------------------
    def draw_game_over_screen(self):
        self.screen.fill((20,0,0))
        text = self.font.render("GAME OVER", True, (255,0,0))
        self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 80))

        btn_text = self.font.render("RETRY", True, (0,0,0))
        btn_w, btn_h = 200, 60
        btn_x = WIDTH//2 - btn_w//2
        btn_y = HEIGHT//2

        self.retry_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, (255,50,50), self.retry_btn_rect)
        self.screen.blit(btn_text, (btn_x + btn_w//2 - btn_text.get_width()//2,
                                    btn_y + btn_h//2 - btn_text.get_height()//2))

    # -----------------------------
    # GAME COMPLETED SCREEN
    # -----------------------------
    def draw_game_ended(self):
        self.screen.fill((0,0,40))
        title = self.font.render("🎉 YOU COMPLETED ALL LEVELS!", True, (0,255,255))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 40))
        small = self.font.render("Thanks for playing!", True, (200,200,200))
        self.screen.blit(small, (WIDTH//2 - small.get_width()//2, HEIGHT//2 + 20))
