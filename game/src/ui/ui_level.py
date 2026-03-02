# src/ui/ui_level.py
import pygame
import random

class LevelButton:
    def __init__(self, text, x, y, w=150, h=50):
        self.text = text
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)
        self.base_color = (40,40,90)
        self.hover_color = (0,200,255)
        self.glow_alpha = 0

    def draw(self, screen, font, mouse_pos):
        hover = self.rect.collidepoint(mouse_pos)
        self.glow_alpha = min(255, self.glow_alpha+15) if hover else max(0, self.glow_alpha-15)
        glow = pygame.Surface((self.rect.w+20, self.rect.h+20), pygame.SRCALPHA)
        pygame.draw.rect(glow, (0,200,255,self.glow_alpha), glow.get_rect(), border_radius=12)
        screen.blit(glow, (self.rect.x-10, self.rect.y-10))
        color = self.hover_color if hover else self.base_color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        label = font.render(self.text, True, (255,255,255))
        screen.blit(label, label.get_rect(center=self.rect.center))
        return hover

class LevelUI:
    def __init__(self, screen, max_level=10):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.max_level = max_level
        self.font_title = pygame.font.Font(None, 72)
        self.font_item = pygame.font.Font(None, 36)

        margin_x = 120
        margin_y = 200
        gap_x = (screen.get_width() - 2*margin_x) // 4
        gap_y = 90

        self.buttons = []
        for i in range(max_level):
            row = i // 5
            col = i % 5
            x = margin_x + col * gap_x
            y = margin_y + row * gap_y
            self.buttons.append(LevelButton(f"Level {i+1}", x, y))

        self.stars = [{"x": random.randint(0, screen.get_width()),
                       "y": random.randint(0, screen.get_height()),
                       "speed": random.randint(1,4),
                       "size": random.randint(1,3)} for _ in range(120)]

    def run(self):
        while True:
            self.clock.tick(60)
            mx, my = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()[0]
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.screen.fill((5,5,20))
            for s in self.stars:
                pygame.draw.circle(self.screen, (255,255,255), (s["x"], s["y"]), s["size"])
                s["y"] += s["speed"]
                if s["y"] > self.screen.get_height():
                    s["y"] = 0
                    s["x"] = random.randint(0, self.screen.get_width())

            title = self.font_title.render("SELECT LEVEL", True, (0,255,255))
            self.screen.blit(title, title.get_rect(center=(self.screen.get_width()//2, 100)))

            for i, btn in enumerate(self.buttons):
                btn.draw(self.screen, self.font_item, (mx,my))
                if btn.rect.collidepoint(mx,my) and click:
                    return i+1

            pygame.display.flip()
