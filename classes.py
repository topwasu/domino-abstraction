import pygame
from Box2D import (
    b2World, b2PolygonShape, b2CircleShape,
    b2_dynamicBody, b2_staticBody, b2ContactListener, b2RevoluteJointDef
)


# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)



class Slider:
    def __init__(self, name, x, y, width, height):
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.circle_radius = height // 2
        self.circle_x = x  # Start position of the slider handle
        self.dragging = False

    def draw(self, surface):
        # Draw the slider track
        pygame.draw.rect(surface, GRAY, self.rect)
        
        # Draw the slider handle
        pygame.draw.circle(surface, BLACK, (self.circle_x, self.rect.centery), self.circle_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the mouse clicked on the slider handle
            if pygame.Rect(self.circle_x - self.circle_radius, self.rect.centery - self.circle_radius, 
                           self.circle_radius * 2, self.circle_radius * 2).collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            # Stop dragging when the mouse button is released
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            # Update the slider handle position if dragging
            if self.dragging:
                self.circle_x = max(self.rect.left, min(event.pos[0], self.rect.right))
                
    def get_value(self):
        # Map the slider position to a range (e.g., 0 to 100)
        return (self.circle_x - self.rect.left) / self.rect.width * 100

# Contact listener to monitor contacts
class ContactListener(b2ContactListener):
    def __init__(self, last_domino_body, bowling_ball_body, platform_body, beam_body):
        b2ContactListener.__init__(self)
        self.last_domino_body = last_domino_body
        self.bowling_ball_body = bowling_ball_body
        self.platform_body = platform_body
        self.beam_body = beam_body

        # Contact status variables
        self.domino_ball_contact = False
        self.ball_contact_top = False
        self.ball_contact_bottom = False

    def BeginContact(self, contact):
        fixtureA = contact.fixtureA
        fixtureB = contact.fixtureB
        bodyA = fixtureA.body
        bodyB = fixtureB.body

        # Check if the last domino is in contact with the bowling ball
        if (bodyA == self.last_domino_body and bodyB == self.bowling_ball_body) or \
           (bodyB == self.last_domino_body and bodyA == self.bowling_ball_body):
            self.domino_ball_contact = True

        # Check if the bowling ball is in contact with the top platform
        if (bodyA == self.bowling_ball_body and bodyB == self.platform_body) or \
           (bodyB == self.bowling_ball_body and bodyA == self.platform_body):
            self.ball_contact_top = True

        # Check if the bowling ball is in contact with the balance beam
        if (bodyA == self.bowling_ball_body and bodyB == self.beam_body) or \
           (bodyB == self.bowling_ball_body and bodyA == self.beam_body):
            self.ball_contact_bottom = True  # Reusing variable for simplicity

    def EndContact(self, contact):
        fixtureA = contact.fixtureA
        fixtureB = contact.fixtureB
        bodyA = fixtureA.body
        bodyB = fixtureB.body

        # Check if the last domino is no longer in contact with the bowling ball
        if (bodyA == self.last_domino_body and bodyB == self.bowling_ball_body) or \
           (bodyB == self.last_domino_body and bodyA == self.bowling_ball_body):
            self.domino_ball_contact = False

        # Check if the bowling ball is no longer in contact with the top platform
        if (bodyA == self.bowling_ball_body and bodyB == self.platform_body) or \
           (bodyB == self.bowling_ball_body and bodyA == self.platform_body):
            self.ball_contact_top = False

        # Check if the bowling ball is no longer in contact with the balance beam
        if (bodyA == self.bowling_ball_body and bodyB == self.beam_body) or \
           (bodyB == self.bowling_ball_body and bodyA == self.beam_body):
            self.ball_contact_bottom = False
            
    def get_contacts(self):
        return self.domino_ball_contact, self.ball_contact_top, self.ball_contact_bottom
            
class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, surface):
        # Change color on hover
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        
        # Render the text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        # Check if mouse is hovering over the button
        self.is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        
        # Check if button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            return True
        return False