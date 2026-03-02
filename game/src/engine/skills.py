import pygame
import os
import random

# =========================
# EFFECT SPRITE
# =========================
class SkillEffect(pygame.sprite.Sprite):
    def __init__(self, image_path=None, pos=(0,0), scale=None, duration=800,
                 follow_player=None, enemy_bullets=None, custom_surface=None,
                 skill_type=None):
        super().__init__()
        self.skill_type = skill_type
        self.follow_player = follow_player
        self.enemy_bullets = enemy_bullets
        self.alpha = 255
        self.duration = duration
        self.start_time = pygame.time.get_ticks()

        # bomb/lightning đánh trúng 1 lần mỗi enemy
        self.hit_once = set() if skill_type in [2,3] else None

        # Load hình
        if custom_surface:
            self.image = custom_surface
        else:
            if image_path and os.path.exists(image_path):
                img = pygame.image.load(image_path).convert_alpha()
                if scale:
                    img = pygame.transform.scale(img, scale)
                self.image = img
            else:
                self.image = pygame.Surface((80,80), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (0,255,255,180), (40,40), 40)

        self.rect = self.image.get_rect(center=pos)

    def update(self):
        now = pygame.time.get_ticks()

        # Shield dính theo player
        if self.follow_player:
            self.rect.center = self.follow_player.rect.center

        # Shield block đạn liên tục
        if self.skill_type == 1 and self.enemy_bullets:
            pygame.sprite.spritecollide(self, self.enemy_bullets, True)

        # Fade out
        elapsed = now - self.start_time
        if elapsed > self.duration - 300:
            fade_ratio = max(0,(self.duration-elapsed)/300)
            self.alpha = int(255*fade_ratio)
            self.image.set_alpha(self.alpha)

        if elapsed > self.duration:
            self.kill()

