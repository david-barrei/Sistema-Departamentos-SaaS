from django.contrib.auth import get_user_model, authenticate, login
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse
from .models import FailedLoginAttempt

User = get_user_model()

class FailedLoginMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.method == "POST" and request.POST.get("login") == '1':
            username = request.POST.get("username")
            user = User.objects.filter(username = username).first()

            if user:
                failed_attempts = FailedLoginAttempt.objects.filter(
                    user = user,
                    attemted_at__gte = timezone.now() - timezone.timedelta(hours=24)
                ).count()

                if failed_attempts >=5:
                    return redirect(reverse("users:account_locked"))
                
                password = request.POST.get("password")
                authenticated_user = authenticate(request,username = username, password = password)

                if authenticated_user is None:
                    FailedLoginAttempt.objects.create(user=user)
                else:
                    FailedLoginAttempt.objects.filter(user=user).delete()
        
        return self.get_response(request)