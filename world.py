import pygame
from Box2D import (
    b2World, b2PolygonShape, b2CircleShape,
    b2_dynamicBody, b2_staticBody, b2ContactListener, b2RevoluteJointDef
)
import imageio
import numpy as np

from classes import ContactListener, Button, Slider

# Screen dimensions and conversion factor
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
PPM = 20.0  # Pixels per meter
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
DURATION = 15  # Duration of the simulation in seconds

BLACK = (0, 0, 0)

# Function to convert Box2D to Pygame coordinates
def to_pygame(pos):
    """Convert physics coordinates to pygame coordinates"""
    return int(pos[0] * PPM), int(SCREEN_HEIGHT - pos[1] * PPM)


def get_world(domino_spacing=0.5, domino_width=0.2, domino_height=1.0, num_dominoes=20, small_gap=0.1, hole_size=0.1):
    # Box2D world setup
    world = b2World(gravity=(0, -10), doSleep=True)


    # Elevated platform (the ledge)
    platform_body = world.CreateStaticBody(
        position=(12.5, 5),  # Centered at x=12.5, y=5
        shapes=b2PolygonShape(box=(12.5, 1)),  # Half-width 12.5, half-height 1
    )
    
    platform_body2 = world.CreateStaticBody(
        position=(25 + hole_size + 1, 5),  # Centered at x=12.5, y=5
        shapes=b2PolygonShape(box=(1, 1)),  # Half-width 12.5, half-height 1
    )
    


    # Create dominoes
    start_x = 5  # Starting x position on the platform
    start_y = 6 + domino_height / 2  # Platform top surface y=6, domino center y

    domino_bodies = []  # List to hold domino bodies
    num_dominoes = int(num_dominoes)
    for i in range(num_dominoes):
        angle = 0.0
        if i == 0:
            angle = -0.3  # Slightly tilt the first domino to initiate the fall
        body = world.CreateDynamicBody(
            position=(start_x + i * (domino_width + domino_spacing), start_y),
            angle=angle,
        )
        body.CreatePolygonFixture(box=(domino_width / 2, domino_height / 2), density=1.0, friction=0.3)
        body.fixedRotation = False  # Allow rotation
        domino_bodies.append(body)  # Add to list
    first_domino_body = domino_bodies[0]
    last_domino_body = domino_bodies[-1]

    # Compute last domino x-position
    last_domino_x = start_x + (num_dominoes - 1) * (domino_width + domino_spacing)

    # Bowling ball properties
    bowling_ball_radius = 0.5  # 0.5 meters radius
    bowling_ball_density = 0.5  # Adjust as needed

    bowling_ball_x = last_domino_x + domino_width / 2 + bowling_ball_radius + small_gap
    bowling_ball_y = 6 + bowling_ball_radius  # On top of the platform

    # Create bowling ball
    bowling_ball_body = world.CreateDynamicBody(
        position=(bowling_ball_x, bowling_ball_y),
    )
    bowling_ball_body.CreateCircleFixture(radius=bowling_ball_radius, density=bowling_ball_density, friction=0.3)

    # Create the balance beam (seesaw)
    beam_length = 8.0  # Total length of the beam
    beam_thickness = 0.2  # Thickness of the beam
    beam_position = (32 + hole_size, 2.0)  # Position of the fulcrum (pivot point)

    # Beam body (dynamic)
    beam_body = world.CreateDynamicBody(
        position=beam_position,
        angle=0.0,
    )
    beam_body.CreatePolygonFixture(box=(beam_length / 2, beam_thickness / 2), density=1.0, friction=0.5)

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

    # Add the contact listener to the world
    contact_listener = ContactListener(last_domino_body, bowling_ball_body, platform_body, beam_body)
    world.contactListener = contact_listener
    return world, first_domino_body, last_domino_body, bowling_ball_body, beam_body


def draw_world_on_screen(world, screen):
    # Draw static bodies (platform, fulcrum)
        for body in world.bodies:
            if body.type == b2_staticBody:
                for fixture in body.fixtures:
                    shape = fixture.shape
                    if isinstance(shape, b2PolygonShape):
                        vertices = [body.transform * v for v in shape.vertices]
                        vertices = [to_pygame(v) for v in vertices]
                        pygame.draw.polygon(screen, BLACK, vertices)

        # Draw dynamic bodies (dominoes, bowling ball, beam)
        for body in world.bodies:
            if body.type == b2_dynamicBody:
                for fixture in body.fixtures:
                    shape = fixture.shape
                    if isinstance(shape, b2PolygonShape):
                        vertices = [body.transform * v for v in shape.vertices]
                        vertices = [to_pygame(v) for v in vertices]
                        pygame.draw.polygon(screen, BLACK, vertices)
                    elif isinstance(shape, b2CircleShape):
                        position = body.transform * shape.pos
                        position = to_pygame(position)
                        pygame.draw.circle(screen, BLACK, position, int(shape.radius * PPM))