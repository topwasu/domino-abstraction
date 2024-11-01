
import hydra
import logging
from openai_hf_interface import choose_provider, create_llm

from sklearn.linear_model import LogisticRegression


from programs import *
from world import get_world
from classes import StructureRep


# init_logger() # Don't need this if already using hydra
log = logging.getLogger('main')
log.setLevel(logging.INFO)


def get_values(task):
    if task == 'task_1':
        return [0.5, 0.2, 1.0, 4, 0.1, 0]
    elif task == 'task_2':
        return [0.5, 0.2, 1.0, 22, 2, 0]
    elif task == 'task_3':
        return [0.5, 0.2, 1.0, 6, 0.6, 0]
    else:
        raise NotImplementedError


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(config):
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    choose_provider(config.provider)
    
    programs = [get_abstract_feature_1,
                get_abstract_feature_2, 
                # get_abstract_feature_3, 
                get_abstract_feature_4, 
                get_abstract_feature_5]


    all_features = []
    all_ys = [1, 0, 1]
    for task in ['task_1', 'task_2', 'task_3']:
        values = get_values(task)

        world, first_domino_body, last_domino_body, bowling_ball_body, beam_body, domino_bodies, ball_body = get_world(*values)
        rep = StructureRep(domino_bodies, ball_body)
        
        features = [f(rep) for f in programs]
        
        log.info(f'Feature for task {task} = {features}')
        all_features.append(features)
            
    
    model = LogisticRegression(
        penalty='l1',         # L2 regularization by default
        solver='liblinear',   # Recommended solver for small or binary datasets
        max_iter=1000,         # Increase if the model struggles to converge
        verbose=True
    )

    # Fit the model
    model.fit(all_features * 10, all_ys * 10)   
    log.info(model.coef_)


if __name__ == '__main__':
    main()