from django.shortcuts import render
import requests
import logging
import json
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FacebookToken, FacebookPage
from .serializers import FacebookPageSerializer, FacebookPostSerializer
from django.http import HttpResponse

logger = logging.getLogger(__name__)

def parse_form_data(request):
    """Helper function to parse FormData and handle JSON fields"""
    data = request.data.copy()
    files = request.FILES.copy()
    
    # Parse hashtag if it's a JSON string
    if 'hashtag' in data:
        try:
            if isinstance(data['hashtag'], str):
                data['hashtag'] = json.loads(data['hashtag'])
        except json.JSONDecodeError:
            logger.error(f"Failed to parse hashtag JSON: {data['hashtag']}")
            data['hashtag'] = []
    
    return data, files

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
                        'access_token': page['access_token'],
                        'category': page.get('category', ''),
                        'category_id': page.get('category_list', [{}])[0].get('id', ''),
                        'tasks': ','.join(page.get('tasks', []))
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
    def create_post(self, request):
        try:
            logger.info("=== Create Post Request Started ===")
            logger.info(f"Request Headers: {request.headers}")
            logger.info(f"User: {request.user}")
            logger.info(f"Auth: {request.auth}")

            if not request.user.is_authenticated:
                logger.error("User is not authenticated")
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            logger.info(f"Request Data: {request.data}")
            logger.info(f"Request Files: {request.FILES}")

            # Parse FormData
            data, files = parse_form_data(request)
            logger.info(f"Parsed Data: {data}")
            logger.info(f"Parsed Files: {files}")

            serializer = FacebookPostSerializer(data=data)
            if not serializer.is_valid():
                logger.error(f"Serializer Validation Errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            page_id = serializer.validated_data['page_id']
            page_token = serializer.validated_data['page_access_token']
            logger.info(f"Page ID: {page_id}")
            logger.info(f"Page Token: {page_token}")

            # Prepare hashtags
            hashtags = ' '.join([f"#{tag.strip('#')}" for tag in serializer.validated_data['hashtag']])
            logger.info(f"Prepared hashtags: {hashtags}")

            post_data = {
                'message': hashtags,
                'access_token': page_token
            }
            logger.info("Post data prepared")

            # Handle image upload
            if 'image' in files:
                logger.info("Processing image upload")
                files = {'source': files['image']}
                response = requests.post(
                    f'https://graph.facebook.com/v18.0/{page_id}/photos',
                    data=post_data,
                    files=files
                )
            # Handle video upload
            elif 'video' in files:
                logger.info("Processing video upload")
                files = {'source': files['video']}
                response = requests.post(
                    f'https://graph.facebook.com/v18.0/{page_id}/videos',
                    data=post_data,
                    files=files
                )
            else:
                logger.error("No image or video file provided")
                return Response(
                    {"error": "Either image or video must be provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            response.raise_for_status()
            logger.info(f"Facebook API Response: {response.json()}")

            return Response({
                "message": "Post created successfully",
                "post_id": response.json().get('id')
            })

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating Facebook post: {str(e)}")
            logger.error(f"Response content: {e.response.content if hasattr(e, 'response') else 'No response content'}")
            return Response(
                {"error": f"Failed to create Facebook post: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error in create_post: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {"error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            logger.info("=== Create Post Request Ended ===")

def home(request):
    return HttpResponse("Server is running on Cpanel!")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def facebook_profile(request):
    try:
        fb_token = FacebookToken.objects.get(user=request.user)
    except FacebookToken.DoesNotExist:
        return Response({'error': 'No Facebook token found'}, status=400)
    url = 'https://graph.facebook.com/v18.0/me'
    params = {
        'fields': 'id,name,email,picture',
        'access_token': fb_token.access_token
    }
    r = requests.get(url, params=params)
    return Response(r.json())

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def facebook_page(request):
#     try:
#         fb_token = FacebookToken.objects.get(user=request.user)
#     except FacebookToken.DoesNotExist:
#         return Response({'error': 'No Facebook token found'}, status=400)
#     url = 'https://graph.facebook.com/v18.0/me/accounts'
#     params = {
#         'access_token': fb_token.access_token
#     }
#     r = requests.get(url, params=params)
#     return Response(r.json())





