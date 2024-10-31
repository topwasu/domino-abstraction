import sys
from Box2D import (
    b2World,
    b2PolygonShape,
    b2CircleShape,
    b2_dynamicBody,
    b2_staticBody,
    b2ContactListener,
    b2RevoluteJointDef,
)
import imageio
import numpy as np

# # Initialize Pygame
# pygame.init()

# Screen dimensions and conversion factor
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PPM = 20.0  # Pixels per meter
TARGET_FPS = 120
TIME_STEP = 1.0 / TARGET_FPS
DURATION = 30  # Duration of the simulation in seconds

# # Pygame setup
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("Domino Simulation with Balance Beam and Cups")
# clock = pygame.time.Clock()
# font = pygame.font.SysFont("Arial", 18)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Box2D world setup
world = b2World(gravity=(0, -10), doSleep=True)

# Variables to track
first_domino_tipped = False
last_domino_tipped = False
domino_ball_contact = False
ball_moving_right = False
ball_contact_top = False
ball_contact_bottom = False
beam_tip = "neutral"


# Contact listener to monitor contacts
class ContactListener(b2ContactListener):
    def __init__(self):
        b2ContactListener.__init__(self)

    def BeginContact(self, contact):
        global domino_ball_contact, ball_contact_top, ball_contact_bottom
        fixtureA = contact.fixtureA
        fixtureB = contact.fixtureB
        bodyA = fixtureA.body
        bodyB = fixtureB.body

        # Check if the last domino is in contact with the bowling ball
        if (bodyA == last_domino_body and bodyB == bowling_ball_body) or (
            bodyB == last_domino_body and bodyA == bowling_ball_body
        ):
            domino_ball_contact = True

        # Check if the bowling ball is in contact with the top platform
        if (bodyA == bowling_ball_body and bodyB == platform_body) or (
            bodyB == bowling_ball_body and bodyA == platform_body
        ):
            ball_contact_top = True

        # Check if the bowling ball is in contact with the balance beam
        if (bodyA == bowling_ball_body and bodyB == beam_body) or (
            bodyB == bowling_ball_body and bodyA == beam_body
        ):
            ball_contact_bottom = True  # Reusing variable for simplicity

    def EndContact(self, contact):
        global domino_ball_contact, ball_contact_top, ball_contact_bottom
        fixtureA = contact.fixtureA
        fixtureB = contact.fixtureB
        bodyA = fixtureA.body
        bodyB = fixtureB.body

        # Check if the last domino is no longer in contact with the bowling ball
        if (bodyA == last_domino_body and bodyB == bowling_ball_body) or (
            bodyB == last_domino_body and bodyA == bowling_ball_body
        ):
            domino_ball_contact = False

        # Check if the bowling ball is no longer in contact with the top platform
        if (bodyA == bowling_ball_body and bodyB == platform_body) or (
            bodyB == bowling_ball_body and bodyA == platform_body
        ):
            ball_contact_top = False

        # Check if the bowling ball is no longer in contact with the balance beam
        if (bodyA == bowling_ball_body and bodyB == beam_body) or (
            bodyB == bowling_ball_body and bodyA == beam_body
        ):
            ball_contact_bottom = False


# Add the contact listener to the world
contact_listener = ContactListener()
world.contactListener = contact_listener

# Elevated platform (the ledge)
platform_body = world.CreateStaticBody(
    position=(12.5, 5),  # Centered at x=12.5, y=5
    shapes=b2PolygonShape(box=(12.5, 1)),  # Half-width 12.5, half-height 1
)


# Function to convert Box2D to Pygame coordinates
def to_pygame(pos):
    """Convert physics coordinates to pygame coordinates"""
    return int(pos[0] * PPM), int(SCREEN_HEIGHT - pos[1] * PPM)


domino_width = 0.2

scenarios = []

for r in [3, 6, 9, 12]:
    for n in [5, 10, 20]:
        for k in [0, 2, 4]:
            scenarios.append((domino_width * r, n, k))

# Create dominoes
scenario = int(sys.argv[1])
if scenario >= len(scenarios):
    exit(0)
domino_height, num_dominoes, n_skip = scenarios[scenario]
start_x = 5  # Starting x position on the platform
start_y = 6 + domino_height / 2  # Platform top surface y=6, domino center y

print(f"width({domino_width}).")
print(f"height({domino_height}).")

domino_spacing = 0.5  # Spacing between dominoes
domino_bodies = []  # List to hold domino bodies

