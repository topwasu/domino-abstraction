import math

from classes import StructureRep

# Domino Spacing and Alignment
def get_abstract_feature_1(structure_rep: StructureRep) -> float:
    res = None
    
    # Check if there are at least two dominos to calculate spacing
    if len(structure_rep.sorted_domino_positions) < 2:
        return res
    
    # Calculate the spacing between consecutive dominos
    spacings = [
        structure_rep.sorted_domino_positions[i+1] - structure_rep.sorted_domino_positions[i]
        for i in range(len(structure_rep.sorted_domino_positions) - 1)
    ]
    
    # Calculate the average spacing
    average_spacing = sum(spacings) / len(spacings)
    
    # Check alignment: if all spacings are approximately equal, dominos are aligned
    # We can use a tolerance to account for minor deviations
    tolerance = 0.01 * structure_rep.domino_width  # 1% of the domino width as tolerance
    aligned = all(abs(spacing - average_spacing) <= tolerance for spacing in spacings)
    
    # Combine spacing and alignment into a single feature
    # For simplicity, let's return the average spacing if aligned, otherwise None
    if aligned:
        res = average_spacing
    
    return res
    
# Initial Force Applied
def get_abstract_feature_2(structure_rep: StructureRep) -> float:
    res = None
    
    # Calculate the volume of the ball
    ball_volume = (4/3) * math.pi * (structure_rep.ball_radius ** 3)
    
    # Calculate the mass of the ball
    ball_mass = structure_rep.ball_density * ball_volume
    
    # Assume a velocity for the ball (since it's not provided)
    assumed_velocity = 1.0  # This is arbitrary and should be replaced with actual data if available
    
    # Calculate the initial force applied using F = m * a
    # Here, we assume acceleration is equivalent to the assumed velocity for simplicity
    # In reality, you would need the actual acceleration or impact velocity
    initial_force_applied = ball_mass * assumed_velocity
    
    # Assign the calculated force to res
    res = initial_force_applied
    
    return res

# Beam Stability and Balance
def get_abstract_feature_3(structure_rep: StructureRep) -> float:
    res = None
    
    # Assumptions:
    # 1. The beam is stable if the ball is positioned on top of the dominos without falling off.
    # 2. The balance could be related to the ball's position relative to the center of the dominos.
    
    # Calculate the total width of the dominos
    total_domino_width = len(structure_rep.sorted_domino_positions) * structure_rep.domino_width
    
    # Calculate the center position of the dominos
    center_domino_position = (structure_rep.sorted_domino_positions[0] + 
                              structure_rep.sorted_domino_positions[-1]) / 2
    
    # Check if the ball is within the bounds of the dominos
    if (structure_rep.ball_position - structure_rep.ball_radius >= structure_rep.sorted_domino_positions[0] and
        structure_rep.ball_position + structure_rep.ball_radius <= structure_rep.sorted_domino_positions[-1]):
        
        # Calculate balance as the distance of the ball from the center of the dominos
        balance = abs(structure_rep.ball_position - center_domino_position)
        
        # Normalize balance by the total width of the dominos
        res = 1 - (balance / (total_domino_width / 2))
    else:
        # If the ball is not on the dominos, return None
        res = None
    
    return res


# Ball Position Relative to the Last Domino
def get_abstract_feature_4(structure_rep: StructureRep) -> float:
    res = None
    # Check if there are any dominos in the list
    if structure_rep.sorted_domino_positions:
        # Get the position of the last domino
        last_domino_position = structure_rep.sorted_domino_positions[-1]
        # Compute the ball position relative to the last domino
        res = structure_rep.ball_position - last_domino_position
    return res


# Domino Size and Mass Variation
def get_abstract_feature_5(structure_rep: StructureRep) -> float:
    res = None
    
    try:
        # Calculate the volume of a single domino
        domino_volume = structure_rep.domino_width * structure_rep.domino_height
        
        # Assume a uniform density for dominos (since it's not provided)
        # For simplicity, let's assume the density is 1 unit
        domino_density = 1.0
        domino_mass = domino_volume * domino_density
        
        # Calculate the mass of the ball
        ball_volume = (4/3) * 3.14159 * (structure_rep.ball_radius ** 3)
        ball_mass = ball_volume * structure_rep.ball_density
        
        # Calculate the variation between domino mass and ball mass
        # This is a simple ratio of the two masses
        mass_variation = domino_mass / ball_mass if ball_mass != 0 else None
        
        # Calculate the size variation
        # This could be the ratio of the domino's height to the ball's diameter
        size_variation = structure_rep.domino_height / (2 * structure_rep.ball_radius) if structure_rep.ball_radius != 0 else None
        
        # Combine the two variations into a single metric
        if mass_variation is not None and size_variation is not None:
            res = mass_variation * size_variation
    except Exception as e:
        # If any error occurs, return None
        res = None
    
    return res