# =========================
# BOSS BULLET & SKILL
# =========================
class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx=0, dy=5, color=(255,0,0), size=10):
        super().__init__()
        self.image = pygame.Surface((size,size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        self.rect = self.image.get_rect(center=(x,y))
        self.dx = dx
        self.dy = dy

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.y > 720 or self.rect.x < 0 or self.rect.x > 1280:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class BossSkill(pygame.sprite.Sprite):
    def __init__(self, boss, all_sprites, enemy_bullets, cooldown=2000, skill_type="shoot"):
        super().__init__()
        self.boss = boss
        self.all_sprites = all_sprites
        self.enemy_bullets = enemy_bullets
        self.cooldown = cooldown
        self.skill_type = skill_type
        self.last_cast = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if not self.boss.alive():
            self.kill()
            return
        if now - self.last_cast >= self.cooldown:
            self.cast()
            self.last_cast = now

    def cast(self):
        if self.skill_type == "shoot":
            # Bắn 15 viên ngẫu nhiên từ boss
            for _ in range(5):
                bx = self.boss.rect.centerx + random.randint(-80, 80)  # tản rộng hơn
                by = self.boss.rect.bottom
                bullet = BossBullet(bx, by, dy=2)  # tốc độ đạn chậm lại (dy=2)
                self.all_sprites.add(bullet)
                self.enemy_bullets.add(bullet)
        elif self.skill_type == "wide":
            # Bắn đạn diện rộng: 15 viên
            for dx in [-7,-5,-3,-2,-1,0,1,2,3,5,7,6,-6,4,-4][:15]:  # 15 hướng khác nhau
                bullet = BossBullet(self.boss.rect.centerx, self.boss.rect.bottom, dx=dx, dy=2)
                self.all_sprites.add(bullet)
                self.enemy_bullets.add(bullet)


# =========================
# SKILL MANAGER (player skills)
# =========================
class SkillManager:
    def __init__(self, player, all_sprites, enemies=None, enemy_bullets=None, width=1280, height=720):
        self.player = player
        self.all_sprites = all_sprites
        self.enemies = enemies if enemies else pygame.sprite.Group()
        self.enemy_bullets = enemy_bullets if enemy_bullets else pygame.sprite.Group()
        self.width = width
        self.height = height

        # cooldowns in ms
        self.cooldowns = {1:5000,2:7000,3:30000}
        self.last_used = {1:0,2:0,3:0}

        # load icons
        self.skill_icons = {}
        for i, name in enumerate(["shield","bomb","lightning"], start=1):
            path = f"assets/images/{name}.png"
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.skill_icons[i] = pygame.transform.scale(img,(48,48))
            else:
                surf = pygame.Surface((48,48), pygame.SRCALPHA)
                pygame.draw.rect(surf,(150,150,150),(0,0,48,48))
                self.skill_icons[i] = surf

        # Damage values
        self.data = {
            "skills": {
                1: {"damage": 0},   # shield không gây damage
                2: {"damage": 5},  # bomb damage
                3: {"damage": 50}   # lightning damage
            }
        }

    # ------------------------------
    # Handle key input
    # ------------------------------
    def handle_input(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        # Skill 1 — Shield
        if keys[pygame.K_1] and now - self.last_used[1] > self.cooldowns[1]:
            eff = SkillEffect(
                image_path="assets/images/shield.png",
                follow_player=self.player,
                scale=(140,140),
                duration=2500,
                enemy_bullets=self.enemy_bullets,
                skill_type=1
            )
            self.all_sprites.add(eff)
            self.last_used[1] = now

        # Skill 2 — Bomb
        if keys[pygame.K_2] and now - self.last_used[2] > self.cooldowns[2]:
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255,120,0,140),
                               (self.width//2,self.height//2), self.height//2)
            eff = SkillEffect(custom_surface=surf,
                              pos=(self.width//2,self.height//2),
                              duration=900,
                              skill_type=2)
            self.all_sprites.add(eff)
            self.last_used[2] = now

        # Skill 3 — Lightning
        if keys[pygame.K_3] and now - self.last_used[3] > self.cooldowns[3]:
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(surf,(160,210,255,200),(0,0,self.width,self.height))
            eff = SkillEffect(custom_surface=surf,
                              pos=(self.width//2,self.height//2),
                              duration=600,
                              skill_type=3)
            self.all_sprites.add(eff)
            self.last_used[3] = now

    # ------------------------------
    # Apply damage correctly
    # ------------------------------
    def apply_damage(self, enemy, skill_effect):
        stype = skill_effect.skill_type
        dmg = self.data["skills"][stype]["damage"]

        if stype == 1:  # shield không gây damage
            return

        # bomb/lightning chỉ đánh trúng 1 lần mỗi enemy
        if skill_effect.hit_once is not None:
            if enemy in skill_effect.hit_once:
                return
            skill_effect.hit_once.add(enemy)

        if hasattr(enemy,"hp"):
            enemy.hp -= dmg
            if enemy.hp <= 0:
                enemy.kill()
        else:
            enemy.kill()

    # ------------------------------
    # Draw skill icons
    # ------------------------------
    def draw_skill_icons(self, screen):
        font = pygame.font.Font(None,24)
        now = pygame.time.get_ticks()

        for i, icon in self.skill_icons.items():
            x = 20 + (i-1)*70
            y = screen.get_height() - 70

            screen.blit(icon,(x,y))

            cooldown = self.cooldowns[i]
            elapsed = now - self.last_used[i]
            ratio = min(1, elapsed / cooldown)

            # background bar
            pygame.draw.rect(screen,(80,80,80),(x, y+52, 48, 6))
            # progress bar
            pygame.draw.rect(screen,(0,200,255),(x, y+52, int(48*ratio), 6))

            # countdown text
            if ratio < 1:
                remain = max(0, (cooldown - elapsed)//1000)
                txt = font.render(str(remain),True,(255,255,255))
                screen.blit(txt, (x+16, y+10))
