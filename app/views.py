import calendar as pycal
import datetime
import boto3

from django.shortcuts import render, redirect
from django.urls import reverse

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
recipesTable = dynamodb.Table('CookSmartRecipes')
calendarTable = dynamodb.Table('CookSmartCalendar')
pantryTable = dynamodb.Table('CookSmartPantry')

CAL = pycal.Calendar(6)

MEALTYPES = ['Breakfast', 'Lunch / Dinner', 'Dessert']
YMD = '%Y-%m-%d'


def add(request):
    context = {
        'today': datetime.date.today().strftime(YMD),
        'recipes': [r['RecipeName'] for r in recipesTable.scan()['Items']],
        'page_title': 'Add | '
    }
    return render(request, 'add.html', context)


def incrMonthYear(year, month, delta=1):
    if month == 1 and delta == -1:
        return year - 1, 12
    elif month == 12 and delta == 1:
        return year + 1, 1
    return year, month + delta


def calendar(request):
    if request.method == 'POST':
        recipes = request.POST.getlist('recipes[]')
        dates = request.POST.getlist('dates[]')
        mealtypes = request.POST.getlist('mealtypes[]')
        for i, recipe in enumerate(recipes):
            if dates[i] and mealtypes[i]:
                item = {
                    'RecipeName': recipe,
                    'Date': dates[i],
                    'MealType': mealtypes[i]
                }
                calendarTable.put_item(Item=item)

    today = datetime.date.today()
    oneday = datetime.timedelta(1)
    dates = []
    items = calendarTable.scan()['Items']
    mealTypes = ['Breakfast', 'Lunch', 'Dinner', 'Dessert']
    for i in range(7):
        day = today + i*oneday
        date = { 'date': day.strftime('%A, %B %d, %Y'), 'meals': [] }
        for item in items:
            if item['Date'] == day.strftime(YMD):
                date['meals'].append((item['MealType'], item['RecipeName']))
        dates.append(date)
    for date in dates:
        date['meals'] = sorted(date['meals'], key=lambda x: mealTypes.index(x[0]))

    context = {
        'dates': dates,
        'addtype': 'meals'
    }
    return render(request, 'calendar.html', context)


def calendar_dates(request):
    date = datetime.datetime.strptime(request.POST['ym'], '%Y-%m')
    day = datetime.timedelta(1)
    context = {
        'month_year': date.strftime('%B %Y'),
        'prev': '{}-{:02d}'.format(*incrMonthYear(date.year, date.month, -1)),
        'next': '{}-{:02d}'.format(*incrMonthYear(date.year, date.month, 1)),
        'days': CAL.monthdayscalendar(date.year, date.month)
    }
    return render(request, 'calendar_dates.html', context)


def view_mealplan(request):
    return render(request, 'calendar_mealplan.html')


def recipes(request):
    if request.method == 'POST':
        recipe_name = request.POST['RecipeName']
        ingredients = [i for i in request.POST.getlist('Ingredients[]') if i]
        directions = [d for d in request.POST.getlist('Directions[]') if d]
        if recipe_name and ingredients:
            item = {
                'RecipeName': recipe_name,
                'IngredientsList': '\n'.join(ingredients),
                'MealType': request.POST['MealType']
            }
            if directions:
                item['PrepDirections'] = '\n'.join(directions)
            recipesTable.put_item(Item=item)
            return redirect('view_recipe', recipe_name=recipe_name)
        return redirect(reverse('add') + '#add-recipe')

    items = recipesTable.scan()['Items']
    mealTypes = []
    for mealType in MEALTYPES:
        mealTypes.append(
            (mealType, [r for r in items if r['MealType'] == mealType])
        )
    context = {
        'mealTypes': mealTypes,
        'placeholder': 'Search recipes...',
        'addtype': 'recipe',
        'page_title': 'All Recipes | '
    }
    return render(request, 'recipes.html', context)


def splitByNewline(recipe):
    recipe['Ingredients'] = recipe['IngredientsList'].split('\n')
    if 'PrepDirections' in recipe:
        recipe['Directions'] = recipe['PrepDirections'].split('\n')
    return recipe


def view_recipe(request, recipe_name):
    if request.method == 'POST':
        recipesTable.delete_item(Key={'RecipeName': recipe_name})
        return redirect('recipes')

    query = recipesTable.get_item(Key={'RecipeName': recipe_name})
    if 'Item' in query:
        context = {
            'recipe': splitByNewline(query['Item']),
            'page_title': recipe_name + ' | ',
            'addtype': 'recipe'
        }
        return render(request, 'view_recipe.html', context)
    raise Http404("Recipe does not exist.")


def pantry(request):
    if request.method == 'POST':
        ingredients = request.POST.getlist('ingredients[]')
        categories = request.POST.getlist('categories[]')
        dates = request.POST.getlist('dates[]')
        quantities = request.POST.getlist('quantities[]')
        units = request.POST.getlist('units[]')
        for i, ingredient in enumerate(ingredients):
            if ingredient and dates[i] and quantities[i]:
                item = {
                    'IngredientName': ingredient,
                    'ExpirationDate': dates[i],
                    'IngredientAmount': quantities[i],
                    'Category': categories[i],
                }
                if units[i]:
                    item['IngredientUnit'] = units[i]
                pantryTable.put_item(Item=item)

    categories = ['Fruits', 'Vegetables', 'Dairy', 'Spices', 'Meats']
    items = pantryTable.scan()['Items']
    ingredients = {}
    today = datetime.datetime.today()
    for item in items:
        exp = datetime.datetime.strptime(item['ExpirationDate'], YMD)
        item['DaysLeft'] = (exp - today).days
        if item['Category'] in ingredients:
            ingredients[item['Category']].append(item)
        else:
            ingredients[item['Category']] = [item]

    context = {
        'ingredients': ingredients,
        'page_title': 'Pantry | ',
        'placeholder': 'Search ingredients...',
        'addtype': 'ingredients'
    }
    return render(request, 'pantry.html', context)
