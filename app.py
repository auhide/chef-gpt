import re
import logging

import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM

from config import MODEL_ID, TOKENIZER_PATH
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
st.caption("Въвеждането на конкретните количества на продуктите помага на Готвача. Например, вместо 'брашно' - '1 ч.ч. брашно' или '250 гр брашно'. Все пак Готвачът иска да Ви предложи перфектните рецепти!")
st.caption("Ако не сте доволни от рецептата, може да кликнете 'Създай рецепта' повторно - Готвачът ще се опита да измисли нещо ново.")


if "ingredients" not in st.session_state:
    st.session_state.ingredients = []

if "recipe" not in st.session_state:
    st.session_state.recipe = ""

if "full_recipe" not in st.session_state:
    st.session_state.full_recipe = ""


# Generate recipes based on ingredients.
with st.expander("Създай рецепта от съставки"):
    ingredient = st.text_input('', placeholder="Въведи съставка")

    based_on_ingredients_widget(
        st, 
        ingredient=ingredient, 
        tokenizer=tokenizer, model=chef_gpt
    )

    ing_col1, ing_col2 = st.columns(2)

    # Ingredients subsection.
    with ing_col1:
        if st.session_state.ingredients:
            st.markdown("<h3 style='text-align: center; color: grey;'>Съставки</h3>", unsafe_allow_html=True)
            st.markdown(f"{', '.join(st.session_state.ingredients)}")

    # Recipe subsection.
    with ing_col2:
        if st.session_state.ingredients:
            st.markdown("<h3 style='text-align: center; color: grey;'>Рецепта</h3>", unsafe_allow_html=True)
            
            if st.session_state.recipe:
                st.markdown(st.session_state.recipe)


with st.expander("Създай рецепта от име"):
    title = st.text_input('', placeholder="Въведи име на рецептата")

    based_on_title_widget(
        st, 
        title=title, 
        tokenizer=tokenizer, model=chef_gpt
    )

    if title:
        st.markdown("<h3 style='text-align: center; color: grey;'>Рецепта</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: grey;'>{title}</h4>", unsafe_allow_html=True)
        
        if st.session_state.full_recipe:
            st.markdown(st.session_state.full_recipe)
