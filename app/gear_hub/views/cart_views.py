from django.shortcuts import get_object_or_404, get_list_or_404

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from gear_hub.models import Cart, GearItem
from gear_hub.serializers import CartSerializer


class CartCreateAPIView(generics.CreateAPIView):
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated, )

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

class CartRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated, )
    
    def get_object(self):
        user = self.request.user
        cart_id = self.kwargs["id"]
        return get_object_or_404(Cart, id=cart_id, user=user)

class CartUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated, )
    
    def get_object(self):
        user = self.request.user
        cart_id = self.kwargs["id"]
        return get_object_or_404(Cart, id=cart_id, user=user)


class CartListAPIView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        return get_list_or_404(Cart, user=user)

class CartDeleteAPIView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Cart.objects.all()

    def get_object(self):
        user = self.request.user
        cart_id = self.kwargs["id"]
        cart = get_object_or_404(Cart, id=cart_id, user=user)
        return cart

class CartDeleteAllAPIView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Cart.objects.all()

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        cart = Cart.objects.filter(user=user)

        if not cart.exists():
            return Response({
                "cart": "No details found"
                })
        
        cart.delete()
        return Response({
            "cart":"Cart item deleted successfully"
            })