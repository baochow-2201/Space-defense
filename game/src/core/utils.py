# src/core/utils.py
import os
import pygame

# ==============================================
# Thư mục gốc project
# ==============================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)  # vì utils.py nằm trong /src/core

# Alias dễ dùng
project_root = PROJECT_ROOT

# ==============================================
# Hàm trả đường dẫn tuyệt đối
# ==============================================
def asset_path(relative_path: str) -> str:
    """
    Trả về đường dẫn tuyệt đối tới thư mục assets
    """
    return os.path.join(PROJECT_ROOT, "assets", relative_path)

def image_path(filename: str) -> str:
    """Đường dẫn ảnh, tự động thêm 'images/' nếu cần"""
    if filename.startswith("images/"):
        return asset_path(filename)
    return asset_path(f"images/{filename}")

def sound_path(filename: str) -> str:
    """Đường dẫn âm thanh, tự động thêm 'sounds/' nếu cần"""
    if filename.startswith("sounds/"):
        return asset_path(filename)
    return asset_path(f"sounds/{filename}")

def video_path(filename: str) -> str:
    """Đường dẫn video, tự động thêm 'videos/' nếu cần"""
    if filename.startswith("videos/"):
        return asset_path(filename)
    return asset_path(f"videos/{filename}")

# ==============================================
# Load ảnh an toàn
# ==============================================
def safe_load_image(filename: str, scale=None) -> pygame.Surface:
    """
    Load ảnh từ assets/images/
    Nếu scale được truyền vào, resize ảnh
    """
    full_path = image_path(filename)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Image not found: {full_path}")

    image = pygame.image.load(full_path).convert_alpha()

    if scale:
        image = pygame.transform.scale(image, scale)

    return image

# ==============================================
# Load âm thanh an toàn
# ==============================================
def safe_load_sound(filename: str) -> pygame.mixer.Sound:
    """
    Load âm thanh từ assets/sounds/
    """
    full_path = sound_path(filename)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Sound not found: {full_path}")

    return pygame.mixer.Sound(full_path)

# ==============================================
# Kiểm tra video tồn tại
# ==============================================
def safe_video_path(filename: str) -> str:
    """
    Kiểm tra video tồn tại và trả đường dẫn tuyệt đối
    """
    full_path = video_path(filename)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Video not found: {full_path}")
    return full_path
