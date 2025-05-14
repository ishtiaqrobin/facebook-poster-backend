from django.shortcuts import render
import requests
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FacebookToken, FacebookPage
from .serializers import FacebookPageSerializer, FacebookPostSerializer

logger = logging.getLogger(__name__)

class FacebookViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _get_user_token(self):
        try:
            return FacebookToken.objects.get(user=self.request.user).access_token
        except FacebookToken.DoesNotExist:
            return None

    def _get_page_token(self, page_id):
        try:
            return FacebookPage.objects.get(user=self.request.user, page_id=page_id).access_token
        except FacebookPage.DoesNotExist:
            return None

    @action(detail=False, methods=['get'])
    def pages(self, request):
        user_token = self._get_user_token()
        if not user_token:
            return Response(
                {"error": "No Facebook token found. Please login with Facebook first."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            # Get user's pages
            response = requests.get(
                'https://graph.facebook.com/v18.0/me/accounts',
                params={'access_token': user_token}
            )
            response.raise_for_status()
            pages_data = response.json().get('data', [])

            # Update or create pages in database
            for page in pages_data:
                FacebookPage.objects.update_or_create(
                    user=request.user,
                    page_id=page['id'],
                    defaults={
                        'name': page['name'],
                        'access_token': page['access_token']
                    }
                )

            # Get pages from database
            pages = FacebookPage.objects.filter(user=request.user)
            serializer = FacebookPageSerializer(pages, many=True)
            return Response(serializer.data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Facebook pages: {str(e)}")
            return Response(
                {"error": "Failed to fetch Facebook pages"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def post(self, request):
        serializer = FacebookPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page_id = serializer.validated_data['page_id']
        page_token = self._get_page_token(page_id)
        
        if not page_token:
            return Response(
                {"error": "Page not found or no access token available"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Prepare post data
            post_data = {
                'message': serializer.validated_data['message'],
                'access_token': page_token
            }

            # Add image URL if provided
            if serializer.validated_data.get('image_url'):
                post_data['url'] = serializer.validated_data['image_url']

            # Make the post
            response = requests.post(
                f'https://graph.facebook.com/v18.0/{page_id}/photos' if 'url' in post_data else f'https://graph.facebook.com/v18.0/{page_id}/feed',
                data=post_data
            )
            response.raise_for_status()

            return Response({
                "message": "Post created successfully",
                "post_id": response.json().get('id')
            })

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating Facebook post: {str(e)}")
            return Response(
                {"error": "Failed to create Facebook post"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def home(request):
    return render(request, 'home.html')
