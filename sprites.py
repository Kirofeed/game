import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, animations, x, y):
        super().__init__()
        self.animations = animations
        self.current_animation = "idle_idle_right"
        self.images = self.animations[self.current_animation]
        self.current_image = 0
        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.gravity = 0.5
        self.jump_power = -10
        self.on_ground = False

        self.animation_speed = 0.07  # скорость анимации в секундах на кадр
        self.animation_timer = 0

        self.direction = "right"  # направление игрока

    def update(self, dt):
        # Обновление анимации
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]

        # Обновление положения
        self.velocity.y += self.gravity
        self.rect.y += self.velocity.y

        # Обработка столкновения с землей
        if self.rect.bottom >= 600:  # screen_height должно быть передано или жестко закодировано
            self.rect.bottom = 600
            self.velocity.y = 0
            self.on_ground = True
            if self.current_animation.startswith("jump"):
                self.change_animation(f"idle_idle_{self.direction}")

        # Ограничение по горизонтали
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 800:  # screen_width должно быть передано или жестко закодировано
            self.rect.right = 800

    def move_left(self):
        self.rect.x -= 5
        if self.on_ground:
            self.direction = "left"
            self.change_animation("walk_walk_left")

    def move_right(self):
        self.rect.x += 5
        if self.on_ground:
            self.direction = "right"
            self.change_animation("walk_walk_right")

    def jump(self):
        if self.on_ground:
            self.velocity.y = self.jump_power
            self.on_ground = False
            self.change_animation(f"jump_jump_{self.direction}")

    def change_animation(self, animation):
        if self.current_animation != animation:
            self.current_animation = animation
            self.images = self.animations[self.current_animation]
            self.current_image = 0
            self.animation_timer = 0
            self.image = self.images[self.current_image]


def load_images(sprite_dir):
    animations = {}
    for animation in os.listdir(sprite_dir):
        animation_path = os.path.join(sprite_dir, animation)
        if os.path.isdir(animation_path):
            for sub_animation in os.listdir(animation_path):
                sub_animation_path = os.path.join(animation_path, sub_animation)
                if os.path.isdir(sub_animation_path):
                    frames = []
                    for img_file in sorted(os.listdir(sub_animation_path)):
                        img_path = os.path.join(sub_animation_path, img_file)
                        frames.append(pygame.image.load(img_path).convert_alpha())
                    animations[f"{animation}_{sub_animation}"] = frames
    print("Loaded animations:", animations.keys())  # Временный вывод ключей
    return animations