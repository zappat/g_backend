from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import uuid
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils import timezone
import os

from core.models import User
from user.serializers import UserSerializer
from user.serializers import MerchantProfileSerializer, RenterProfileSerializer
from user.models import MerchantProfile, RenterProfile

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None) or getattr(settings, 'STRIPE_API_KEY', None)

class MerchantProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve Update merchant profile object"""
    
    permission_classes = (permissions.AllowAny, )  # Temporarily allow all access
    serializer_class = MerchantProfileSerializer
    
    def get_object(self):
        if not self.request.user.is_authenticated:
            # Return a default merchant profile or raise an error
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must be authenticated to access merchant profile")
        
        # Try to get the merchant profile, create one if it doesn't exist
        try:
            return self.request.user.merchantprofile
        except MerchantProfile.DoesNotExist:
            # Create a new merchant profile for the user
            return MerchantProfile.objects.create(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        try:
            print(f"📝 Merchant profile update - Received data: {request.data}")
            print(f"📝 Request user: {request.user}")
            print(f"📝 Request authenticated: {request.user.is_authenticated}")
            serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
            if not serializer.is_valid():
                print(f"❌ Merchant profile validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            print(f"✅ Merchant profile data is valid")
            return super().update(request, *args, **kwargs)
        except Exception as e:
            print(f"❌ Merchant profile update error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MerchantProfileDetailAPIView(generics.RetrieveAPIView):
    """Get merchant profile by user ID"""
    
    permission_classes = (permissions.AllowAny,)
    serializer_class = MerchantProfileSerializer
    queryset = MerchantProfile.objects.all()

class MerchantProfileDeleteAPIView(generics.DestroyAPIView):
    """Delete merchant profile object"""
    
    permission_classes = (permissions.AllowAny, )  # Temporarily allow all access
    serializer_class = MerchantProfileSerializer
    queryset = MerchantProfile.objects.all()

class MerchantsByMerchantIdsAPIView(APIView):
    """Return users for a list of merchant profile IDs.

    Expects JSON body: { "merchant_ids": ["<uuid>", "<uuid>"] }
    """

    permission_classes = (permissions.AllowAny,)

    def _fetch(self, merchant_ids_raw):
        merchant_ids = merchant_ids_raw

        if not isinstance(merchant_ids, list) or len(merchant_ids) == 0:
            return Response(
                {"detail": "merchant_ids must be a non-empty list"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_uuids = []
        valid_ints = []
        for id_value in merchant_ids:
            # Try UUID first
            try:
                valid_uuids.append(uuid.UUID(str(id_value)))
                continue
            except (ValueError, TypeError):
                pass
            # Try integer (user id)
            try:
                valid_ints.append(int(str(id_value)))
            except (ValueError, TypeError):
                continue

        if len(valid_uuids) == 0 and len(valid_ints) == 0:
            return Response(
                {"detail": "No valid merchant IDs provided (accepts UUID merchant profile IDs or integer user IDs)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profiles_qs = (
            MerchantProfile
            .objects
            .filter(Q(id__in=valid_uuids) | Q(user_id__in=valid_ints))
        )
        serialized = MerchantProfileSerializer(profiles_qs, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        return self._fetch(request.data.get("merchant_ids"))

    def get(self, request, *args, **kwargs):
        # Support query param style: /user/by-merchant-ids/?merchant_ids=a,b,c
        merchant_ids_param = request.query_params.get("merchant_ids")
        if merchant_ids_param is None:
            return Response(
                {"detail": "merchant_ids query param is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        merchant_ids = [part.strip() for part in merchant_ids_param.split(",") if part.strip()]
        return self._fetch(merchant_ids)


@csrf_exempt
def create_checkout_session(request):
    if request.method not in ['GET', 'POST']:
        return HttpResponseNotAllowed(['GET', 'POST'])

    # Prefer query params; allow POST form/body as fallback; then settings; then hardcoded dev defaults
    price_id = 'price_1RvqO9CioQm1zjDsOAJNr3C3'
    success_url = 'https://www.google.com'
    cancel_url = 'https://www.google.com'
    quantity = 1
    
    # Ensure API key is set (prefer STRIPE_API_KEY if available)
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    print("stripe.api_key",stripe.api_key)

    # Prepare metadata and client reference
    metadata = {}
    client_ref = None
    if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
        client_ref = str(request.user.id)
        try:
            metadata['merchant_profile_id'] = str(request.user.merchantprofile.id)
        except Exception:
            pass

    try:
        session = stripe.checkout.Session.create(
            mode='subscription',
            line_items=[{
                'price': price_id,
                'quantity': quantity,
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=client_ref,
            metadata=metadata or None,
        )
        return JsonResponse({'id': session.id, 'url': session.url})
    except Exception as e:
        return JsonResponse({'detail': str(e)}, status=400)


class StripeWebhookView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

        if not endpoint_secret:
            return Response({'detail': 'Webhook secret not configured'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=endpoint_secret,
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        event_type = event.get('type')
        data = event.get('data', {}).get('object', {})

        try:
            if event_type == 'checkout.session.completed':
                # Identify merchant profile
                metadata = data.get('metadata') or {}
                merchant_profile_id = metadata.get('merchant_profile_id')
                profile = None
                if merchant_profile_id:
                    try:
                        profile = MerchantProfile.objects.get(id=merchant_profile_id)
                    except MerchantProfile.DoesNotExist:
                        profile = None
                if profile is None:
                    client_ref = data.get('client_reference_id')
                    if client_ref:
                        try:
                            user = User.objects.get(id=client_ref)
                            profile = getattr(user, 'merchantprofile', None)
                        except User.DoesNotExist:
                            profile = None

                if profile is not None:
                    # Determine expiration
                    expires_at = None
                    subscription_id = data.get('subscription')
                    if subscription_id:
                        try:
                            sub = stripe.Subscription.retrieve(subscription_id)
                            cpe = sub.get('current_period_end')
                            if cpe:
                                expires_at = timezone.datetime.fromtimestamp(int(cpe), tz=timezone.utc)
                        except Exception:
                            pass
                    if not expires_at:
                        cpe = data.get('current_period_end')
                        if cpe:
                            try:
                                expires_at = timezone.datetime.fromtimestamp(int(cpe), tz=timezone.utc)
                            except Exception:
                                expires_at = None

                    profile.is_pro = True
                    profile.pro_expires_at = expires_at
                    profile.save()

            elif event_type in ('customer.subscription.updated', 'customer.subscription.created'):
                metadata = data.get('metadata') or {}
                merchant_profile_id = metadata.get('merchant_profile_id')
                if merchant_profile_id:
                    try:
                        profile = MerchantProfile.objects.get(id=merchant_profile_id)
                        cpe = data.get('current_period_end')
                        expires_at = None
                        if cpe:
                            try:
                                expires_at = timezone.datetime.fromtimestamp(int(cpe), tz=timezone.utc)
                            except Exception:
                                expires_at = None
                        profile.is_pro = True
                        profile.pro_expires_at = expires_at
                        profile.save()
                    except MerchantProfile.DoesNotExist:
                        pass

            elif event_type in ('customer.subscription.deleted', 'invoice.payment_failed'):
                metadata = data.get('metadata') or {}
                merchant_profile_id = metadata.get('merchant_profile_id')
                if merchant_profile_id:
                    try:
                        profile = MerchantProfile.objects.get(id=merchant_profile_id)
                        profile.is_pro = False
                        profile.pro_expires_at = timezone.now()
                        profile.save()
                    except MerchantProfile.DoesNotExist:
                        pass
        except Exception:
            # swallow internal errors to avoid webhook retries storm
            pass

        return Response({'received': True}, status=status.HTTP_200_OK)

class RenterProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve Update renter profile object"""
    
    permission_classes = (permissions.AllowAny, )  # Temporarily allow all access
    serializer_class = RenterProfileSerializer
    
    def get_object(self):
        if not self.request.user.is_authenticated:
            # Return a default renter profile or raise an error
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must be authenticated to access renter profile")
        
        # Try to get the renter profile, create one if it doesn't exist
        try:
            return self.request.user.renterprofile
        except RenterProfile.DoesNotExist:
            # Create a new renter profile for the user
            return RenterProfile.objects.create(user=self.request.user)
    

class RenterProfileDetailAPIView(generics.RetrieveAPIView):
    """Get renter profile by user ID"""
    
    permission_classes = (permissions.AllowAny,)
    serializer_class = RenterProfileSerializer
    queryset = RenterProfile.objects.all()
    
    def get_object(self):
        """Get renter profile by user ID from URL parameter"""
        user_id = self.kwargs.get('pk')
        if not user_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("User ID is required")
        
        try:
            # Get the user first
            from core.models import User
            user = User.objects.get(id=user_id)
            
            # Try to get the renter profile, create one if it doesn't exist
            try:
                return user.renterprofile
            except RenterProfile.DoesNotExist:
                # Create a new renter profile for the user
                return RenterProfile.objects.create(user=user)
                
        except User.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("User not found")


class RenterProfileDeleteAPIView(generics.DestroyAPIView):
    """Delete renter profile object"""
    
    permission_classes = (permissions.AllowAny, )  # Temporarily allow all access
    serializer_class = RenterProfileSerializer
    queryset = RenterProfile.objects.all()
