from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Activity, Workout
from .serializers import ActivitySerializer, WorkoutSerializer
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.core.mail import send_mail
import random
import logging

logger = logging.getLogger(__name__)

class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

class WorkoutViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)


class SendLoginCodeView(APIView):
    def post(self, request):
        logger.info("SendLoginCodeView POST called with data: %s", request.data)
        try:
            email = request.data.get('email')
            user, created = User.objects.get_or_create(email=email, defaults={'username': email})
            code = random.randint(100000, 999999)
            user.profile.login_code = code
            user.profile.save()

            # Uncomment to send email
            '''
            send_mail(
                'Your Login Code',
                f'Your login code is {code}',
                'leifnhammar@gmail.com',
                [email],
                fail_silently=False,
            )
            '''
            return Response({'message': 'Login code sent', 'code': code}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error in SendLoginCodeView: %s", str(e))
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyLoginCodeView(APIView):
    def post(self, request):
        logger.info("VerifyLoginCodeView POST called with data: %s", request.data)
        try:
            email = request.data.get('email')
            code = request.data.get('code')
            user = User.objects.get(email=email)
            if user.profile.login_code == code:
                user.profile.login_code = ''
                user.profile.save()
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error in VerifyLoginCodeView: %s", str(e))
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)