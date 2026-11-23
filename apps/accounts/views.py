from rest_framework import status
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

from apps.accounts.serializers import RegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers import LoginSerializer

from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def register(request):
    serializer = RegistrationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        return Response(
            {
                'message': 'Account created successfully.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'role': user.role.role_name,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    SessionAuthentication().enforce_csrf(request._request)

    serializer = LoginSerializer(
        data=request.data,
        context={'request': request},
    )

    if serializer.is_valid():
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(
            {
                'message': 'Login successful.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'email': user.email,
                    'role': user.role.role_name,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key='access_token',
            value=str(access),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=15 * 60,
        )

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=7 * 24 * 60 * 60,
        )

        return response

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )

@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_token(request):
    return Response({
        'csrfToken': get_token(request),
    })

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def refresh_token(request):
    SessionAuthentication().enforce_csrf(request._request)
    refresh = request.COOKIES.get('refresh_token')

    if not refresh:
        return Response(
            {'detail': 'Refresh token not found.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    serializer = TokenRefreshSerializer(
        data={'refresh': refresh}
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED,
        )

    response = Response(
        {'message': 'Token refreshed successfully.'},
        status=status.HTTP_200_OK,
    )

    response.set_cookie(
        key='access_token',
        value=serializer.validated_data['access'],
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=15 * 60,
    )

    if 'refresh' in serializer.validated_data:
        response.set_cookie(
            key='refresh_token',
            value=serializer.validated_data['refresh'],
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=7 * 24 * 60 * 60,
        )

    return response
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def logout(request):
    SessionAuthentication().enforce_csrf(request._request)

    refresh = request.COOKIES.get('refresh_token')

    if refresh:
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            pass

    response = Response(
        {'message': 'Logout successful.'},
        status=status.HTTP_200_OK,
    )

    response.delete_cookie('access_token', samesite='Lax')
    response.delete_cookie('refresh_token', samesite='Lax')

    return response