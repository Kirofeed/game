# main.py
import os
import sys
import json
import pygame

from config import (
    screen, screen_width, screen_height, debug_mode, scale_factor, music_on, sound_on, 
    key_bindings, difficulty_levels, heart_sprite_path
)
import config  # Для обновления переменных конфигурации
from player import Player
from coin import Coin
from portal import Portal
from heart import Heart  # Импортируем класс Heart
from sprites import load_images
from sounds import (
    load_sounds, play_sound, stop_sound, play_music, stop_music
)
from platform_loader import load_sprite_positions
from hud import draw_hud
from menu import (
    draw_menu, handle_menu_click, draw_settings_menu, 
    handle_settings_click, change_key, draw_end_screen, 
    Get_high_graphics_on
)
from background import draw_background, background_image
from start_screen import start_screen, draw_death_screen

pygame.init()
clock = pygame.time.Clock()

# Загрузка спрайта сердечка
try:
    heart_image = pygame.image.load(heart_sprite_path).convert_alpha()
    heart_image = pygame.transform.scale(heart_image, (50, 50))
    print("Heart sprite loaded successfully")
except pygame.error as e:
    print(f"Failed to load heart sprite: {e}")
    pygame.quit()
    sys.exit()

# Показ стартового окна
selected_difficulty = start_screen()
if selected_difficulty:
    config.current_difficulty = selected_difficulty
    config.current_health = difficulty_levels[config.current_difficulty]
else:
    pygame.quit()
    sys.exit()

animations = load_images('sprites', scale_factor)
sounds = load_sounds('sounds')

level = 1
levels = {
    1: "map_kirill",
    2: "map_danik",
    3: "map_vika",
    4: "map_stas"
}

if music_on:
    play_music(os.path.join('sounds', 'background_music.mp3'))

player_cords = 0
player_death_line = 0
collected_coins = {level: [] for level in levels}  # Для отслеживания собранных монеток

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
portals = pygame.sprite.Group()
platforms_passive_group = pygame.sprite.Group()
coins = pygame.sprite.Group()
hearts = pygame.sprite.Group()
player = Player(animations, sounds, 0, 0, screen_width, screen_height, 2)


def reset_player():
    global level, temp_coin
    level = 1
    config.current_health = difficulty_levels[config.current_difficulty]
    temp_coin = 0
    config.score = 0
    create_map()
    update_hearts()


def load_all_sprites(directory, scale_factor=3):
    sprites_coin = {}
    supported_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}

    for img_file in os.listdir(directory):
        img_path = os.path.join(directory, img_file)
        _, ext = os.path.splitext(img_file)
        if ext.lower() in supported_extensions:
            try:
                image = pygame.image.load(img_path).convert_alpha()
                if scale_factor != 1:
                    width, height = image.get_size()
                    image = pygame.transform.scale(
                        image, (int(width * scale_factor), int(height * scale_factor))
                    )
                sprites_coin[os.path.splitext(img_file)[0]] = image
            except pygame.error as e:
                print(f"Could not load image {img_file}: {e}")

    return sprites_coin


def create_map():
    global player, player_cords, player_death_line, temp_coin
    temp_coin = 0
    all_sprites.empty()
    platforms.empty()
    platforms_passive_group.empty()
    coins.empty()
    portals.empty()
    hearts.empty()

    with open(f"maps/{levels[level]}.json", 'r') as f:
        data = json.load(f)
    
    player_cords = data['player_spawn']
    player_death_line = data["death_line"]["y_d"]

    load_sprite_positions(
        f'{levels[level]}.json', platforms, screen_height, 
        platforms_passive_group, levels[level]
    )
    player = Player(
        animations, sounds, player_cords["x"], player_cords["y"], 
        screen_width, screen_height, 2
    )

    all_sprites.add(platforms)
    all_sprites.add(platforms_passive_group)
    all_sprites.add(player)

    all_sprites_dict = load_all_sprites('img/coin_sprites', 3)
    if not all_sprites_dict:
        print("Error: No sprites loaded.")
        return

    coin_animations = [
        all_sprites_dict[key] for key in sorted(all_sprites_dict.keys()) if 'coin' in key.lower()
    ]

    for coin_data in data.get("coins", []):
        coin = Coin(coin_data["x"], coin_data["y"], coin_animations)
        coins.add(coin)
        all_sprites.add(coin)

    portal_image = pygame.image.load('img/portal_open.png').convert_alpha()
    width, height = portal_image.get_size()
    portal_image = pygame.transform.scale(portal_image, (int(width * 3), int(height * 3)))

    for portal_data in data.get("portals", []):
        portal = Portal(portal_data["x"], portal_data["y"], portal_image)
        portals.add(portal)
        all_sprites.add(portal)

    if Get_high_graphics_on():
        all_sprites.remove(player)
        all_sprites.add(*platforms_passive_group)
        all_sprites.add(player)


def update_hearts():
    hearts.empty()
    for i in range(config.current_health):
        heart = Heart(heart_image, 10 + i * (heart_image.get_width() + 5), 40)
        hearts.add(heart)
        all_sprites.add(heart)


