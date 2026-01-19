from rest_framework import serializers
from core.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_celebrity']
    
class PostSerializer(serializers.ModelSerializer):
    Author = UserSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'Author', 'content', 'created_at']