from django.urls import path
from .views import (
    RegisterView, CategoryListCreateView, CategoryDetailView,
    PhotoListCreateView, PhotoDetailView, LikeToggleView,
    CommentListCreateView, AdminStatsView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("categories/", CategoryListCreateView.as_view(), name="categories"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),

    path("photos/", PhotoListCreateView.as_view(), name="photos"),
    path("photos/<int:pk>/", PhotoDetailView.as_view(), name="photo-detail"),
    path("photos/<int:photo_id>/like/", LikeToggleView.as_view(), name="photo-like"),
    path("photos/<int:photo_id>/comments/", CommentListCreateView.as_view(), name="photo-comments"),

    path("admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
]