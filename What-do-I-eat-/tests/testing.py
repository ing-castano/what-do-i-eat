from cs50 import SQL


""" add ingridient to the sql database
INGREDIENTS = ['bread', 'cheese', 'chicken', 'eggs', 'tomatoe']
words = 'eggs,tomatoe,chorizo,apple,zarasa'
word = 'chorizo'

db = SQL("sqlite:///recipes.db")

ing = db.execute("select * from ing_table where ingredients=?", word)
if not ing:
    db.execute("INSERT INTO ing_table (ingredients) VALUES (?)", word)
print(ing)
"""


""" UPDATE INGREDIENTS TEST 
INGREDIENTS = ['bread', 'cheese', 'chicken', 'eggs', 'tomatoe']
words = 'eggs ,tomatoe, chorizo,'',zarasa, bell peppers'
wordss = words.split(",")
print(wordss)
    
def update(word):
    for key, ingredient in enumerate(INGREDIENTS):
        if word == '':
            return
        if word == ingredient:
            return
        if word < ingredient:
            INGREDIENTS.insert(key, word)
            return
        if key + 1 == len(INGREDIENTS):
            INGREDIENTS.insert(key + 1, word)
            return

       # print(f"len INGREDIENTS = {len(INGREDIENTS)} AND key={key+1}")

print('BEFORE:') 
print(INGREDIENTS)
for word in wordss:
    update(word.strip(" "))
print('AFTER: ')
print(INGREDIENTS)

"""

