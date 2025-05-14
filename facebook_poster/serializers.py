from rest_framework import serializers
from .models import FacebookPage

class FacebookPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacebookPage
        fields = ['id', 'page_id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class FacebookPostSerializer(serializers.Serializer):
    page_id = serializers.CharField(required=True)
    message = serializers.CharField(required=True)
    image_url = serializers.URLField(required=False, allow_null=True) 