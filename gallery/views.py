from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from .models import Photo, Category, Comment, Like, User
from .serializers import (
    UserRegisterSerializer, PhotoListSerializer, PhotoCreateSerializer,
    CategorySerializer, CommentSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from django.db.models import Count

# Регистрация
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

# Категории - CRUD (админ)
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

# Фото - список и загрузка
class PhotoListCreateView(generics.ListCreateAPIView):
    queryset = Photo.objects.filter(is_public=True).select_related("owner").prefetch_related("categories")
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at","views"]
    search_fields = ["title","description","owner__username","categories__name"]
    pagination_class = None  # или использовать PageNumberPagination из settings

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PhotoCreateSerializer
        return PhotoListSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Детали / редактирование фото
class PhotoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Photo.objects.all().select_related("owner")
    serializer_class = PhotoListSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        # увеличить счётчик просмотров (если анонимный — тоже)
        instance = self.get_object()
        instance.views = models.F('views') + 1
        instance.save(update_fields=['views'])
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# Лайк / анлайк
class LikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, photo_id):
        user = request.user
        try:
            photo = Photo.objects.get(pk=photo_id)
        except Photo.DoesNotExist:
            return Response({"detail":"Not found"}, status=404)
        like, created = Like.objects.get_or_create(user=user, photo=photo)
        if not created:
            # уже был - удаляем (тоггл)
            like.delete()
            return Response({"liked": False})
        return Response({"liked": True})

# Комментарии (создать, список под фото)
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        photo_id = self.kwargs['photo_id']
        return Comment.objects.filter(photo__id=photo_id, is_visible=True).select_related("user")

    def perform_create(self, serializer):
        photo = Photo.objects.get(pk=self.kwargs['photo_id'])
        serializer.save(user=self.request.user, photo=photo)


# Админ: статистика
class AdminStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def get(self, request):
        total_photos = Photo.objects.count()
        active_users = User.objects.annotate(photo_count=Count('photos')).filter(photo_count__gt=0).count()
        top_categories = Category.objects.annotate(photo_count=Count('photos')).order_by('-photo_count')[:10].values('name','photo_count')
        return Response({
            "total_photos": total_photos,
            "active_users": active_users,
            "top_categories": list(top_categories),
        })