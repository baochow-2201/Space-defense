# src/engine/enemy.py

import pygame
import math
import random
from core.utils import safe_load_image
from engine.bullet import Bullet

WIDTH = 1280
HEIGHT = 720

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, config, bullet_group):
        super().__init__()
        self.cfg = config
        self.bullet_group = bullet_group

        # Stats
        self.hp = int(config.get("hp", 10))
        self.speed = float(config.get("speed", 2))
        self.pattern = config.get("pattern", "straight")
        self.score_value = int(config.get("score_value", 10))

        # Enemy size
        self.width = config.get("width", 125)
        self.height = config.get("height", 75)

        # Load animation frames
        cfg_images = config.get("images", ["ma1.png", "ma2.png"])
        self.frames = []
        for img in cfg_images:
            try:
                surf = safe_load_image(img, scale=(self.width, self.height))
            except FileNotFoundError:
                surf = pygame.Surface((self.width, self.height))
                surf.fill((255, 0, 0))
            self.frames.append(surf)
        if not self.frames:
            self.frames = [pygame.Surface((self.width, self.height))]

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))

        # Animation timer
        self.last_anim = pygame.time.get_ticks()
        self.anim_speed = 150

        # Shooting
        self.last_shot = 0
        self.shoot_delay = max(600, int(1800 - self.speed * 80))

        # Bullet animation
        self.bullet_frames = []
        for bimg in ["enemybullet1.png", "enemybullet2.png"]:
            try:
                bsurf = safe_load_image(bimg, scale=(25, 45))
            except FileNotFoundError:
                bsurf = pygame.Surface((25, 45))
                bsurf.fill((255, 255, 0))
            self.bullet_frames.append(bsurf)

        # Movement vars
        self.start_x = x
        self.start_y = y
        self.angle = random.random() * math.pi * 2
        self.dir = 1

    def update(self):
        self.move()
        self.animate()
        self.try_shoot()

    def move(self):
        # Boss drop then stationary
        if self.pattern == "drop_then_stationary":
            target_y = HEIGHT // 9
            if self.rect.y < target_y:
                self.rect.y += self.speed
            else:
                self.rect.y = target_y
            return

        # Quái thường
        if self.pattern == "straight":
            self.rect.y += self.speed
        elif self.pattern == "zigzag":
            self.rect.y += self.speed
            self.rect.x += int(self.dir * self.speed * 2.5)
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.dir *= -1
        elif self.pattern == "wave":
            self.rect.y += self.speed
            self.rect.x = int(self.start_x + math.sin(self.rect.y / 30) * 90)
        elif self.pattern == "spiral":
            self.angle += 0.05
            self.rect.x = int(self.start_x + math.cos(self.angle) * 60)
            self.rect.y += self.speed
        elif self.pattern == "random":
            self.rect.x += random.randint(-1, 1) * int(self.speed)
            self.rect.y += self.speed
        elif self.pattern == "chase":
            self.rect.y += self.speed
            self.rect.x += random.randint(-2, 2)

        # Respawn quái thường
        if self.pattern != "drop_then_stationary" and self.rect.top > HEIGHT + 80:
            self.rect.y = random.randint(-200, -80)
            self.rect.x = random.randint(60, WIDTH - 60)

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim > self.anim_speed:
            self.last_anim = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def try_shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay and random.random() < 0.03:
            bullet = Bullet(
                self.rect.centerx,
                self.rect.centery + 25,
                speed=6,
                damage=5,
                images=self.bullet_frames
            )
            self.bullet_group.add(bullet)
            self.last_shot = now

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.kill()
            return self.score_value
        return 0
