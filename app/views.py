import calendar as pycal
import datetime
import boto3

from django.shortcuts import render

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
recipesTable = dynamodb.Table('CookSmartRecipes')
calendarTable = dynamodb.Table('CookSmartCalendar')
pantryTable = dynamodb.Table('CookSmartPantry')

CAL = pycal.Calendar(6)

MEALTYPES = ['Breakfast', 'Lunch / Dinner', 'Dessert']
YMD = '%Y-%m-%d'


def incrMonthYear(year, month, delta=1):
    if month == 1 and delta == -1:
        return year - 1, 12
    elif month == 12 and delta == 1:
        return year + 1, 1
    return year, month + delta


def calendar(request):
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
        'calendar_selected': 'selected'
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


def calendar_add(request):
    context = {
        'today': datetime.date.today().strftime(YMD)
    }
    return render(request, 'calendar_add.html', context)


def view_mealplan(request):
    return render(request, 'calendar_mealplan.html')


def recipes(request, recipe_name=None):
    items = recipesTable.scan()['Items']
    mealTypes = []
    for mealType in MEALTYPES:
        mealTypes.append(
            (mealType, [r for r in items if r['MealType'] == mealType])
        )
    context = {
        'mealTypes': mealTypes,
        'recipes_selected': 'selected'
    }
    return render(request, 'recipes.html', context)


def recipes_add(request):
    return render(request, 'recipes_add.html')


def view_recipe(request, recipe_name):
    query = recipesTable.get_item(Key={'RecipeName': recipe_name})
    if 'Item' in query:
        context = {
            'recipe': splitByNewline(query['Item']),
            'page_title': recipe_name + ' | '
        }
        return render(request, 'view_recipe.html', context)
    raise Http404("Recipe does not exist.")


def pantry(request):
    items = pantryTable.scan()['Items']
    today = datetime.datetime.today()
    for item in items:
        exp = datetime.datetime.strptime(item['ExpirationDate'], YMD)
        item['DaysLeft'] = (exp - today).days
    context = {
        'items': items,
        'pantry_selected': 'selected'
    }
    return render(request, 'pantry.html', context)


def pantry_add(request):
    return render(request, 'pantry_add.html')


def splitByNewline(recipe):
    recipe['Ingredients'] = recipe['IngredientsList'].split('\n')
    if 'PrepDirections' in recipe:
        recipe['Directions'] = recipe['PrepDirections'].split('\n')
    return recipe
