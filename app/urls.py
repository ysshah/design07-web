from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='calendar', permanent=False)),
    url(r'^add/$', views.add, name='add'),
    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^recipes/$', views.recipes, name='recipes'),
    url(r'^recipes/(?P<recipe_name>.+)/$', views.view_recipe, name='view_recipe'),
    url(r'^pantry/$', views.pantry, name='pantry'),

    # Ajax
    url(r'^view-mealplan/$', views.view_mealplan, name='view-mealplan'),
    url(r'^calendar-dates/$', views.calendar_dates, name='calendar-dates'),
]
