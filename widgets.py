import re
import logging
from typing import Dict, List

from transformers import AutoTokenizer, AutoModelForCausalLM

from config import BG_LANG


def _generate_recipe(
    text: str, 
    tokenizer: AutoTokenizer, 
    model: AutoModelForCausalLM,
    lang: str,
    do_sample=True
) -> str:
    # Convert the text into a vector.
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    
    # Generate text.
    output = model.generate(
        input_ids, 
        do_sample=do_sample, 
        max_length=150, 
        top_p=0.95,
    )

    recipe = tokenizer.batch_decode(output)[0]

    return _parse_ingredients_recipe_prediction(recipe, lang=lang)


def _generate_full_recipe(
    title: str, 
    tokenizer: AutoTokenizer, 
    model: AutoModelForCausalLM,
    do_sample=True
) -> str:
    # Convert the text into a vector.
    input_ids = tokenizer(title, return_tensors="pt").input_ids
    
    # Generate text.
    output = model.generate(
        input_ids, 
        do_sample=do_sample, 
        max_length=200, 
        top_p=0.90,
        num_beams=3
    )

    recipe = tokenizer.batch_decode(output)[0]
    # Get the generated recipe - it is up until the 1st [SEP] tag.
    try:
        recipe = re.findall(r"(\[ING\].+?)\[SEP\]", recipe)[0]
    except IndexError:
        # When the generated recipe is not finished - return the generated one
        # up until the last symbol.
        pass
    recipe = recipe.replace("[ING]", "- ")
    recipe = re.sub(r"\[TTL\][^\-]+", "", recipe)
    recipe = recipe.replace("[EOL]", "\n- ")
    recipe = recipe.replace("[REC]", "\n\n")

    return recipe


def based_on_ingredients_widget(
    st, 
    ingredient: str, 
    tokenizer: AutoTokenizer, 
    model: AutoModelForCausalLM, 
    texts: Dict[str, str],
    lang: str
):
    if st.button(texts["ingredients_add"], use_container_width=True):
        if ingredient.strip() != "":
            st.session_state.ingredients.append(ingredient)

    if st.button(texts["ingredients_clear"], use_container_width=True):
        st.session_state.ingredients = []
        st.session_state.recipe = []

    if st.button(
        texts["recipe_create"], 
        key="btn1",
        disabled=True 
        if st.session_state.ingredients == [] 
        else False,
        use_container_width=True
    ):
        if st.session_state.ingredients:
            with st.spinner(texts["chef_thinking"]):
                logging.info("Generating recipe...")
                # Lowercasing the ingredients.
                st.session_state.ingredients = [
                    ing.lower() 
                    for ing in st.session_state.ingredients
                ]
                curr_ingredients = _prepare_ingredients(
                    st.session_state.ingredients, 
                    lang=lang
                )
                st.session_state.recipe = _generate_recipe(
                    curr_ingredients, 
                    tokenizer=tokenizer, model=model, 
                    lang=lang,
                    do_sample=True
                )


def based_on_title_widget(
    st, 
    title: str, 
    tokenizer: AutoTokenizer, 
    model: AutoModelForCausalLM, 
    texts: Dict[str, str]
):
    if st.button(
        texts["recipe_create"], 
        key="btn2"
    ):
        if title:
            with st.spinner(texts["chef_thinking"]):
                logging.info("Generating recipe...")
                title_input = f"[TTL]{title}[ING]"
                st.session_state.full_recipe = _generate_full_recipe(
                    title_input, 
                    tokenizer=tokenizer, model=model,
                    do_sample=True
                )


def _prepare_ingredients(ingredients: List[str], lang: str):
    if lang == BG_LANG:
        return f"[ING]{'[EOL]'.join(ingredients)}[REC]"

    # This is the English prompt format.
    return f"ingredients>> {','.join(ingredients)}; recipe>>"


def prepare_title(title: str, lang: str):
    # TODO: Implement this when the English model for it has been trained.
    pass


def _parse_ingredients_recipe_prediction(prediction: str, lang: str):
    if lang == BG_LANG:
        # Get the generated recipe - it is up until the 1st [SEP] tag.
        try:
            prediction = re.findall(r"(\[REC\].+$)", prediction)[-1]
            prediction = re.findall(r"\[REC\](.+?)\[SEP\]", prediction)[-1]
        except IndexError:
            pass

        prediction = re.sub(f"\[\w+\]", "", prediction)

        return prediction

    # When the language is English.
    try:
        prediction = re.findall(r"recipe>>([^>]+)<\|endoftext", prediction)[0].strip()
        prediction = "\n".join([
            f"{i + 1}. {pred.capitalize()}" 
            for i, pred in enumerate(prediction.split("\n"))
        ])
    except IndexError:
        prediction = "Give the Chef a little bit more time! Click 'Create recipe' again."

    return prediction