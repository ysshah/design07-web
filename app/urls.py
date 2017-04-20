from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='calendar', permanent=False)),
    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^recipes/$', views.recipes, name='recipes'),
    url(r'^pantry/$', views.pantry, name='pantry'),

    url(r'^view-recipe/$', views.view_recipe, name='view-recipe'),
]
