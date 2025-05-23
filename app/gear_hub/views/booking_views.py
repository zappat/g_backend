from django.utils.timezone import now
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from gear_hub.models import Booking, Cart, GearItemRent
from gear_hub.serializers import BookingSerializer, CartSerializer
from core.permission import IsAdminOrRenter
from core.pagination import StandardResultsSetPagination
from user.permissions import IsProvider

class ReservationListApiView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = CartSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.role == "renter":
            queryset = Cart.objects.filter(
                user=user,
            )
        elif user.role == "gear_provider":
            queryset = Cart.objects.filter(
                gear_item__provider=user
            )

        return  queryset.order_by("-created_at")
                    
class BookingListApiView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()
    pagination_class = StandardResultsSetPagination

class BookingCreateApiView(generics.CreateAPIView):
    permission_classes = (IsAdminOrRenter, )
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()
    
class BookingRetrieveUpdateApiView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAdminOrRenter, )
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()
    
class BookingDeleteApiView(generics.DestroyAPIView):    
    permission_classes = (IsAdminOrRenter, )
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()

class BookingStatusUpdateAPIView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated ,IsProvider)
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()

    def update(self, request, *args, **kwargs):
        user = request.user
        booking_id = self.kwargs.get("booking_id")
        booking = get_object_or_404(Booking, id=booking_id)

        gear_item_rent = get_object_or_404(GearItemRent, gear_item=booking.cart.gear_item)


        if gear_item_rent.qty_rented + booking.cart.quantity > gear_item_rent.qty:
            return Response({
                "quantity" : f"Out of stock . Can't book the item with {booking.cart.quantity} quantity"
            }) 
        gear_item_rent.qty_rented += booking.cart.quantity
        gear_item_rent.save()

        if not booking:
            return Response({
                "booking":"No booking found"
            }, status=status.HTTP_404_NOT_FOUND)

        if booking.cart.gear_item.provider != user:
            return Response({
                "user": "Not a valid provider"
            }, status=status.HTTP_403_FORBIDDEN)
        
        status = request.data.get("status")

        if status in dict(Booking.BookingStatus.choices).keys():    
            if status in ("accepted", "paid"):
                booking.cart.has_booked = True
                booking.cart.save()

        else:
            return Response({
                "status": "Not a valid choice for status"
            }, status=status.HTTP_400_BAD_REQUEST)

        booking.status = status
        print(booking.status)
        booking.save()

        return Response({
            "status": f"Successfully updated the status to {status}"
        })