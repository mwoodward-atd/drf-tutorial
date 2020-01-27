from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from snippets import views


app_name = 'snippets'


urlpatterns = [
    path('snippets/', views.SnippetList.as_view(), name='snippets-list'),
    path('snippets/<int:pk>/', views.SnippetDetail.as_view(), name='snippets-detail'),
    path('users/', views.UserList.as_view(), name='users-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='users-detail')
]

urlpatterns = format_suffix_patterns(urlpatterns)
