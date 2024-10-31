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

# Screen dimensions and conversion factor
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PPM = 20.0  # Pixels per meter
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
DURATION = 3  # Duration of the simulation in seconds

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


# Elevated platform (the ledge)
platform_body = world.CreateStaticBody(
    position=(12.5, 5),  # Centered at x=12.5, y=5
    shapes=b2PolygonShape(box=(12.5, 1)),  # Half-width 12.5, half-height 1
)


# Function to convert Box2D to Pygame coordinates
def to_pygame(pos):
    """Convert physics coordinates to pygame coordinates"""
    return int(pos[0] * PPM), int(SCREEN_HEIGHT - pos[1] * PPM)


# Create dominoes
domino_width = float(sys.argv[1])  # Meters
domino_height = float(sys.argv[2])  # Meters
num_dominoes = 1
start_x = 5  # Starting x position on the platform
start_y = 6 + domino_height / 2  # Platform top surface y=6, domino center y

domino_spacing = 0.5  # Spacing between dominoes
domino_bodies = []  # List to hold domino bodies

for i in range(num_dominoes):
    angle = 0.0
    if i == 0:
        angle = -0.3  # Slightly tilt the first domino to initiate the fall

    body = world.CreateDynamicBody(
        position=(start_x + i * (domino_width + domino_spacing), start_y),
        angle=angle,
    )
    body.CreatePolygonFixture(
        box=(domino_width / 2, domino_height / 2), density=1.0, friction=0.3
    )
    body.fixedRotation = False  # Allow rotation
    domino_bodies.append(body)  # Add to list

# First and last domino references
first_domino_body = domino_bodies[0]
last_domino_body = domino_bodies[-1]

# Simulation loop
running = True
frame_count = 0
total_frames = DURATION * TARGET_FPS  # Total number of frames to record

while running:
    # Update variables
    # Check if the first domino has tipped (angle significantly different from initial angle)
    if not first_domino_tipped and abs(first_domino_body.angle) > 0.5:
        first_domino_tipped = True

    # Check if the last domino has tipped
    if not last_domino_tipped and abs(last_domino_body.angle) > 0.5:
        last_domino_tipped = True
        exit(0)

    # Update physics
    world.Step(TIME_STEP, 10, 10)
    world.ClearForces()

    frame_count += 1
    if frame_count >= total_frames:
        running = False

exit(1)
