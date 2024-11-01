import pygame
import logging
from Box2D import (
    b2World, b2PolygonShape, b2CircleShape,
    b2_dynamicBody, b2_staticBody, b2ContactListener, b2RevoluteJointDef
)
import imageio
import numpy as np
import hydra
import matplotlib.pyplot as plt

from classes import ContactListener, Button, Slider, StructureRep
from world import get_world, to_pygame, draw_world_on_screen


# init_logger() # Don't need this if already using hydra
log = logging.getLogger('main')
log.setLevel(logging.INFO)


def get_values(sliders, config):
    if config.task == 'task_1':
        return [0.5, 0.2, 1.0, 4, 0.1, 0]
    elif config.task == 'task_2':
        return [0.5, 0.2, 1.0, 22, 2, 0]
    elif config.task == 'task_3':
        return [0.5, 0.2, 1.0, 6, 0.6, 0]
    else:
        slider_values = [max(0.1, slider.get_value()) for slider in sliders]
        slider_values[-3] = max(slider_values[-3], 1)
        return slider_values


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(config):
    # Initialize Pygame
    pygame.init()

    # Screen dimensions and conversion factor
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
    PPM = 20.0  # Pixels per meter
    TARGET_FPS = 60
    TIME_STEP = 1.0 / TARGET_FPS
    DURATION = 15  # Duration of the simulation in seconds

    # Pygame setup
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Domino Simulation with Balance Beam and Cups')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 18)

    # Colors
    WHITE = (255, 255, 255)
    GRAY = (200, 200, 200)
    BLACK = (0, 0, 0)

    # Variables to track
    first_domino_tipped = False
    last_domino_tipped = False
    ball_moving_right = False
    beam_tip = "neutral"

    # Create a video writer using imageio
    video_writer = imageio.get_writer(f'domino_simulation_balance_beam_{config.task}.mp4', fps=TARGET_FPS)


    domino_spacing_slider = Slider('domino_spacing', 100, 50, 600, 20, 2)
    domino_width_slider = Slider('domino_width', 100, 150, 600, 20, 2)
    domino_height_slider = Slider('domino_height', 100, 250, 600, 20, 2)
    num_dominoes_slider = Slider('num_dominoes', 100, 350, 600, 20, 20)
    small_gap_slider = Slider('small_gap', 100, 450, 600, 20, 2)
    hole_size_slider = Slider('hole_size', 100, 550, 600, 20, 2)
    sliders = [domino_spacing_slider, domino_width_slider, domino_height_slider, num_dominoes_slider, small_gap_slider, hole_size_slider]
    start_button = Button(350, 400, 100, 50, "Start", font, GRAY, (170, 170, 170), BLACK)

    # Simulation loop
    running = True
    game_started = False
    frame_count = 0
    total_frames = DURATION * TARGET_FPS  # Total number of frames to record
    
    # if config.task != 'slider':
    #     slider_values = get_values([], config)
    #     world, first_domino_body, last_domino_body, bowling_ball_body, beam_body, domino_bodies, ball_body = get_world(*slider_values)
        
    #     rep = StructureRep(domino_bodies, ball_body)
    #     print(rep)
        
    #     screen.fill(WHITE)
    #     draw_world_on_screen(world, screen)
        
    #     frame = pygame.surfarray.array3d(screen)
    #     # Convert from (width, height, channels) to (height, width, channels)
    #     frame = np.transpose(frame, (1, 0, 2))
        
    #     plt.imshow(frame)
    #     plt.axis('off')
    #     plt.savefig(f'domino_simulation_balance_beam_{config.task}.png')
        
    #     input()

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            for slider in sliders:
                slider.handle_event(event)
            
            # Handle button click to start the game
            slider_values = get_values(sliders, config)
            # slider_values = [max(0.1, slider.get_value()) for slider in sliders]
            # slider_values[-3] = max(slider_values[-3], 1)
            
            if start_button.handle_event(event):
                game_started = True  # Set the flag to True to indicate game has started
                
            world, first_domino_body, last_domino_body, bowling_ball_body, beam_body, _, _ = get_world(*slider_values)

        # Clear screen
        screen.fill(WHITE)
        
        draw_world_on_screen(world, screen)
        
        if not game_started:
            # Draw the slider and display its current value
            if config.task == 'slider':
                for idx, slider in enumerate(sliders):
                    slider.draw(screen)
                    font = pygame.font.Font(None, 36)
                    text = font.render(f"{slider.name}: {slider.get_value():.2f}", True, BLACK)
                    screen.blit(text, (100, 100*(idx)))
            
            start_button.draw(screen)
            
            
        else:

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

            # Display variables on the screen
            status_texts = [
                f"First Domino Tipped: {'Yes' if first_domino_tipped else 'No'}",
                f"Last Domino Tipped: {'Yes' if last_domino_tipped else 'No'}",
                f"Domino and Ball Contact: {'Yes' if world.contactListener.domino_ball_contact else 'No'}",
                f"Ball Moving Right: {'Yes' if ball_moving_right else 'No'}",
                f"Ball Contact Top Level: {'Yes' if world.contactListener.ball_contact_top else 'No'}",
                f"Ball Contact Beam: {'Yes' if world.contactListener.ball_contact_bottom else 'No'}",
                f"Beam Tip: {beam_tip}"
            ]

            for i, text in enumerate(status_texts):
                rendered_text = font.render(text, True, BLACK)
                screen.blit(rendered_text, (10, 10 + i * 20))
                
            # Update physics
            world.Step(TIME_STEP, 10, 10)
            world.ClearForces()

        # Capture the screen surface as an image
        frame = pygame.surfarray.array3d(screen)
        # Convert from (width, height, channels) to (height, width, channels)
        frame = np.transpose(frame, (1, 0, 2))
        # Write the frame to the video
        video_writer.append_data(frame)

        # Update display
        pygame.display.flip()
        clock.tick(TARGET_FPS)

        # frame_count += 1
        # if frame_count >= total_frames:
        #     running = False

    # Clean up
    video_writer.close()
    pygame.quit()
    
if __name__ == '__main__':
    main()
