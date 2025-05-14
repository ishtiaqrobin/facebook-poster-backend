from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from dotenv import load_dotenv
 
load_dotenv()

FACEBOOK_CLIENT_ID = os.getenv("SOCIAL_AUTH_FACEBOOK_KEY")

@csrf_exempt
def facebook_login(request):
    if request.method == "POST":
        next_url = request.POST.get("next", "https://facebook-poster.ezbitly.com")
        facebook_auth_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth?"
            f"client_id={FACEBOOK_CLIENT_ID}&"
            f"redirect_uri=https://facebook-poster-backend.ezbitly.com/facebook/callback/&"
            f"state={next_url}&"
            f"scope=email,public_profile,pages_show_list,pages_manage_posts,pages_read_engagement"
        )
        return JsonResponse({"redirect_url": facebook_auth_url})
    return JsonResponse({"error": "Method not allowed"}, status=405)
