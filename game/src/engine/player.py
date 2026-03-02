# src/engine/player.py
import pygame
from core.utils import safe_load_image
from core.settings import WIDTH, HEIGHT
from engine.bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, bullets_group, config=None):
        super().__init__()
        self.bullets_group = bullets_group
        self.config = config or {}

        # ========= LOAD ANIMATION MÁY BAY =========
        image_files = self.config.get("images", ["mbayf1.png", "mbayf2.png"])
        self.images = [safe_load_image(p, scale=(120, 90)) for p in image_files]

        self.current_image = 0
        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect(center=(x, y))

        # ========= PLAYER STATS =========
        self.hp = self.config.get("hp", 100)
        self.speed = self.config.get("speed", 5)

        # ========= ANIMATION SPEED =========
        self.last_anim = pygame.time.get_ticks()
        self.anim_speed = 100

        # ========= ĐẠN ANIMATION =========
        self.bullet_images = [
            safe_load_image("bullet1.png", scale=(50, 60)),
            safe_load_image("bullet2.png", scale=(50, 60))
        ]
        self.bullet_anim_index = 0

        # ========= SHOOTING =========
        self.last_shot = 0
        self.shoot_delay = 250  # ms

    # ==================================================================
    # UPDATE PLAYER (MOVE + ANIM + SHOOT)
    # ==================================================================
    def update(self, keys_pressed):

        # --------- DI CHUYỂN ----------
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys_pressed[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys_pressed[pygame.K_DOWN]:
            self.rect.y += self.speed

        # --------- GIỮ TRONG MÀN HÌNH ----------
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

        # --------- ANIMATION BAY ----------
        now = pygame.time.get_ticks()
        if now - self.last_anim > self.anim_speed:
            self.last_anim = now
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]

        # --------- BẮN ĐẠN ----------
        if keys_pressed[pygame.K_SPACE]:
            self.shoot()

    # ==================================================================
    # SHOOTING FUNCTION
    # ==================================================================
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_delay:
            return

        # 2 dạng animation đạn
        bullet_img = self.bullet_images[self.bullet_anim_index]
        self.bullet_anim_index = (self.bullet_anim_index + 1) % len(self.bullet_images)

        bullet = Bullet(
            self.rect.centerx,
            self.rect.top,
            speed=-12,
            damage=10,
            image=bullet_img
        )

        self.bullets_group.add(bullet)
        self.last_shot = now

    # ==================================================================
    # DRAW PLAYER
    # ==================================================================
    def draw(self, screen):
        screen.blit(self.image, self.rect)
