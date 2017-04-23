import calendar as pycal
import datetime
import boto3

from django.shortcuts import render

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
recipesTable = dynamodb.Table('CookSmartRecipes')
calendarTable = dynamodb.Table('CookSmartCalendar')
pantryTable = dynamodb.Table('CookSmartCalendar')

cal = pycal.Calendar(6)


def incrMonthYear(year, month, delta=1):
    if month == 1 and delta == -1:
        return year - 1, 12
    elif month == 12 and delta == 1:
        return year + 1, 1
    return year, month + delta


def calendar(request):
    today = datetime.date.today()
    day = datetime.timedelta(1)
    context = {
        'dates': [(today + day*i).strftime('%A, %B %d, %Y') for i in range(7)]
    }
    return render(request, 'calendar.html', context)


def calendar_dates(request):
    date = datetime.datetime.strptime(request.POST['ym'], '%Y-%m')
    day = datetime.timedelta(1)
    context = {
        'month_year': date.strftime('%B %Y'),
        'prev': '{}-{:02d}'.format(*incrMonthYear(date.year, date.month, -1)),
        'next': '{}-{:02d}'.format(*incrMonthYear(date.year, date.month, 1)),
        'days': cal.monthdayscalendar(date.year, date.month)
    }
    return render(request, 'calendar_dates.html', context)


def view_mealplan(request):
    return render(request, 'view_mealplan.html')


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


def add_recipes(request):
    return render(request, 'add_recipes.html')


def pantry(request):
    return render(request, 'pantry.html')


def add_ingredients(request):
    return render(request, 'add_ingredients.html')


def view_recipe(request):
    query = recipesTable.get_item(Key={'RecipeName': request.POST['name']})
    context = {'thisRecipe': splitByNewline(query['Item'])}
    return render(request, 'view_recipe.html', context)


def splitByNewline(recipe):
    recipe['Ingredients'] = recipe['IngredientsList'].split('\n')
    if 'PrepDirections' in recipe:
        recipe['Directions'] = recipe['PrepDirections'].split('\n')
    return recipe