mid = num_dominoes // 2
skip_start = mid - n_skip // 2
skip_end = mid + n_skip // 2
pushed = False
for i in range(num_dominoes):
    if skip_start <= i < skip_end:
        continue

    domino_x = start_x + i * (domino_width + domino_spacing)
    angle = 0.0
    if not pushed:
        angle = -0.3  # Slightly tilt the first domino to initiate the fall
        print(f"push(domino({domino_x})).")
        pushed = True

    body = world.CreateDynamicBody(
        position=(domino_x, start_y),
        angle=angle,
    )
    print(f"domino({domino_x}).")
    body.CreatePolygonFixture(
        box=(domino_width / 2, domino_height / 2), density=1.0, friction=0.3
    )
    body.fixedRotation = False  # Allow rotation
    domino_bodies.append(body)  # Add to list

# First and last domino references
first_domino_body = domino_bodies[0]
last_domino_body = domino_bodies[-1]

# Compute last domino x-position
last_domino_x = start_x + (num_dominoes - 1) * (domino_width + domino_spacing)

# Bowling ball properties
bowling_ball_radius = 0.5  # 0.5 meters radius
bowling_ball_density = 0.5  # Adjust as needed
small_gap = 0.1  # Gap between last domino and bowling ball

bowling_ball_x = last_domino_x + domino_width / 2 + bowling_ball_radius + small_gap
bowling_ball_y = 6 + bowling_ball_radius  # On top of the platform

print(f"ball_x({bowling_ball_x}).")

# Create bowling ball
bowling_ball_body = world.CreateDynamicBody(
    position=(bowling_ball_x, bowling_ball_y),
)
bowling_ball_body.CreateCircleFixture(
    radius=bowling_ball_radius, density=bowling_ball_density, friction=0.3
)

# Create the balance beam (seesaw)
beam_length = 8.0  # Total length of the beam
beam_thickness = 0.2  # Thickness of the beam
beam_position = (30, 2.0)  # Position of the fulcrum (pivot point)

# Beam body (dynamic)
beam_body = world.CreateDynamicBody(
    position=beam_position,
    angle=0.0,
)
beam_body.CreatePolygonFixture(
    box=(beam_length / 2, beam_thickness / 2), density=1.0, friction=0.5
)

# Attach cups to each end of the beam
cup_width = 2.0  # Width of the cup (meters)
cup_height = 1.0  # Height of the cup walls (meters)
wall_thickness = 0.1  # Thickness of the cup walls (meters)

# Left cup (where the ball will land)
left_cup_offset = (-beam_length / 2 + cup_width / 2, 0)
# Left cup walls relative to beam body
left_wall_vertices = [
    (left_cup_offset[0] - cup_width / 2 + wall_thickness / 2, cup_height / 2),
    (left_cup_offset[0] - cup_width / 2 + wall_thickness / 2, -cup_height / 2),
    (left_cup_offset[0] - cup_width / 2 - wall_thickness / 2, -cup_height / 2),
    (left_cup_offset[0] - cup_width / 2 - wall_thickness / 2, cup_height / 2),
]

right_wall_vertices = [
    (left_cup_offset[0] + cup_width / 2 - wall_thickness / 2, cup_height / 2),
    (left_cup_offset[0] + cup_width / 2 - wall_thickness / 2, -cup_height / 2),
    (left_cup_offset[0] + cup_width / 2 + wall_thickness / 2, -cup_height / 2),
    (left_cup_offset[0] + cup_width / 2 + wall_thickness / 2, cup_height / 2),
]

# Create fixtures for the left cup walls
beam_body.CreatePolygonFixture(vertices=left_wall_vertices, density=1.0, friction=0.5)
beam_body.CreatePolygonFixture(vertices=right_wall_vertices, density=1.0, friction=0.5)

# Right cup (opposite side)
right_cup_offset = (beam_length / 2 - cup_width / 2, 0)
# Right cup walls relative to beam body
left_wall_vertices = [
    (right_cup_offset[0] - cup_width / 2 + wall_thickness / 2, cup_height / 2),
    (right_cup_offset[0] - cup_width / 2 + wall_thickness / 2, -cup_height / 2),
    (right_cup_offset[0] - cup_width / 2 - wall_thickness / 2, -cup_height / 2),
    (right_cup_offset[0] - cup_width / 2 - wall_thickness / 2, cup_height / 2),
]

right_wall_vertices = [
    (right_cup_offset[0] + cup_width / 2 - wall_thickness / 2, cup_height / 2),
    (right_cup_offset[0] + cup_width / 2 - wall_thickness / 2, -cup_height / 2),
    (right_cup_offset[0] + cup_width / 2 + wall_thickness / 2, -cup_height / 2),
    (right_cup_offset[0] + cup_width / 2 + wall_thickness / 2, cup_height / 2),
]

