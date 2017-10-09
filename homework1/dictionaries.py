"""
    The dictionaries presented here are regular expressions, not simple words. So we can easily handle abbreviations and
    plurals or for instances, berries occurrences that we can shorten in [a-z]*berr(y|ies) or nuts: [a-z]*nuts?
"""

"""
    undesirables are words that shouldn't be at the beginning of an ingredient list item (for instance, when people use
    lists to describe the actions to realize the receipt
    This should mainly be adverbs, pronouns and infinitive verb forms
"""
undesirables = [
    'reserve',
    'apply',
    'arrange',
    'reduce',
    'continue',
    'blend',
    'assemble',
    'your?',
    'there',
    'peel',
    'spray',
    'split',
    'break',
    'begin',
    'coat',
    'whisk',
    'strain',
    'garnish',
    'process',
    'transfer',
    'i',
    'he',
    'she',
    'we',
    'they',
    'in',
    'bring',
    'place',
    'roll',
    'heat',
    'take',
    'remove',
    'let',
    'add',
    'leave',
    'put',
    'scoop',
    'pour',
    'preheat', 'pre-heat',
    'grease',
    'sprinkle',
    'combine',
    'mix',
    'while',
    'carefully',
    'serve',
    'line',
    'enjoy',
    'repeat',
    'unroll',
    'bake',
    'cool',
    'spoon',
    'slowly',
    'quickly',
    'cream',
    'stir',
    'fold',
    'separate',
    'using',
    'store',
    'whip',
    'spread',
    'crush',
    'press',
    'set',
    'wash',
    'wait',
    'cover',
    'gently',
    'refrigerate',
    'melt',
    'dip',
    'lay',
    'chill',
    'microwave',
    'use',
    'allow',
    'drop',
    'beat',
    'swirl',
    'be',
    'then',
    'cook',
    'boil',
    'pile',
    'if',
    'slice',
    'once',
    'brush',
    'with',
    'pipe',
    'slightly',
    'butter',
    'soak',
    'insert',
    'dust',
    'before',
    'skim',
    'no',
]

""" some units, simply! """
units = [
    'g\.?', 'kg\.?',
    'teaspoons?', 'tsps?\.?',
    'tablespoons?', 'tbsps?\.?',
    'pounds?',
    'lbs?\.?',
    'jars?',
    'drops?',
    'box(es)?',
    'bottles?',
    'bags?',
    'zests?',
    'ounces?', 'oz\.?',
    'cups?', 'c\.?',
    'cloves?',
    'sticks?',
    'pinch(es)?',
    'packets?', 'pkgs?\.?',
]

'''
    The list of ingredients is quite tricky, because we have to handle the fact we can say 'pepper sauce', or things
    like that. For that reason, spices are at the end, some more generics at the beginning, and a good trade-off in the
    middle of them to handle the cases we have encountered (almond milk, ...)
'''
ingredients = [
    # Generics, come last in the phrase while still the most important ->
    'marinade',

    'cremes?',
    'seeds',
    'fillets?'
    'creams?',
    'juices?',
    'seasoning',
    'oils?',
    'powders?',
    'sauces?',
    'syrup',
    'extracts?',

    # Shouldn't be before generics if more
    'mix(es)?',
    'paste',
    'pudding',
    'lea(f|ves)',
    'coating',
    'rolls?',
    'flakes?',
    'buns?',
    'cornstarch',
    'sprinkles?',
    'crumbs?',
    'crackers?',
    'popcorns?',
    'crusts?',
    'chips',
    'gelatins?',
    'oats?',
    'flour',
    'liners?',
    'cereals?',
    'cakes?',
    'macaroons?',
    'marshmallows?',
    'blooms?',
    'cookies?',

    'oreos?',
    'nutella',

    # Water, vinegar, soda and milky products
    'water',
    'vinegar',
    'soda',
    'milk',

    'yogurt',
    'cheeses?',
    'cheddar',
    'butters?',
    'margarine',

    # alcohols
    'rum',
    'vodkas?',

    'liquids?',
    'zests?',

    # Fruits
    'fruits?',
    'preserves',
    'limes?',

    'cocoa',
    'cacao',
    '[a-z]*nuts?',
    'pineapples?',
    'peach(es)?',
    'bananas?',
    'pistachios?',
    'almonds?',
    'oranges?',
    'apples?',
    '[a-z]*berr(y|ies)',
    'cherr(y|ies)',
    'lemons?',
    'kiwis?',

    # Vegetables
    'avocados?',
    'olives?',
    'onions?',
    'carrots?',
    'tomato(es)?',
    'beans?',

    # Animals
    'meats?',
    'steaks?',
    'ribs?',
    'beef',
    'lamb',
    'salmons?',
    'fish(es)?',

    'turkeys?',
    'chickens?',
    'yolks?',
    'eggs?',

    # Come first
    'chocolates?',
    'rice',
    'nutmegs?',
    'tapiocas?',
    'cinnamon',
    'stevia',
    'molasses',
    'cardamoms?',
    'salt',
    'sugar',
    'vanilla',
    'honey',
    'pepper',
    'garlic',
    'ginger',
    'ketchup',
    'oregano',
    'cumin',
    'paprika',
    'parsley',
]