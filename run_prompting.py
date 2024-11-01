
import hydra
import logging
from openai_hf_interface import choose_provider, create_llm


from prompts import *


# init_logger() # Don't need this if already using hydra
log = logging.getLogger('main')
log.setLevel(logging.INFO)


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(config):
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    choose_provider(config.provider)

    llm = create_llm('gpt-4o-2024-08-06' if config.provider == 'openai' else 'openai/gpt-4o-2024-08-06')
    llm.setup_cache('disk', database_path=config.database_path)
    llm.set_default_kwargs({'timeout': 60})
    
    abstract_features = [
        "Domino Spacing and Alignment",
        "Initial Force Applied",
        "Beam Stability and Balance",
        "Ball Position Relative to the Last Domino",
        "Domino Size and Mass Variation",
    ]
    
    outputs = llm.prompt([abstract_feature_prompt.format(abstract_feature=abstract_feature) for abstract_feature in abstract_features], 
                         temperature = 0)
    
    for abstract_feature, output in zip(abstract_features, outputs):
        log.info(f'Abstract feature = "{abstract_feature}"')
        log.info(output)
    
    
    

if __name__ == '__main__':
    main()