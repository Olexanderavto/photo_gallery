from rest_framework import serializers
from .models import User, Photo, Category, Like, Comment
from django.contrib.auth.password_validation import validate_password

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ("id","username","email","full_name","city","country","nickname","password")

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id","name","description")

class PhotoListSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    categories = CategorySerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ("id","title","description","image","owner","categories","created_at","views","likes_count","comments_count","is_public")

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.filter(is_visible=True).count()

class PhotoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ("id","title","description","image","categories","is_public")

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ("id","user","photo","text","created_at","is_visible")
        read_only_fields = ("user","created_at")