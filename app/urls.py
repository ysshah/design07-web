from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='calendar', permanent=False)),
    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^recipes/$', views.recipes, name='recipes'),
    url(r'^recipes/add/$', views.add_recipes, name='add_recipes'),
    url(r'^pantry/$', views.pantry, name='pantry'),
    url(r'^pantry/add/$', views.add_ingredients, name='add_ingredients'),

    # Ajax
    url(r'^view-recipe/$', views.view_recipe, name='view-recipe'),
    url(r'^view-mealplan/$', views.view_mealplan, name='view-mealplan'),
    url(r'^calendar-dates/$', views.calendar_dates, name='calendar-dates'),
]
