import pygame
import os
from sounds import play_sound

class Player(pygame.sprite.Sprite):
    def __init__(self, animations, sounds, x, y, screen_width, screen_height, scale_factor):
        super().__init__()
        self.animations = animations
        self.sounds = sounds
        self.current_animation = "idle_right"
        self.images = self.animations[self.current_animation]
        self.current_image = 0
        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.gravity = 0.5
        self.jump_power = -10
        self.on_ground = False
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.animation_speed = 0.14
        self.animation_timer = 0
        self.direction = "right"
        self.walk_speed = 5
        self.sprint_multiplier = 1.7
        self.jump_multiplier = 1.3
        self.normal_animation_speed = 0.14
        self.sprint_animation_speed = self.normal_animation_speed / 2
        self.is_walking = False
        self.sounds_on = True  # Добавим этот атрибут

    def update(self, dt, platforms):
        # Обновление анимации
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]

        # Обновление положения
        self.velocity.y += self.gravity
        self.rect.y += self.velocity.y
        self.on_ground = False

        # Проверка столкновения с платформами
        collisions = pygame.sprite.spritecollide(self, platforms, False)

        for platform in collisions:
            if self.velocity.y > 0:
                # Обработка коллизий по вертикали (падение на платформу)
                self.rect.bottom = platform.rect.top
                self.velocity.y = 0
                self.on_ground = True
            elif self.velocity.y < 0:
                # Обработка коллизий по вертикали (удар головой о платформу)
                self.rect.top = platform.rect.bottom
                self.velocity.y = 0

        # Ограничение по горизонтали
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width

        # Ограничение по вертикали
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height
            self.on_ground = True

    def move_left(self, platforms, sprinting):
        speed = self.walk_speed * self.sprint_multiplier if sprinting else self.walk_speed
        self.rect.x -= speed
        self.animation_speed = self.sprint_animation_speed if sprinting else self.normal_animation_speed

        collisions = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collisions:
            if self.rect.colliderect(platform.rect):
                self.rect.left = platform.rect.right
        self.direction = "left"
        if self.on_ground:
            if sprinting:
                self.change_animation("sprint_left")
            else:
                self.change_animation("walk_left")
        else:
            self.change_animation("jump_left")

    def move_right(self, platforms, sprinting):
        speed = self.walk_speed * self.sprint_multiplier if sprinting else self.walk_speed
        self.rect.x += speed
        self.animation_speed = self.sprint_animation_speed if sprinting else self.normal_animation_speed

        collisions = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collisions:
            if self.rect.colliderect(platform.rect):
                self.rect.right = platform.rect.left
        self.direction = "right"
        if self.on_ground:
            if sprinting:
                self.change_animation("sprint_right")
            else:
                self.change_animation("walk_right")
        else:
            self.change_animation("jump_right")

    def jump(self, sprinting=False):
        jump_power = self.jump_power * self.jump_multiplier if sprinting else self.jump_power
        if self.on_ground:
            self.velocity.y = jump_power
            self.on_ground = False
            self.change_animation(f"jump_{self.direction}")
            if self.sounds_on:  # Проверка звукового флага
                play_sound(self.sounds, 'jump')

    def change_animation(self, animation):
        if self.current_animation != animation:
            self.current_animation = animation
            self.images = self.animations[self.current_animation]
            self.current_image = 0
            self.animation_timer = 0
            self.image = self.images[self.current_image]

    def reset_animation_speed(self):
        self.animation_speed = self.normal_animation_speed
