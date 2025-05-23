from rest_framework import generics, permissions

from gear_hub.models import Review
from gear_hub.serializers import ReviewSerializer
from core.permission import IsAdminOrRenter


class ReviewListApiView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ReviewSerializer

    def get_queryset(self):
        gear_item = self.kwargs['gear_item']
        return Review.objects.filter(gear_item=gear_item)


class ReviewCreateApiView(generics.CreateAPIView):
    permission_classes = (IsAdminOrRenter, )
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    

class ReviewDeleteApiView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAdminUser, )
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()