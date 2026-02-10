from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from apps.core.api.messages import MESSAGES

from apps.core.api.utils import api_response


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if not user:
            return api_response(
                'INVALID_CREDENTIALS',
                MESSAGES['INVALID_CREDENTIALS'],
                status.HTTP_401_UNAUTHORIZED
            )

        login(request, user)

        return api_response(
            'LOGIN_SUCCESS',
            MESSAGES['LOGIN_SUCCESS'],
            status.HTTP_200_OK,
            data={
                'username': user.username,
                'role': user.role
            }
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return api_response(
            'LOGOUT_SUCCESS',
            MESSAGES['LOGOUT_SUCCESS']
        )
