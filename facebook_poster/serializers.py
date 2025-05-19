from rest_framework import serializers
from .models import FacebookPage

class FacebookPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacebookPage
        fields = ['page_id', 'name', 'category', 'category_id', 'access_token']

class FacebookPostSerializer(serializers.Serializer):
    page_id = serializers.CharField(required=True)
    page_access_token = serializers.CharField(required=True)
    hashtag = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        allow_empty=False
    )
    image = serializers.ImageField(required=False, allow_null=True)
    video = serializers.FileField(required=False, allow_null=True)

    def validate(self, data):
        if not data.get('image') and not data.get('video'):
            raise serializers.ValidationError("Either image or video must be provided")
        return data 