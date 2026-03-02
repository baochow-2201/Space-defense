# src/video/intro_player.py
import pygame
import cv2
from core.utils import video_path, sound_path

class IntroPlayer:
    def __init__(self, screen, video_filename="intro2.0.mp4", audio_filename="intro.mp3", fps=30):
        self.screen = screen
        self.video_path = video_path(video_filename)
        self.audio_path = sound_path(audio_filename)
        self.fps = fps
        self.clock = pygame.time.Clock()

    def run(self):
        # Play nhạc
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.play()
        except Exception:
            pass

        # Mở video
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.screen.get_width(), self.screen.get_height()))
            surface = pygame.surfarray.make_surface(frame)
            surface = pygame.transform.rotate(surface, -90)
            surface = pygame.transform.flip(surface, True, False)
            self.screen.blit(surface, (0,0))
            pygame.display.flip()
            self.clock.tick(self.fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    try:
                        pygame.mixer.music.stop()
                    except Exception:
                        pass
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    cap.release()
                    try:
                        pygame.mixer.music.stop()
                    except Exception:
                        pass
                    return

        cap.release()
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
