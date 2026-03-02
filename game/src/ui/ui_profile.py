# src/ui/ui_profile.py
import pygame
from core.database import Database

class ProfileUI:
    def __init__(self, screen, db, player_name):
        self.screen = screen
        self.db = db
        self.visible = False
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()

        # Player info
        self.player_name = player_name
        self.load_player_data()

        # Input for changing name
        self.editing_name = False
        self.input_name = self.player_name

        # Profile window
        self.width = 450
        self.height = 550
        self.rect = pygame.Rect(
            self.screen.get_width()//2 - self.width//2,
            self.screen.get_height()//2 - self.height//2,
            self.width,
            self.height
        )

        # Reset button
        self.reset_btn_rect = pygame.Rect(self.rect.x + 50, self.rect.bottom - 100, 350, 50)
        self.reset_glow = 0

    def load_player_data(self):
        self.player_data = self.db.get_player_data()
        self.level_scores = self.player_data.get("level_scores", {})
        self.total_score = self.player_data.get("total_score", 0)

    def toggle(self):
        self.visible = not self.visible
        self.load_player_data()  # Reload data every time mở profile

    def run(self):
        while self.visible:
            dt = self.clock.tick(60)
            mx, my = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()[0]

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif e.type == pygame.KEYDOWN:
                    if self.editing_name:
                        if e.key == pygame.K_RETURN:
                            # Update name in DB
                            self.player_name = self.input_name.strip() or "Player"
                            self.db.update_player_name(self.player_name)
                            self.editing_name = False
                        elif e.key == pygame.K_BACKSPACE:
                            self.input_name = self.input_name[:-1]
                        else:
                            if len(self.input_name) < 16 and e.unicode.isprintable():
                                self.input_name += e.unicode
                    elif e.key == pygame.K_ESCAPE:
                        self.visible = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    # Click on name box to edit
                    name_box = pygame.Rect(self.rect.x + 50, self.rect.y + 50, 350, 40)
                    if name_box.collidepoint(mx, my):
                        self.editing_name = True
                    # Click reset button
                    if self.reset_btn_rect.collidepoint(mx, my):
                        self.db.reset_scores()
                        self.load_player_data()

            self.draw(mx, my)  # truyền cả mx, my để kiểm tra hover
            pygame.display.flip()

    def draw(self, mx, my):
        # Semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0,0))

        # Window background
        pygame.draw.rect(self.screen, (20,20,50), self.rect, border_radius=12)
        pygame.draw.rect(self.screen, (200,200,255), self.rect, 3, border_radius=12)

        # Avatar
        avatar_rect = pygame.Rect(self.rect.x + self.width//2 - 50, self.rect.y + 110, 100, 100)
        pygame.draw.circle(self.screen, (100,200,255), avatar_rect.center, 50)
        self.screen.blit(self.small_font.render("Avatar", True, (255,255,255)),
                         (avatar_rect.centerx - 30, avatar_rect.centery - 10))

        # Name box
        name_box = pygame.Rect(self.rect.x + 50, self.rect.y + 50, 350, 40)
        pygame.draw.rect(self.screen, (255,255,255), name_box, 2)
        display_name = self.input_name if self.editing_name else self.player_name
        txt_color = (0,255,0) if self.editing_name else (255,255,255)
        name_surf = self.font.render(display_name or "_", True, txt_color)
        self.screen.blit(name_surf, (name_box.x + 5, name_box.y + 5))

        # Total score
        ts_surf = self.font.render(f"Total Score: {self.total_score}", True, (255,255,0))
        self.screen.blit(ts_surf, (self.rect.x + 50, self.rect.y + 230))

        # Level scores
        self.screen.blit(self.small_font.render("Level Scores:", True, (200,200,200)),
                         (self.rect.x + 50, self.rect.y + 270))
        y_offset = 300
        for lvl in sorted(self.level_scores.keys()):
            score = self.level_scores[lvl]
            s = self.small_font.render(f"Level {lvl}: {score}", True, (255,255,255))
            self.screen.blit(s, (self.rect.x + 60, self.rect.y + y_offset))
            y_offset += 30

        # Reset Score button với hiệu ứng hover
        hover = self.reset_btn_rect.collidepoint(mx, my)
        self.reset_glow = min(255, self.reset_glow+15) if hover else max(0, self.reset_glow-15)
        glow_surf = pygame.Surface((self.reset_btn_rect.w+20, self.reset_btn_rect.h+20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255,100,100, self.reset_glow), glow_surf.get_rect(), border_radius=12)
        self.screen.blit(glow_surf, (self.reset_btn_rect.x-10, self.reset_btn_rect.y-10))

        color = (255,50,50) if hover else (200,0,0)
        pygame.draw.rect(self.screen, color, self.reset_btn_rect, border_radius=8)
        txt = self.font.render("RESET SCORE", True, (255,255,255))
        self.screen.blit(txt, (self.reset_btn_rect.x + self.reset_btn_rect.width//2 - txt.get_width()//2,
                               self.reset_btn_rect.y + self.reset_btn_rect.height//2 - txt.get_height()//2))

        # Instructions
        instr_surf = self.small_font.render("Click name to edit, Enter to save, ESC to close", True, (180,180,180))
        self.screen.blit(instr_surf, (self.rect.x + 20, self.rect.bottom - 40))
