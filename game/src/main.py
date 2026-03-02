import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pygame.pkgdata')

import pygame
from core.database import Database
from ui.ui_name_input import NameInputUI
from ui.ui_menu import MenuUI
from ui.ui_level import LevelUI
from video.intro_player import IntroPlayer
from core.utils import sound_path
from core.settings import WIDTH, HEIGHT, TITLE
from game import Game

def play_intro(screen):
    try:
        intro = IntroPlayer(screen, video_filename="intro2.0.mp4", audio_filename="intro.mp3")
        intro.run()
    except Exception as e:
        print(f"Intro skipped: {e}")

def play_background_music():
    try:
        pygame.mixer.init()
        bgm_file = sound_path("background.mp3")
        pygame.mixer.music.load(bgm_file)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"BGM skipped: {e}")

def stop_music():
    try:
        pygame.mixer.music.stop()
    except:
        pass

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)

    db = Database()

    # Intro
    play_intro(screen)

    # --- Nhập tên người chơi nếu là lần đầu ---
    player = db.get_player()
    if player["name"] == "Player":
        name_ui = NameInputUI(screen, db)
        player_name = name_ui.run()
    else:
        player_name = player["name"]

    print("Logged in as:", player_name)
    # Lấy người chơi
    player_data = db.get_player_data()
    if player_data is None or not player_data.get("name"):
        name_ui = NameInputUI(screen, db)
        player_name = name_ui.run()
    else:
        player_name = player_data["name"]

    # Nhạc nền
    play_background_music()

    # Menu chính
    while True:
        menu = MenuUI(screen, db, player_name)
        action = menu.run()

        # Cập nhật tên sau menu
        player_name = menu.player_name

        if action == "exit":
            break

        elif action == "load":
            pass

        elif action == "start":
            stop_music()

            # Chọn level
            level_ui = LevelUI(screen, max_level=10)
            selected_level = level_ui.run()

            # Chơi game
            game = Game(screen, player_name, level=selected_level)
            game.run()

            # Không save score ở đây nữa – Game lớp tự lo rồi

            # Nhạc nền lại
            play_background_music()

    pygame.quit()

if __name__ == "__main__":
    main()
