# src/ui/ui_name_input.py
import pygame

class NameInputUI:
    def __init__(self, screen, db=None):
        self.screen = screen
        self.db = db
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small = pygame.font.Font(None, 28)

    def run(self):
        name = ""
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if name.strip():
                            if self.db:
                                self.db.update_player_name(name.strip())
                            return name.strip()
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if len(name) < 16 and event.unicode.isprintable():
                            name += event.unicode

            self.screen.fill((10, 10, 20))
            prompt = self.font.render("Enter player name:", True, (0, 255, 255))
            self.screen.blit(prompt, prompt.get_rect(center=(self.screen.get_width() // 2, 200)))

            box = pygame.Rect(self.screen.get_width() // 2 - 200, 260, 400, 50)
            pygame.draw.rect(self.screen, (255, 255, 255), box, 2)
            txt = self.font.render(name or "_", True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(center=box.center))

            hint = self.small.render("Press Enter to confirm", True, (180, 180, 180))
            self.screen.blit(hint, (self.screen.get_width() // 2 - hint.get_width() // 2, box.bottom + 12))

            pygame.display.flip()
