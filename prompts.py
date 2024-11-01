abstract_feature_prompt = """\
We want to synthesize a python function that returns "{abstract_feature}"

The format of the function should be

def get_abstract_feature(structure_rep: StructureRep) -> float
    res = None
    # Compute "{abstract_feature}" and put it in res
    # If you don't know how to compute it just return None
    return res

class StructureRep:
    Attributes:
        sorted_domino_positions (list of floats): x-axis positions of the dominos, sorted
        domino_width (float): width of the dominos
        domino_height (float): height of the dominos
        ball_position (float): x-axis position of the ball
        ball_radius (float): radius of the ball
        ball_density (float): density of the ball
        
"""