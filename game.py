import pygame
import pymunk
from pymunk.vec2d import Vec2d
import os
import math

# Window configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 50

# Physics constants
GRAVITY = 900  # magnitude of gravity force
IMPULSE_STRENGTH = 300
HALF_IMPULSE = IMPULSE_STRENGTH / 2


class Player:
    """Physics controlled player square."""

    def __init__(self, space):
        self.space = space
        mass = 1
        moment = pymunk.moment_for_box(mass, (PLAYER_SIZE, PLAYER_SIZE))
        self.body = pymunk.Body(mass, moment)
        # Start slightly above the ground
        self.body.position = (100, SCREEN_HEIGHT - 100)
        self.shape = pymunk.Poly.create_box(self.body, (PLAYER_SIZE, PLAYER_SIZE))
        self.shape.friction = 0.7
        self.shape.color = (255, 0, 0, 255)
        space.add(self.body, self.shape)

        # Sprite setup
        img_path = os.path.join(os.path.dirname(__file__), "red_square.png")
        self.image_orig = pygame.image.load(img_path).convert_alpha()
        self.image_orig = pygame.transform.smoothscale(
            self.image_orig, (PLAYER_SIZE, PLAYER_SIZE)
        )
        self.image = self.image_orig
        self.rect = self.image.get_rect()

        # Mouse drag helpers
        self.mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.drag_joint = None
        self.prev_mouse_pos = None

    def handle_input(self, keys):
        if keys[pygame.K_a]:
            self.body.apply_impulse_at_local_point((-HALF_IMPULSE, 0))
        if keys[pygame.K_d]:
            self.body.apply_impulse_at_local_point((IMPULSE_STRENGTH, 0))
        if keys[pygame.K_w]:
            self.body.apply_impulse_at_local_point((0, HALF_IMPULSE))
        if keys[pygame.K_s]:
            self.body.apply_impulse_at_local_point((0, -IMPULSE_STRENGTH))

    def start_drag(self, pos):
        """Begin dragging if the position is over the square."""
        if self.shape.point_query(pos).distance > 0:
            return
        self.mouse_body.position = pos
        self.prev_mouse_pos = pos
        # Anchor the drag joint at the clicked position on the square
        # `pos` is already a Vec2d, so avoid reinitializing to prevent errors
        local_anchor = (pos - self.body.position).rotated(-self.body.angle)
        self.drag_joint = pymunk.PivotJoint(self.mouse_body, self.body,
                                            (0, 0), local_anchor)
        self.drag_joint.max_force = 10000
        self.space.add(self.mouse_body, self.drag_joint)

    def update_drag(self, pos, dt):
        if not self.drag_joint:
            return
        if dt <= 0:
            # Avoid division by zero if the very first frame has dt == 0
            dt = 1e-6
        vel = (pos[0] - self.prev_mouse_pos[0], pos[1] - self.prev_mouse_pos[1])
        self.mouse_body.velocity = (vel[0] / dt, vel[1] / dt)
        self.mouse_body.position = pos
        self.prev_mouse_pos = pos

    def end_drag(self):
        if not self.drag_joint:
            return
        # Apply the last velocity to fling the square
        self.body.velocity = self.mouse_body.velocity
        self.space.remove(self.drag_joint, self.mouse_body)
        self.drag_joint = None
        self.mouse_body.velocity = (0, 0)


def create_test_area(space, width, height):
    """Create a simple boxed area so the square doesn't fall forever."""
    body = space.static_body
    floor = pymunk.Segment(body, (0, 40), (width, 40), 0)
    left = pymunk.Segment(body, (0, 40), (0, height), 0)
    right = pymunk.Segment(body, (width, 40), (width, height), 0)
    ceiling = pymunk.Segment(body, (0, height), (width, height), 0)
    for line in (floor, left, right, ceiling):
        line.friction = 1.0
    space.add(floor, left, right, ceiling)
    return [floor, left, right, ceiling]


def world_to_screen(p: Vec2d, camera: Vec2d, surface: pygame.Surface) -> tuple[int, int]:
    """Convert world coordinates to screen coordinates using a camera offset."""
    x = (p.x - camera.x) + surface.get_width() / 2
    y = surface.get_height() / 2 - (p.y - camera.y)
    return int(x), int(y)

def screen_to_world(p: tuple[int, int], camera: Vec2d, surface: pygame.Surface) -> Vec2d:
    """Inverse of world_to_screen for translating mouse positions."""
    x = p[0] - surface.get_width() / 2 + camera.x
    y = camera.y - (p[1] - surface.get_height() / 2)
    return Vec2d(x, y)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                     pygame.RESIZABLE)
    pygame.display.set_caption("Physics Example")
    clock = pygame.time.Clock()

    space = pymunk.Space()
    # Negative Y is up in this coordinate system, so gravity must be negative
    space.gravity = (0, -GRAVITY)

    # ➊  Create the player **before** you use it
    player = Player(space)

    # ➋  Build the walls
    segments = create_test_area(space, SCREEN_WIDTH, SCREEN_HEIGHT)

    # ➌  Now it’s safe to read player.body.position
    camera_pos = Vec2d(*player.body.position)   # centered on the player
    CAMERA_SMOOTHING = 5.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if dt <= 0:
            dt = 1e-6
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = screen_to_world(event.pos, camera_pos, screen)
                player.start_drag(pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                player.end_drag()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

        mouse_pos = screen_to_world(pygame.mouse.get_pos(), camera_pos, screen)
        player.update_drag(mouse_pos, dt)

        keys = pygame.key.get_pressed()
        player.handle_input(keys)

        # Smooth camera follow
        camera_pos += (player.body.position - camera_pos) * CAMERA_SMOOTHING * dt

        space.step(dt)

        screen.fill((135, 206, 235))

        # Draw static segments
        for segment in segments:
            start = world_to_screen(segment.a, camera_pos, screen)
            end = world_to_screen(segment.b, camera_pos, screen)
            pygame.draw.line(screen, (0, 0, 0), start, end, 2)

        # Draw the player sprite
        angle_deg = -math.degrees(player.body.angle)
        player.image = pygame.transform.rotozoom(player.image_orig, angle_deg, 1)
        player.rect = player.image.get_rect()
        player.rect.center = world_to_screen(player.body.position, camera_pos, screen)
        screen.blit(player.image, player.rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
