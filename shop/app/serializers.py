from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.views import obtain_auth_token

from .models import User, Product, Cart, Order


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(

    )
    password = serializers.CharField(

    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

        attrs['user'] = user
        return attrs


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["email", "fio", "password"]

    def save(self, **kwargs):
        user = User(email=self.validated_data["email"], fio=self.validated_data["fio"])
        user.set_password(self.validated_data["password"])
        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["id", "products", "user"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "products", "order_price"]