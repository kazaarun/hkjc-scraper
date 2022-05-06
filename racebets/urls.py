from django.urls import path, re_path
from racebets import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('bet-results', views.bet_results),

]
