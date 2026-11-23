from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import Role, User


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        trim_whitespace=False,
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = [
            'username',
            'full_name',
            'email',
            'phone_number',
            'password',
            'password_confirm',
        ]

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'An account with this email already exists.'
            )

        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        registered_role = Role.objects.get(
            role_name='Registered User'
        )

        user = User(
            **validated_data,
            role=registered_role,
        )

        user.set_password(password)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(
    write_only=True,
    trim_whitespace=False,
)

    def validate(self, attrs):
        login = attrs.get('login', '').strip()
        password = attrs.get('password')

        user = User.objects.filter(
            email__iexact=login
        ).first()

        if user is None:
            user = User.objects.filter(
                username=login
            ).first()

        if user is None:
            raise serializers.ValidationError(
                'Invalid login credentials.'
            )

        authenticated_user = authenticate(
            request=self.context.get('request'),
            username=user.username,
            password=password,
        )

        if authenticated_user is None:
            raise serializers.ValidationError(
                'Invalid login credentials.'
            )

        attrs['user'] = authenticated_user
        return attrs