# Create fixtures for the right cup walls
beam_body.CreatePolygonFixture(vertices=left_wall_vertices, density=1.0, friction=0.5)
beam_body.CreatePolygonFixture(vertices=right_wall_vertices, density=1.0, friction=0.5)

# Create the fulcrum (static body)
fulcrum_body = world.CreateStaticBody(
    position=beam_position,
)

# Create a revolute joint (pivot) between the beam and the fulcrum
joint_def = b2RevoluteJointDef(
    bodyA=beam_body,
    bodyB=fulcrum_body,
    localAnchorA=(0, 0),
    localAnchorB=(0, 0),
    enableMotor=False,
    enableLimit=True,
    lowerAngle=-15 * (3.1416 / 180),  # Limit the rotation to prevent excessive tilt
    upperAngle=15 * (3.1416 / 180),
)
world.CreateJoint(joint_def)

# Create a video writer using imageio
video_writer = imageio.get_writer("domino_simulation_balance_beam.mp4", fps=TARGET_FPS)

# Simulation loop
running = True
frame_count = 0
total_frames = DURATION * TARGET_FPS  # Total number of frames to record

while running:
    # # Handle events
    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         running = False

    # # Clear screen
    # screen.fill(WHITE)

    # Update variables
    # Check if the first domino has tipped (angle significantly different from initial angle)
    if not first_domino_tipped and abs(first_domino_body.angle) > 0.5:
        first_domino_tipped = True

    # Check if the last domino has tipped
    if not last_domino_tipped and abs(last_domino_body.angle) > 0.5:
        last_domino_tipped = True

    if beam_body.angle > 0.2:
        beam_tip = "positive"
    elif beam_body.angle < -0.2:
        beam_tip = "negative"
    else:
        beam_tip = "neutral"

    # Check if the bowling ball is moving to the right
    ball_velocity = bowling_ball_body.linearVelocity.x
    ball_moving_right = ball_velocity > 0.1  # Threshold to avoid floating-point errors

    # # Draw static bodies (platform, fulcrum)
    # for body in world.bodies:
    #     if body.type == b2_staticBody:
    #         for fixture in body.fixtures:
    #             shape = fixture.shape
    #             if isinstance(shape, b2PolygonShape):
    #                 vertices = [body.transform * v for v in shape.vertices]
    #                 vertices = [to_pygame(v) for v in vertices]
    #                 pygame.draw.polygon(screen, BLACK, vertices)

    # # Draw dynamic bodies (dominoes, bowling ball, beam)
    # for body in world.bodies:
    #     if body.type == b2_dynamicBody:
    #         for fixture in body.fixtures:
    #             shape = fixture.shape
    #             if isinstance(shape, b2PolygonShape):
    #                 vertices = [body.transform * v for v in shape.vertices]
    #                 vertices = [to_pygame(v) for v in vertices]
    #                 pygame.draw.polygon(screen, BLACK, vertices)
    #             elif isinstance(shape, b2CircleShape):
    #                 position = body.transform * shape.pos
    #                 position = to_pygame(position)
    #                 pygame.draw.circle(screen, BLACK, position, int(shape.radius * PPM))

    # # Display variables on the screen
    # status_texts = [
    #     f"First Domino Tipped: {'Yes' if first_domino_tipped else 'No'}",
    #     f"Last Domino Tipped: {'Yes' if last_domino_tipped else 'No'}",
    #     f"Domino and Ball Contact: {'Yes' if domino_ball_contact else 'No'}",
    #     f"Ball Moving Right: {'Yes' if ball_moving_right else 'No'}",
    #     f"Ball Contact Top Level: {'Yes' if ball_contact_top else 'No'}",
    #     f"Ball Contact Beam: {'Yes' if ball_contact_bottom else 'No'}",
    #     f"Beam Tip: {beam_tip}",
    # ]

    # for i, text in enumerate(status_texts):
    #     rendered_text = font.render(text, True, BLACK)
    #     screen.blit(rendered_text, (10, 10 + i * 20))

    # # Capture the screen surface as an image
    # frame = pygame.surfarray.array3d(screen)
    # # Convert from (width, height, channels) to (height, width, channels)
    # frame = np.transpose(frame, (1, 0, 2))
    # # Write the frame to the video
    # video_writer.append_data(frame)

    if beam_tip == "positive":
        break

    # Update physics
    world.Step(TIME_STEP, 10, 10)
    world.ClearForces()

    # # Update display
    # pygame.display.flip()
    # clock.tick(TARGET_FPS)

    frame_count += 1
    if frame_count >= total_frames:
        running = False

# Clean up
# video_writer.close()
# pygame.quit()

if beam_tip == "positive":
    print("success.")
