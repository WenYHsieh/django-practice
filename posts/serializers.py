from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        # specify the model to be serialized
        model = Post
        # fields that should be included in the serialization
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'created_by']
        # fields that should not be modified through any API
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def validate(self, data):
        if 'title' not in data:
            raise serializers.ValidationError({"title": "Title is required."})
        if 'content' not in data:
            raise serializers.ValidationError({"content": "Content is required."})
        return data