create_map()
update_hearts()

running = True
paused = False
menu_active = False
settings_active = False
end_game_active = False
death_screen_active = False
was_sprinting = False
was_walking = False
key_changing = None

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if menu_active:
                if event.key == pygame.K_ESCAPE:
                    menu_active = False
                elif event.key == pygame.K_q:
                    running = False
            elif settings_active:
                if event.key == pygame.K_ESCAPE:
                    settings_active = False
                    menu_active = True
                else:
                    key_changing = change_key(event, key_changing, key_bindings)
            elif event.key == pygame.K_ESCAPE:
                menu_active = not menu_active
            elif event.key == pygame.K_q and end_game_active:
                running = False
            elif event.key == pygame.K_q and death_screen_active:
                running = False
            elif event.key == pygame.K_RETURN and death_screen_active:
                selected_difficulty = start_screen()
                if selected_difficulty:
                    config.current_difficulty = selected_difficulty
                    config.current_health = difficulty_levels[config.current_difficulty]
                    death_screen_active = False
                    reset_player()
                    update_hearts()
                else:
                    running = False
            elif event.key == pygame.K_g and debug_mode:
                level += 1
                if level != 5:
                    create_map()
                    update_hearts()
                else:
                    end_game_active = True
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if menu_active:
                result = handle_menu_click(event.pos, player)
                if result == "settings":
                    menu_active = False
                    settings_active = True
                elif result == "restart":
                    reset_player()
                    update_hearts()
                    menu_active = False
                elif result == "graphics":
                    all_sprites.remove(*platforms_passive_group)
                    if Get_high_graphics_on():
                        all_sprites.remove(player)
                        all_sprites.add(*platforms_passive_group)
                        all_sprites.add(player)

            elif settings_active:
                result = handle_settings_click(event.pos, key_changing)
                if result == "menu":
                    settings_active = False
                    menu_active = True
                else:
                    key_changing = result

    if player.rect.bottom >= player_death_line:
        config.current_health -= 1
        config.score -= temp_coin
        temp_coin = 0
        if config.current_health > 0:
            create_map()
            update_hearts()
        else:
            death_screen_active = True

    if death_screen_active:
        draw_death_screen(screen)
        pygame.display.flip()
        continue

    if end_game_active:
        draw_end_screen(screen, config.score)
        pygame.display.flip()
        continue

    if menu_active:
        screen.fill((0, 0, 0))
        draw_menu(screen)
        pygame.display.flip()
        continue

    if settings_active:
        screen.fill((0, 0, 0))
        draw_settings_menu(screen, key_bindings, key_changing)
        pygame.display.flip()
        continue

    keys = pygame.key.get_pressed()
    sprinting = keys[key_bindings["sprint"]]
    is_moving = False

    if keys[key_bindings["left"]]:
        player.move_left(platforms, sprinting)
        is_moving = True
    elif keys[key_bindings["right"]]:
        player.move_right(platforms, sprinting)
        is_moving = True
    else:
        if player.is_walking:
            stop_sound(sounds, 'walk')
            stop_sound(sounds, 'sprint')
            player.is_walking = False
        if player.on_ground:
            player.change_animation(f"idle_{player.direction}")
        player.reset_animation_speed()

    if keys[key_bindings["jump"]]:
        if player.on_ground:
            player.jump(sprinting)
            stop_sound(sounds, 'walk')
            stop_sound(sounds, 'sprint')
            if player.sounds_on:
                play_sound(sounds, 'jump')

    if is_moving and player.on_ground:
        if sprinting:
            if not was_sprinting:
                stop_sound(sounds, 'walk')
                if player.sounds_on:
                    play_sound(sounds, 'sprint', -1)
                was_sprinting = True
            was_walking = False
        else:
            if was_sprinting:
                stop_sound(sounds, 'sprint')
                if player.sounds_on:
                    play_sound(sounds, 'walk', -1)
                was_sprinting = False
            elif not was_walking:
                if player.sounds_on:
                    play_sound(sounds, 'walk', -1)
                was_walking = True
        player.is_walking = True
    else:
        was_sprinting = False
        was_walking = False

    platforms_passive_group.update()
    player.update(dt, platforms)
    platforms.update()

    coins.update()
    portals.update()

    collected_coins = pygame.sprite.spritecollide(player, coins, dokill=True)
    temp_coin += len(collected_coins)
    config.score += len(collected_coins)

    if pygame.sprite.spritecollideany(player, portals):
        level += 1
        temp_coin = 0
        if level != 5:
            create_map()
            update_hearts()
        else:
            end_game_active = True

    draw_background(screen, background_image, screen_width)
    all_sprites.draw(screen)

    if debug_mode:
        for sprite in all_sprites:
            if hasattr(sprite, 'rect'):
                pygame.draw.rect(screen, (255, 0, 0), sprite.rect, 1)

    draw_hud(screen, heart_image)

    pygame.display.flip()

pygame.quit()
sys.exit()
