from django.urls import path
from . import views

app_name = 'translator'

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # Main pages
    path('',              views.index,      name='index'),
    path('history/',      views.history,    name='history'),
    path('favorites/',    views.favorites,  name='favorites'),
    path('analytics/',    views.analytics,  name='analytics'),
    path('batch-page/',   views.batch_page, name='batch_page'),
    path('phrasebook/',   views.phrasebook, name='phrasebook'),
    path('export/csv/',   views.export_csv, name='export_csv'),

    # API endpoints
    path('translate/',           views.translate_text,    name='translate'),
    path('batch/',               views.batch_translate,   name='batch_translate'),
    path('add-favorite/',        views.add_favorite,      name='add_favorite'),
    path('delete/<int:pk>/',     views.delete_translation,name='delete_translation'),
    path('delete-fav/<int:pk>/', views.delete_favorite,   name='delete_favorite'),
    path('stats/',               views.stats_view,        name='stats'),
]