from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    full_name = models.CharField("ПІБ", max_length=255)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=50, unique=True)

    def str(self):
        return self.username or self.nickname

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def str(self):
        return self.name

class Photo(models.Model):
    owner = models.ForeignKey("User", related_name="photos", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="photos/%Y/%m/%d/")
    categories = models.ManyToManyField(Category, related_name="photos", blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_public = models.BooleanField(default=True)  # admin can toggle visibility
    views = models.PositiveIntegerField(default=0)

    def str(self):
        return self.title

class Like(models.Model):
    user = models.ForeignKey("User", related_name="likes", on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "photo")

class Comment(models.Model):
    user = models.ForeignKey("User", related_name="comments", on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, related_name="comments", on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True)  # admin moderation

    def str(self):
        return f"Comment by {self.user} on {self.photo}"