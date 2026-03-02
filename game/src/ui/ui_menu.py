# src/ui/ui_menu.py

import pygame
from ui.ui_name_input import NameInputUI
from ui.ui_profile import ProfileUI
import random

class MenuButton:
    def __init__(self, text, x, y, w=300, h=60):
        self.text = text
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)
        self.base_color = (40, 40, 90)
        self.hover_color = (0, 200, 255)
        self.glow = 0

    def draw(self, screen, font, mouse_pos):
        hover = self.rect.collidepoint(mouse_pos)
        self.glow = min(255, self.glow+15) if hover else max(0, self.glow-15)
        glow_surf = pygame.Surface((self.rect.w+20, self.rect.h+20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (0, 200, 255, self.glow), glow_surf.get_rect(), border_radius=12)
        screen.blit(glow_surf, (self.rect.x-10, self.rect.y-10))
        color = self.hover_color if hover else self.base_color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        label = font.render(self.text, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=self.rect.center))
        return hover

class MenuUI:
    def __init__(self, screen, db, player_name):
        self.screen = screen
        self.db = db
        self.player_data = self.db.get_player()
        self.player_name = player_name or self.player_data["name"]
        self.clock = pygame.time.Clock()
        cx = screen.get_width() // 2

        # Chỉ còn Start / Load / Exit
        self.buttons = [
            MenuButton("Start Game", cx, 250),
            MenuButton("Load Game", cx, 340),
            MenuButton("Exit", cx, 430)
        ]

        self.font_title = pygame.font.Font(None, 72)
        self.font_item = pygame.font.Font(None, 48)

        # Background stars
        self.stars = [{"x": random.randint(0, screen.get_width()),
                       "y": random.randint(0, screen.get_height()),
                       "speed": random.randint(1,4),
                       "size": random.randint(1,3)} for _ in range(120)]
        self.music_on = True

        # Profile UI
        self.profile_ui = ProfileUI(screen, db, self.player_name)
        self.profile_icon_rect = pygame.Rect(screen.get_width()-70, 20, 50, 50)

    # Chỉ phần run() được cải tiến
    def run(self):
        while True:
            self.clock.tick(60)
            mx, my = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()[0]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Background stars
            self.screen.fill((5, 5, 20))
            for s in self.stars:
                pygame.draw.circle(self.screen, (255, 255, 255), (s["x"], s["y"]), s["size"])
                s["y"] += s["speed"]
                if s["y"] > self.screen.get_height():
                    s["y"] = 0

            # Title
            title = self.font_title.render("SPACE DEFENDER", True, (0, 255, 255))
            self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, 120)))

            # Player name
            name_surf = self.font_item.render(self.player_name, True, (0, 255, 255))
            self.screen.blit(name_surf, (self.screen.get_width() - 220, 20))

            # Draw buttons
            for btn in self.buttons:
                hovered = btn.draw(self.screen, self.font_item, (mx, my))
                if hovered and click:
                    if btn.text == "Start Game":
                        player = self.db.get_player()
                        if not player:
                            name_ui = NameInputUI(self.screen, self.db)
                            name_ui.run()
                        return "start"
                    elif btn.text == "Load Game":
                        return "load"
                    elif btn.text == "Exit":
                        return "exit"

            # Profile button with hover glow
            profile_hover = self.profile_icon_rect.collidepoint(mx, my)
            glow_val = 150 if profile_hover else 0
            glow_surf = pygame.Surface((self.profile_icon_rect.w + 10, self.profile_icon_rect.h + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (0, 200, 255, glow_val), glow_surf.get_rect(), border_radius=8)
            self.screen.blit(glow_surf, (self.profile_icon_rect.x - 5, self.profile_icon_rect.y - 5))

            pygame.draw.rect(self.screen, (100, 100, 255), self.profile_icon_rect)
            profile_label = self.font_item.render("P", True, (255, 255, 255))
            self.screen.blit(profile_label, profile_label.get_rect(center=self.profile_icon_rect.center))

            if profile_hover and click:
                self.profile_ui.toggle()
                self.profile_ui.run()
                self.player_name = self.profile_ui.player_name  # cập nhật tên mới

            # Music icon with hover glow
            icon_rect = pygame.Rect(self.screen.get_width() - 60, self.screen.get_height() - 60, 40, 40)
            music_hover = icon_rect.collidepoint(mx, my)
            glow_val = 150 if music_hover else 0
            glow_surf = pygame.Surface((icon_rect.w + 10, icon_rect.h + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (0, 200, 255, glow_val), glow_surf.get_rect(), border_radius=5)
            self.screen.blit(glow_surf, (icon_rect.x - 5, icon_rect.y - 5))

            # Music icon draw
            if self.music_on:
                pygame.draw.polygon(self.screen, (0, 255, 255),
                                    [(icon_rect.left, icon_rect.centery - 8),
                                     (icon_rect.left + 12, icon_rect.centery - 8),
                                     (icon_rect.left + 22, icon_rect.top),
                                     (icon_rect.left + 22, icon_rect.bottom),
                                     (icon_rect.left + 12, icon_rect.centery + 8),
                                     (icon_rect.left, icon_rect.centery + 8)])
            else:
                pygame.draw.polygon(self.screen, (255, 0, 0),
                                    [(icon_rect.left, icon_rect.centery - 8),
                                     (icon_rect.left + 12, icon_rect.centery - 8),
                                     (icon_rect.left + 22, icon_rect.top),
                                     (icon_rect.left + 22, icon_rect.bottom),
                                     (icon_rect.left + 12, icon_rect.centery + 8),
                                     (icon_rect.left, icon_rect.centery + 8)])
                pygame.draw.line(self.screen, (255, 0, 0), (icon_rect.left, icon_rect.top),
                                 (icon_rect.right, icon_rect.bottom), 3)

            if music_hover and click:
                if self.music_on:
                    try:
                        pygame.mixer.music.pause()
                    except:
                        pass
                    self.music_on = False
                else:
                    try:
                        pygame.mixer.music.unpause()
                    except:
                        pass
                    self.music_on = True

            pygame.display.flip()
