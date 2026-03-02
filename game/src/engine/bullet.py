# src/engine/bullet.py
import pygame


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=-10, damage=10, image=None, images=None):
        super().__init__()

        # Hỗ trợ animation nhiều ảnh
        self.images = images
        self.image_index = 0

        if self.images:
            self.image = self.images[0]
        elif image:
            self.image = image
        else:
            # Tạo viên đạn mặc định
            surf = pygame.Surface((6, 14), pygame.SRCALPHA)
            surf.fill((255, 255, 0))
            self.image = surf

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.damage = damage

    def update(self):
        # Di chuyển bullet
        self.rect.y += self.speed

        # Nếu có animation, update frame
        if self.images:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.image = self.images[self.image_index]

        # Kiểm tra giới hạn màn hình
        screen = pygame.display.get_surface()
        if screen:
            screen_h = screen.get_height()
            if self.rect.bottom < 0 or self.rect.top > screen_h:
                self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
