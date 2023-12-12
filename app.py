import logging

import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM

from config import (
    BG_MODEL_ID, EN_MODEL_ID, 
    BG_TOKENIZER_PATH, EN_TOKENIZER_PATH,
    EN_LANG, BG_LANG,
    TEXTS,
)
from widgets import based_on_ingredients_widget, based_on_title_widget


st.set_page_config(
    page_title="🤖 Изкуствен Готвач",
)


# Hiding the default Streamlit hamburger and text.
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


# When there has already been a defined logger in the environment.
if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(
        format="%(asctime)s|%(levelname)s:\t%(message)s",
        level=logging.INFO,
        datefmt="%m/%d/%Y %I:%M:%S %p"
    )


@st.cache_resource(show_spinner=False)
def _get_model(lang: str):
    if lang == BG_LANG:
        return AutoModelForCausalLM.from_pretrained(BG_MODEL_ID)
    
    return AutoModelForCausalLM.from_pretrained(EN_MODEL_ID)


@st.cache_resource(show_spinner=False)
def _get_tokenizer(lang: str):
    if lang == BG_LANG:
        return AutoTokenizer.from_pretrained(BG_TOKENIZER_PATH)
    
    return AutoTokenizer.from_pretrained(EN_TOKENIZER_PATH)


language = st.selectbox("", (EN_LANG, BG_LANG))

texts = TEXTS[language]

with st.spinner(texts["chef_prep_1"]):
    chef_gpt = _get_model(lang=language)

with st.spinner(texts["chef_prep_2"]):
    tokenizer = _get_tokenizer(lang=language)


st.markdown(f"<h1 style='text-align: center; color: grey;'>{texts['header']}</h1>", unsafe_allow_html=True)
st.caption(texts["caption_1"])
st.caption(texts["caption_2"])


if "ingredients" not in st.session_state:
    st.session_state.ingredients = []

if "recipe" not in st.session_state:
    st.session_state.recipe = ""

if "full_recipe" not in st.session_state:
    st.session_state.full_recipe = ""


# Generate recipes based on ingredients.
with st.expander(texts["ingredients_expander"]):
    ingredient = st.text_input('', placeholder=texts["ingredient_placeholder"])

    based_on_ingredients_widget(
        st, 
        ingredient=ingredient, 
        tokenizer=tokenizer, model=chef_gpt, 
        texts=texts,
        lang=language
    )

    ing_col1, ing_col2 = st.columns(2)

    # Ingredients subsection.
    with ing_col1:
        if st.session_state.ingredients:
            st.markdown(f"<h3 style='text-align: center; color: grey;'>{texts['ingredients_str']}</h3>", unsafe_allow_html=True)
            st.markdown(f"{', '.join(st.session_state.ingredients)}")

    # Recipe subsection.
    with ing_col2:
        if st.session_state.ingredients:
            st.markdown(f"<h3 style='text-align: center; color: grey;'>{texts['recipe_str']}</h3>", unsafe_allow_html=True)
            
            if st.session_state.recipe:
                st.markdown(st.session_state.recipe)


# TODO: Uncomment this when the English model for name -> recipe generation
# is implemented.
if language == BG_LANG:
    with st.expander(texts["name_expander"]):
        title = st.text_input('', placeholder=texts["recipe_name_placeholder"])

        based_on_title_widget(
            st, 
            title=title, 
            tokenizer=tokenizer, model=chef_gpt,
            texts=texts
        )

        if title:
            st.markdown(f"<h3 style='text-align: center; color: grey;'>{texts['recipe_str']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align: center; color: grey;'>{title}</h4>", unsafe_allow_html=True)
            
            if st.session_state.full_recipe:
                st.markdown(st.session_state.full_recipe)
