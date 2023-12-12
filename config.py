BG_MODEL_ID = "auhide/chef-gpt"
EN_MODEL_ID = "auhide/chef-gpt-en"
BG_TOKENIZER_PATH = "./tokenizers/bg-tokenizer"
EN_TOKENIZER_PATH = "./tokenizers/en-tokenizer"

EN_LANG, BG_LANG = "🇬🇧 English", "🇧🇬 Bulgarian"

TEXTS = {
    BG_LANG: {
        "chef_prep_1": "Готвачът се приготвя...",
        "chef_prep_2": "Готвачът опреснява знанията си...",
        "header": "Изкуствен Готвач",
        "caption_1": "Въвеждането на конкретните количества на продуктите помага на Готвача. Например, вместо 'брашно' - '1 ч.ч. брашно' или '250 гр брашно'. Все пак Готвачът иска да Ви предложи перфектните рецепти!",
        "caption_2": "Ако не сте доволни от рецептата, може да кликнете 'Създай рецепта' повторно - Готвачът ще се опита да измисли нещо ново.",
        "ingredients_expander": "Създай рецепта от съставки",
        "ingredient_placeholder": "Въведи съставка",
        "ingredients_str": "Съставки",
        "recipe_str": "Рецепта",
        "name_expander": "Създай рецепта от име",
        "recipe_name_placeholder": "Въведи име на рецептата",

        "ingredients_add": "Добави",
        "ingredients_clear": "Изчисти",
        "recipe_create": "Създай рецепта",
        "chef_thinking": "Готвачът измисля рецепта, бъдете търпеливи...",
    },
    EN_LANG: {
        "chef_prep_1": "The Chef is getting ready...",
        "chef_prep_2": "The Chef goes over his recipes...",
        "header": "Artificial Chef",
        "caption_1": "You can add input ingredients 1-by-1 or multiple at once, using commas as a delimiter.",
        "caption_2": "If you are not happy with the generated recipe, you can ask the Chef one more time by clicking the button 'Generate recipe'. He'll try to figure something new out.",
        "ingredients_expander": "Create recipe from ingredients",
        "ingredient_placeholder": "Enter ingredient",
        "ingredients_str": "Ingredients",
        "recipe_str": "Recipe",
        "name_expander": "Create recipe from name",
        "recipe_name_placeholder": "Enter recipe name",

        "ingredients_add": "Add",
        "ingredients_clear": "Clear",
        "recipe_create": "Create recipe",
        "chef_thinking": "The Chef is creating a recipe, be patient...",
    }
}
