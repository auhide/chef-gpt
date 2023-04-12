import re
import logging

import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM

from config import MODEL_ID, TOKENIZER_PATH


st.set_page_config(
    page_title="🤖 Изкуствен Готвач",
)


# When there has already been a defined logger in the environment.
if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(
        format="%(asctime)s|%(levelname)s:\t%(message)s",
        level=logging.INFO,
        datefmt="%m/%d/%Y %I:%M:%S %p"
    )


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
        top_p=0.90,
        num_return_sequences=3
    )
    # TODO: Add an option for multiple predictions.
    recipes = tokenizer.batch_decode(output)
    logging.info(f"RECIPES: {recipes}")

    recipe = tokenizer.batch_decode(output)[0]
    # Get the generated recipe - it is up until the 1st [SEP] tag.
    try:
        recipe = re.findall(r"\[REC\](.+?)\[SEP\]", recipe)[0]
    except IndexError:
        # When the generated recipe is not finished - return the generated one
        # up until the last symbol.
        pass

    return recipe


@st.cache_resource(show_spinner=False)
def _get_model():
    return AutoModelForCausalLM.from_pretrained(MODEL_ID)


@st.cache_resource(show_spinner=False)
def _get_tokenizer():
    return AutoTokenizer.from_pretrained(TOKENIZER_PATH)


with st.spinner("Готвачът се приготвя..."):
    chef_gpt = _get_model()

with st.spinner("Готвачът опреснява знанията си..."):
    tokenizer = _get_tokenizer()


st.markdown("<h1 style='text-align: center; color: grey;'>Изкуствен Готвач</h1>", unsafe_allow_html=True)


if "ingredients" not in st.session_state:
    st.session_state.ingredients = []

if "recipe" not in st.session_state:
    st.session_state.recipe = []


ingredient = st.text_input('', placeholder="Въведи съставка")

if st.button("Добави", use_container_width=True):
    if ingredient.strip() != "":
        st.session_state.ingredients.append(ingredient)

if st.button("Изчисти", use_container_width=True):
    st.session_state.ingredients = []
    st.session_state.recipe = []


if st.button(
    "Създай рецепта", 
    disabled=True 
    if st.session_state.ingredients == [] 
    else False,
    use_container_width=True
):
    if st.session_state.ingredients:
        with st.spinner("Готвачът измисля рецепта, бъдете търпеливи..."):
            logging.info("Generating recipe...")
            curr_ingredients = f"[ING]{'[EOL]'.join(st.session_state.ingredients)}[REC]"
            st.session_state.recipe = _generate_recipe(
                curr_ingredients, 
                tokenizer=tokenizer, model=chef_gpt,
                # TODO: Control the randomness.
                do_sample=True
            )


res_col1, res_col2 = st.columns(2)

# Ingredients subsection.
with res_col1:
    if st.session_state.ingredients:
        st.markdown("<h3 style='text-align: center; color: grey;'>Съставки</h3>", unsafe_allow_html=True)
        st.markdown(f"{', '.join(st.session_state.ingredients)}")

# Recipe subsection.
with res_col2:
    if st.session_state.ingredients:
        st.markdown("<h3 style='text-align: center; color: grey;'>Рецепта</h3>", unsafe_allow_html=True)
        
        if st.session_state.recipe:
            st.markdown(st.session_state.recipe)
