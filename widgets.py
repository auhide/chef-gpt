import re
import logging

from transformers import AutoTokenizer, AutoModelForCausalLM


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
        top_p=0.95,
        num_beams=3
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
        top_p=0.95,
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


def based_on_ingredients_widget(st, ingredient, tokenizer, model):
    if st.button("Добави", use_container_width=True):
        if ingredient.strip() != "":
            st.session_state.ingredients.append(ingredient)

    if st.button("Изчисти", use_container_width=True):
        st.session_state.ingredients = []
        st.session_state.recipe = []

    if st.button(
        "Създай рецепта", 
        key="btn1",
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
                    tokenizer=tokenizer, model=model,
                    do_sample=True
                )


def based_on_title_widget(st, title, tokenizer, model):
    if st.button(
        "Създай рецепта", 
        key="btn2"
    ):
        if title:
            with st.spinner("Готвачът измисля рецепта, бъдете търпеливи..."):
                logging.info("Generating recipe...")
                title_input = f"[TTL]{title}[ING]"
                st.session_state.full_recipe = _generate_full_recipe(
                    title_input, 
                    tokenizer=tokenizer, model=model,
                    do_sample=True
                )
