import pygame
import os
from config import sound_on

def load_sounds(sound_dir):
    """
    Загружает звуковые файлы из указанной директории.

    :param sound_dir: Директория с звуковыми файлами.
    :return: Словарь загруженных звуков.
    """
    sounds = {}
    for sound_file in os.listdir(sound_dir):
        if sound_file.endswith(('.wav', '.mp3')):
            sound_path = os.path.join(sound_dir, sound_file)
            sound_name = os.path.splitext(sound_file)[0]
            sounds[sound_name] = pygame.mixer.Sound(sound_path)
    return sounds

def play_sound(sounds, sound_name, loops=0):
    """
    Проигрывает указанный звук, если он загружен и звук включен.

    :param sounds: Словарь загруженных звуков.
    :param sound_name: Имя звука для проигрывания.
    :param loops: Количество повторов (по умолчанию 0).
    """
    if sound_on:
        if sound_name in sounds:
            sounds[sound_name].play(loops=loops)
            print(f"Playing sound: {sound_name}")
        else:
            print(f"Sound '{sound_name}' not found in loaded sounds.")
    else:
        print(f"Sound is disabled. Not playing: {sound_name}")

def stop_sound(sounds, sound_name):
    """
    Останавливает проигрывание указанного звука, если он загружен.

    :param sounds: Словарь загруженных звуков.
    :param sound_name: Имя звука для остановки.
    """
    if sound_name in sounds:
        sounds[sound_name].stop()
    else:
        print(f"Sound '{sound_name}' not found in loaded sounds.")

def play_music(music_file):
    """
    Проигрывает музыкальный файл в цикле.

    :param music_file: Путь к музыкальному файлу.
    """
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)

def stop_music():
    """
    Останавливает проигрывание музыки.
    """
    pygame.mixer.music.stop()
