import pygame
from typing import Callable

from circleshape import CircleShape
from constants import (
    PLAYER_COLOR,
    PLAYER_DRAG,
    LINE_WIDTH,
    PLAYER_INVULNERABLE_SECONDS,
    PLAYER_RADIUS,
    PLAYER_MAX_SPEED,
    PLAYER_BURST_COOLDOWN_SECONDS,
    PLAYER_BURST_INTERVAL_SECONDS,
    PLAYER_BURST_SHOTS,
    PLAYER_SHOOT_SPEED,
    PLAYER_REVERSE_THRUST,
    PLAYER_THRUST,
    PLAYER_TURN_SPEED,
    THRUSTER_COLOR,
    THRUSTER_CORE_COLOR,
)
from shot import Shot


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.spawn_position = pygame.Vector2(x, y)
        self.rotation = 0
        self.invulnerable_timer = PLAYER_INVULNERABLE_SECONDS
        self.on_shoot: Callable[[], None] | None = None  # optional shot callback
        self.thrusting = 0.0
        self.burst_cooldown_timer = 0.0
        self.burst_interval_timer = 0.0
        self.burst_shots_remaining = 0

    @property
    def is_invulnerable(self) -> bool:
        return self.invulnerable_timer > 0

    def respawn(self) -> None:
        self.position = pygame.Vector2(self.spawn_position)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.invulnerable_timer = PLAYER_INVULNERABLE_SECONDS
        self.thrusting = 0.0
        self.burst_cooldown_timer = 0.0
        self.burst_interval_timer = 0.0
        self.burst_shots_remaining = 0

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
        if self.thrusting != 0:
            self.draw_thruster(screen)
        pygame.draw.polygon(screen, PLAYER_COLOR, self.triangle(), LINE_WIDTH)

    def draw_thruster(self, screen: pygame.Surface) -> None:
        backward = pygame.Vector2(0, -1).rotate(self.rotation)
        sideways = pygame.Vector2(1, 0).rotate(self.rotation)
        base = self.position + backward * (self.radius * 1.05)
        jitter = 4 + abs(self.thrusting) * 2
        tip = self.position + backward * (self.radius * (1.7 + abs(self.thrusting) * 0.3))
        left = base + sideways * (self.radius * 0.42 + jitter)
        right = base - sideways * (self.radius * 0.42 + jitter)
        pygame.draw.polygon(screen, THRUSTER_COLOR, [left, tip, right])
        core_tip = self.position + backward * (self.radius * (1.35 + abs(self.thrusting) * 0.2))
        core_left = base + sideways * (self.radius * 0.18)
        core_right = base - sideways * (self.radius * 0.18)
        pygame.draw.polygon(screen, THRUSTER_CORE_COLOR, [core_left, core_tip, core_right])

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        if self.burst_cooldown_timer > 0:
            self.burst_cooldown_timer -= dt
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rotate(-dt)  # negative dt reverses the direction
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rotate(dt)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.thrusting = 1.0
            self.thrust(dt)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.thrusting = -1.0
            self.thrust(-dt)
        if not (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_s] or keys[pygame.K_DOWN]):
            self.thrusting = 0.0

        self.update_burst_fire(dt, keys[pygame.K_SPACE])

        if self.velocity.length_squared() > 0:
            drag = max(0.0, 1 - PLAYER_DRAG * dt)
            self.velocity *= drag

        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity.scale_to_length(PLAYER_MAX_SPEED)

        self.move(dt)

    def thrust(self, dt: float) -> None:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        acceleration = PLAYER_THRUST if dt > 0 else PLAYER_REVERSE_THRUST
        self.velocity += forward * acceleration * dt

    def update_burst_fire(self, dt: float, firing: bool) -> None:
        if firing and self.burst_shots_remaining == 0 and self.burst_cooldown_timer <= 0:
            self.burst_shots_remaining = PLAYER_BURST_SHOTS
            self.burst_interval_timer = 0.0

        if self.burst_shots_remaining <= 0:
            return

        self.burst_interval_timer -= dt
        while self.burst_shots_remaining > 0 and self.burst_interval_timer <= 0:
            self.shoot()
            self.burst_shots_remaining -= 1
            if self.burst_shots_remaining > 0:
                self.burst_interval_timer += PLAYER_BURST_INTERVAL_SECONDS
            else:
                self.burst_cooldown_timer = PLAYER_BURST_COOLDOWN_SECONDS

    def shoot(self) -> None:
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = self.velocity + pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
        if self.on_shoot is not None:
            self.on_shoot()
