import calendar as pycal
import datetime
import boto3

from django.shortcuts import render


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
recipesTable = dynamodb.Table('CookSmartRecipes')
calendarTable = dynamodb.Table('CookSmartCalendar')
pantryTable = dynamodb.Table('CookSmartCalendar')


def calendar(request):
    c = pycal.Calendar(6)
    days = c.monthdayscalendar(2017, 4)

    td = datetime.timedelta(1)
    date = datetime.date.today()
    context = {
        'days': days,
        'dates': [(date + td*i).strftime('%A, %B %d, %Y') for i in range(7)]
    }
    return render(request, 'calendar.html', context)


def recipes(request):
    items = recipesTable.scan()['Items']
    mealTypes = []
    for mealType in ['Breakfast', 'Lunch / Dinner']:
        mealTypes.append(
            (mealType, [r for r in items if r['MealType'] == mealType])
        )
    context = {
        'mealTypes': mealTypes,
        'thisRecipe': splitByNewline(mealTypes[0][1][0])
    }
    return render(request, 'recipes.html', context)


def pantry(request):
    return render(request, 'pantry.html')


def view_recipe(request):
    query = recipesTable.get_item(Key={'RecipeName': request.POST['name']})
    context = {'thisRecipe': splitByNewline(query['Item'])}
    return render(request, 'view_recipe.html', context)


def splitByNewline(recipe):
    recipe['Ingredients'] = recipe['IngredientsList'].split('\n')
    if 'PrepDirections' in recipe:
        recipe['Directions'] = recipe['PrepDirections'].split('\n')
    return recipe
