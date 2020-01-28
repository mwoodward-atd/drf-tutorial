from django.urls import include, path

from rest_framework.routers import DefaultRouter

from snippets import views


router = DefaultRouter()
router.register('snippets', views.SnippetViewSet)
router.register('users', views.UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
