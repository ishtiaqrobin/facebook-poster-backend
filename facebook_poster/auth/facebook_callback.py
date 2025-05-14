import requests
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.middleware.csrf import get_token
import logging
import datetime
import os
from dotenv import load_dotenv
from ..models import FacebookToken, FacebookPage

load_dotenv()

FACEBOOK_CLIENT_ID = os.getenv("SOCIAL_AUTH_FACEBOOK_KEY")
FACEBOOK_CLIENT_SECRET = os.getenv("SOCIAL_AUTH_FACEBOOK_SECRET")

# Configure logging
logger = logging.getLogger(__name__)

@csrf_exempt
def facebook_callback(request):
    try:
        csrf_token = get_token(request)
        code = request.GET.get("code")
        next_url = request.GET.get("state", "https://facebook-poster.ezbitly.com")
        
        if not code:
            return JsonResponse({"error": "Authorization code not provided"}, status=400)

        # Exchange the code for a token
        token_response = requests.post(
            "https://graph.facebook.com/v18.0/oauth/access_token",
            data={
                "client_id": FACEBOOK_CLIENT_ID,
                "client_secret": FACEBOOK_CLIENT_SECRET,
                "redirect_uri": "https://facebook-poster-backend.onrender.com/facebook/callback/",
                "code": code,
            }
        )
        token_data = token_response.json()

        if "access_token" not in token_data:
            return JsonResponse({"error": "Failed to retrieve access token"}, status=400)

        # Retrieve user info using the access token
        user_info = requests.get(
            "https://graph.facebook.com/me",
            params={
                "fields": "id,email,first_name,last_name,picture",
                "access_token": token_data["access_token"]
            }
        ).json()

        email = user_info.get("email")
        first_name = user_info.get("first_name", "")
        last_name = user_info.get("last_name", "")
        profile_image = user_info.get("picture", {}).get("data", {}).get("url", "")

        if not email:
            return JsonResponse({"error": "Email not provided"}, status=400)

        # Create or get user
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name
            }
        )

        # Save Facebook token
        facebook_token, _ = FacebookToken.objects.update_or_create(
            user=user,
            defaults={
                "access_token": token_data["access_token"]
            }
        )

        # Fetch and save user's Facebook pages
        pages_response = requests.get(
            "https://graph.facebook.com/v18.0/me/accounts",
            params={"access_token": token_data["access_token"]}
        ).json()

        for page in pages_response.get("data", []):
            FacebookPage.objects.update_or_create(
                user=user,
                page_id=page["id"],
                defaults={
                    "name": page["name"],
                    "access_token": page["access_token"]
                }
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Set secure cookies
        response = HttpResponseRedirect(
            f"{next_url}?access_token={access_token}&refresh_token={refresh_token}"
        )

        # Set secure cookies with proper security settings
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Strict",
            path="/",
            expires=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="Strict",
            path="/",
            expires=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        )

        response.set_cookie(
            key="csrftoken",
            value=csrf_token,
            httponly=False,
            secure=True,
            samesite="Strict",
            path="/",
            expires=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        )

        return response

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)
