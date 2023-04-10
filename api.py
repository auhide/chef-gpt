import re
import logging
import traceback
from typing import Dict, Union, Any

from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModelForCausalLM

from exceptions import MissingParameterError
from config import MODEL_ID, TOKENIZER_PATH


# When there has already been a defined logger in the environment.
if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(
        format="%(asctime)s|%(levelname)s:\t%(message)s",
        level=logging.INFO,
        datefmt="%m/%d/%Y %I:%M:%S %p"
    )


app = FastAPI()


@app.get("/recipe")
def generate(request: Request) -> Dict[str, str]:
    try:
        ingredients = _get_ingredients(request)
        do_sample = _get_random(request)
        logging.info(f"Ingredients: {ingredients}")
        logging.info(f"Random sampling set to: {do_sample}")

        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
        chef_gpt = AutoModelForCausalLM.from_pretrained(MODEL_ID)

        logging.info("Generating recipe...")
        recipe = _generate_recipe(
            ingredients, 
            tokenizer=tokenizer, model=chef_gpt,
            do_sample=do_sample
        )
        logging.info(f"Generated recipe:\n{recipe}")
        
    except MissingParameterError as mte:
        return _response(recipe=None, status_code=400)
    except Exception as exc:
        return _response(recipe=None, status_code=500)

    return _response(recipe=recipe, status_code=200)


def _generate_recipe(
    text: str, 
    tokenizer: AutoTokenizer, 
    model: AutoModelForCausalLM,
    do_sample=True
) -> str:
    # Convert the text into a vector.
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    
    # Generate text.
    output = model.generate(
        input_ids, 
        do_sample=do_sample, 
        max_length=150, 
        top_p=0.90
    )
    recipe = tokenizer.batch_decode(output)[0]
    # Get the generated recipe - it is up until the 1st [SEP] tag.
    try:
        recipe = re.findall(r"\[REC\](.+?)\[SEP\]", recipe)[0]
    except IndexError:
        # When the generated recipe is not finished - return the generated one
        # up until the last symbol.
        pass

    return recipe


def _get_ingredients(request: Request) -> str:
    if "ingredients" not in request.query_params:
        raise MissingParameterError(f"You should pass 'ingredients' to your request! They are a string of comma separated ingredients.")

    # Splitting the initial ingredients string.
    ingredients = request.query_params["ingredients"].split(",")
    # Removing the surrounding whitespace of each ingredient.
    ingredients = [ing.strip() for ing in ingredients]
    # Adding the special tags to the ingredients.
    ingredients = f"[ING]{'[EOL]'.join(ingredients)}[REC]"

    return ingredients


def _get_random(request: Request) -> bool:
    random = request.query_params.get("random", "True")

    if random.lower() == "true":
        return True
    
    return False


def _response(recipe: Union[str, None], status_code: int, error_message=None) -> Dict[str, Union[str, Any]]:
    if status_code != 200:
        logging.error(traceback.format_exc())
        return {
            "message": error_message,
            "statusCode": status_code
        }

    return {
        "message": {
            "recipe": recipe,
        },
        "statusCode": status_code,
    }
