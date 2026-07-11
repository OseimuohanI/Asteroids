import pygame

from circleshape import CircleShape
from constants import LINE_WIDTH, SHOT_COLOR, SHOT_LIFETIME_SECONDS, SHOT_RADIUS


class Shot(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SHOT_RADIUS)
        self.lifetime = SHOT_LIFETIME_SECONDS

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, SHOT_COLOR, self.position, self.radius, LINE_WIDTH)

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        self.move(dt)
