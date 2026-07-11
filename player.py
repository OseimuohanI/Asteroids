import pygame
from typing import Callable

from circleshape import CircleShape
from constants import (
    PLAYER_COLOR,
    LINE_WIDTH,
    PLAYER_INVULNERABLE_SECONDS,
    PLAYER_RADIUS,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOOT_SPEED,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
)
from shot import Shot


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.spawn_position = pygame.Vector2(x, y)
        self.rotation = 0
        self.shoot_timer = 0
        self.invulnerable_timer = PLAYER_INVULNERABLE_SECONDS
        self.on_shoot: Callable[[], None] | None = None  # optional shot callback

    @property
    def is_invulnerable(self) -> bool:
        return self.invulnerable_timer > 0

    def respawn(self) -> None:
        self.position = pygame.Vector2(self.spawn_position)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.invulnerable_timer = PLAYER_INVULNERABLE_SECONDS

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen: pygame.Surface) -> None:
        # Flash while invulnerable (skip drawing on alternate 0.1s intervals)
        if self.is_invulnerable and int(self.invulnerable_timer * 10) % 2 == 0:
            return
        pygame.draw.polygon(screen, PLAYER_COLOR, self.triangle(), LINE_WIDTH)

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:
        self.shoot_timer -= dt
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(-dt)  # negative dt reverses the direction
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            self.shoot()

    def move(self, dt):
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector

    def shoot(self) -> None:
        if self.shoot_timer > 0:
            return
        self.shoot_timer = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
        if self.on_shoot is not None:
            self.on_shoot()
