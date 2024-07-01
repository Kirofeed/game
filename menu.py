import pygame
from config import font, screen_width, screen_height


def draw_menu(screen, music_on, sounds_on):
    menu_text = font.render("Menu", True, (255, 255, 255))
    quit_text = font.render("Press Q to Quit", True, (255, 255, 255))
    music_text = font.render("Music", True, (255, 255, 255))
    sounds_text = font.render("Sounds", True, (255, 255, 255))

    # Определяем координаты для кнопок
    music_box = pygame.Rect(screen_width // 2 + 50, screen_height // 2 - 23 - music_text.get_height() // 2, 20, 20)
    sounds_box = pygame.Rect(screen_width // 2 + 50, screen_height // 2 + 17 - sounds_text.get_height() // 2, 20, 20)

    screen.blit(menu_text,
                (screen_width // 2 - menu_text.get_width() // 2, screen_height // 2 - menu_text.get_height() // 2 - 80))
    screen.blit(music_text, (
    screen_width // 2 - music_text.get_width() // 2 - 50, screen_height // 2 - 30 - music_text.get_height() // 2))
    screen.blit(sounds_text, (
    screen_width // 2 - sounds_text.get_width() // 2 - 50, screen_height // 2 + 10 - sounds_text.get_height() // 2))

    pygame.draw.rect(screen, (255, 255, 255), music_box, 3)
    pygame.draw.rect(screen, (255, 255, 255), sounds_box, 3)

    if music_on:
        pygame.draw.line(screen, (255, 255, 255), (music_box.left + 3, music_box.top + 3),
                         (music_box.right - 3, music_box.bottom - 3), 3)
        pygame.draw.line(screen, (255, 255, 255), (music_box.right - 3, music_box.top + 3),
                         (music_box.left + 3, music_box.bottom - 3), 3)

    if sounds_on:
        pygame.draw.line(screen, (255, 255, 255), (sounds_box.left + 3, sounds_box.top + 3),
                         (sounds_box.right - 3, sounds_box.bottom - 3), 3)
        pygame.draw.line(screen, (255, 255, 255), (sounds_box.right - 3, sounds_box.top + 3),
                         (sounds_box.left + 3, sounds_box.bottom - 3), 3)

    screen.blit(quit_text,
                (screen_width // 2 - quit_text.get_width() // 2, screen_height // 2 - quit_text.get_height() // 2 + 60))

    return music_box, sounds_box
