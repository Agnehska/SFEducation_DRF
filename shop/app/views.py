from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .authentication import BearerAuthentication
from .models import Product, Cart, Order
from .serializers import LoginSerializer, SignupSerializer, ProductSerializer, OrderSerializer, CartSerializer


# Create your views here.
@api_view(["POST"])
def login(request, *args, **kwargs):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        if not user:
            return Response({"error": {"code": 401, "message": "Login failed"}})
        token, created = Token.objects.get_or_create(user=user)
        return Response({'data': {'user_token': token.key}})
    return Response({"error": {"code": 422, "message": "Validation error", "errors": serializer.errors}})


@api_view(["POST"])
def signup(request, *args, **kwargs):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({'data': {'user_token': token.key}})
    return Response({"error": {"code": 422, "message": "Validation error", "errors": serializer.errors}})


@api_view(["GET"])
def logout(request):
    if request.user.is_active:
        request.user.auth_token.delete()
        return Response({"logout"})
    return Response({"error": {"code": 401, "message": "Login failed"}})


@api_view(["GET"])
def get_products(request):
    products = Product.objects.all()
    return Response({"data": ProductSerializer(products, many=True).data})


@api_view(["POST"])
def post_products(request):
    if request.user.is_staff:
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": {"id": serializer.data["id"], "message": "Product added"}})
        return Response({"error": {"code": 422, "message": "Validation error", "errors": serializer.errors}})
    return Response({"error": {"code": 403, "message": "Forbidden for you"}})


@api_view(["PATCH", "DELETE"])
def update_product(request, **kwargs):
    if request.user.is_staff:
        try:
            product = Product.objects.get(pk=kwargs.get("pk", None))
        except:
            return Response({"error": {"code": 404, "message": "Not found"}})
        if request.method == "PATCH":
            serializer = ProductSerializer(data=request.data, instance=product, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data": {"id": serializer.data["id"], "message": "Product added"}})
            return Response({"error": {"code": 422, "message": "Validation error", "errors": serializer.errors}})
        if request.method == "DELETE":
            product.delete()
            return Response({'data': {"message": "Product removed"}})
    return Response({"error": {"code": 403, "message": "Forbidden for you"}})


@api_view(["GET"])
def get_cart(request):
    if not request.user.is_staff:
        if request.user.is_active:
            cart, c = Cart.objects.get_or_create(user=request.user)
            data = []
            count = 0
            for product in cart.products.all():
                count += 1
                data.append({
                    "id": count,
                    "product_id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price
                })
            return Response({"data": data})
        return Response({"error": {"code": 401, "message": "Login failed"}})
    return Response({"error": {"code": 403, "message": "Forbidden for you"}})


@api_view(["POST", "DELETE"])
def update_cart(request, **kwargs):
    if not request.user.is_staff:
        if request.user.is_active:
            try:
                product = Product.objects.get(pk=kwargs["pk"])
            except:
                return Response({"error": {"code": 404, "message": "Not found"}})
            cart, c = Cart.objects.get_or_create(user=request.user)
            if request.method == 'POST':
                cart.products.add(product)
                cart.save()
                return Response({"data": {"message": "Product add to cart"}})
            if request.method == "DELETE":
                cart.products.remove(product)
                return Response({"data": {"message": "Item removed from cart"}})
        return Response({"error": {"code": 401, "message": "Login failed"}})
    return Response({"error": {"code": 403, "message": "Forbidden for you"}})


@api_view(["GET", "POST"])
def order(request):
    if not request.user.is_staff:
        if request.user.is_active:
            if request.method == "GET":
                order = Order.objects.filter(user=request.user)
                return Response({"data": OrderSerializer(order, many=True).data})
            if request.method == 'POST':
                try:
                    cart = Cart.objects.get(user=request.user)
                except:
                    return Response(
                        {"error": {
                            "code": 422,
                            "message": "Cart is empty"
                        }}
                    )
                order = Order()
                order.user = request.user
                full = 0
                for product in cart.products.all():
                    order.products.add(product)
                    order.save()
                    full += product.price
                order.order_price = full
                order.save()
                cart.delete()
                return Response(
                    {"data": {
                        "order_id": order.id,
                        "message": "Order is processed"
                    }}
                )
        return Response({"error": {"code": 401, "message": "Login failed"}})
    return Response({"error": {"code": 403, "message": "Forbidden for you"}})
