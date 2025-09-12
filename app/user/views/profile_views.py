from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
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


class MerchantProfileByEmailView(generics.RetrieveAPIView):
    """Get merchant profile by user's email"""
    permission_classes = (permissions.AllowAny,)
    serializer_class = MerchantProfileSerializer

    def get_object(self):
        email = self.kwargs.get('email')
        try:
            # Find the user by email
            user = User.objects.get(email=email)
            # Get or create their merchant profile
            profile, created = MerchantProfile.objects.get_or_create(user=user)
            return profile
        except User.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(f"No user found with email: {email}")


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

class GetAllMerchantsAPIView(generics.ListAPIView):
    """Get all merchants"""
    
    permission_classes = (permissions.AllowAny,)
    serializer_class = MerchantProfileSerializer
    queryset = MerchantProfile.objects.all()

@csrf_exempt
def create_checkout_session(request):
    if request.method not in ['GET', 'POST']:
        return HttpResponseNotAllowed(['GET', 'POST'])

    # Prefer query params; allow POST form/body as fallback; then settings; then hardcoded dev defaults
    price_id = 'price_1S3PPRCWogwHqyflQbGpL0Z9'
    success_url = 'http://16.171.200.215/subscription?session_id={CHECKOUT_SESSION_ID}'
    cancel_url = 'http://16.171.200.215/subscription'
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
        return JsonResponse({
            'id': session.id, 
            'url': session.url,
            'success_url': success_url,  # This will be the template with {CHECKOUT_SESSION_ID}
            'session_id': session.id,
            'sessionId': session.id  # Add camelCase version for frontend compatibility
        })
    except Exception as e:
        return JsonResponse({'detail': str(e)}, status=400)


class StripeWebhookView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        """Handle GET requests with session_id parameter from frontend"""
        session_id = request.GET.get('session_id')
        if not session_id:
            return Response({'error': 'session_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the checkout session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            # Process the session as if it was a webhook
            return self._process_checkout_session(session, request)
            
        except stripe.error.InvalidRequestError:
            return Response({'error': 'Invalid session_id'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        # Check if this is a frontend call (has session_id in body) or Stripe webhook (has signature)
        if sig_header:
            # This is a Stripe webhook - validate signature
            endpoint_secret = getattr(settings, 'STRIPE_SECRET_KEY', None)
            if not endpoint_secret:
                return Response({'detail': 'Stripe secret key not configured'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                event = stripe.Webhook.construct_event(
                    payload=payload,
                    sig_header=sig_header,
                    secret=endpoint_secret,
                )
            except ValueError as e:
                return Response({'detail': f'Invalid payload: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.SignatureVerificationError as e:
                return Response({'detail': f'Invalid signature: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'detail': f'Webhook error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Process Stripe webhook event
            event_type = event.get('type')
            print("event_type", event_type)
            data = event.get('data', {}).get('object', {})
            
            try:
                if event_type == 'checkout.session.completed':
                    # Use the shared method to process checkout session
                    return self._process_checkout_session(data, request)
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
        else:
            # This is a frontend call - check for session_id in body
            try:
                import json
                data = json.loads(payload)
                session_id = data.get('session_id')
                if not session_id:
                    return Response({'error': 'session_id is required in request body'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Retrieve the checkout session from Stripe
                session = stripe.checkout.Session.retrieve(session_id)
                
                # Process the session as if it was a webhook
                return self._process_checkout_session(session, request)
                
            except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON in request body'}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.InvalidRequestError:
                return Response({'error': 'Invalid session_id'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _process_checkout_session(self, session_data, request=None):
        """Process checkout session data for both webhook and direct calls"""
        try:
            # Identify merchant profile
            metadata = session_data.get('metadata') or {}
            merchant_profile_id = metadata.get('merchant_profile_id')
            profile = None
            
            if merchant_profile_id:
                try:
                    profile = MerchantProfile.objects.get(id=merchant_profile_id)
                except MerchantProfile.DoesNotExist:
                    profile = None
            
            if profile is None:
                client_ref = session_data.get('client_reference_id')
                if client_ref:
                    try:
                        user = User.objects.get(id=client_ref)
                        profile = getattr(user, 'merchantprofile', None)
                    except User.DoesNotExist:
                        profile = None
            
            # If still no profile found and we have an authenticated request, use the authenticated user
            if profile is None and request and hasattr(request, 'user') and request.user.is_authenticated:
                try:
                    profile = getattr(request.user, 'merchantprofile', None)
                except Exception:
                    profile = None

            if profile is not None:
                # Determine expiration
                expires_at = None
                subscription_id = session_data.get('subscription')
                if subscription_id:
                    try:
                        sub = stripe.Subscription.retrieve(subscription_id)
                        cpe = sub.get('current_period_end')
                        if cpe:
                            expires_at = timezone.datetime.fromtimestamp(int(cpe), tz=timezone.utc)
                    except Exception:
                        pass
                if not expires_at:
                    cpe = session_data.get('current_period_end')
                    if cpe:
                        try:
                            expires_at = timezone.datetime.fromtimestamp(int(cpe), tz=timezone.utc)
                        except Exception:
                            expires_at = None

                # Set pro_expires_at based on your requirements
                from datetime import timedelta
                current_time = timezone.now()
                
                if not profile.pro_expires_at or profile.pro_expires_at == "":
                    # If pro_expires_at is null or empty, set to 30 days from current time
                    profile.pro_expires_at = current_time + timedelta(days=30)
                else:
                    # If pro_expires_at already has a value, set to 30 days from expires_at date
                    if expires_at:
                        profile.pro_expires_at = expires_at + timedelta(days=30)
                    else:
                        # If no expires_at from Stripe, use current pro_expires_at + 30 days
                        profile.pro_expires_at = profile.pro_expires_at + timedelta(days=30)

                profile.is_pro = True
                profile.save()
                
                return Response({
                    'success': True,
                    'message': 'Subscription activated successfully',
                    'merchant_profile_id': str(profile.id),
                    'is_pro': profile.is_pro,
                    'pro_expires_at': profile.pro_expires_at
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Merchant profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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


class RenterProfileByEmailView(generics.RetrieveAPIView):
    """Get renter profile by user's email"""
    permission_classes = (permissions.AllowAny,)
    serializer_class = RenterProfileSerializer

    def get_object(self):
        email = self.kwargs.get('email')
        try:
            # Find the user by email
            user = User.objects.get(email=email)
            # Get or create their renter profile
            profile, created = RenterProfile.objects.get_or_create(user=user)
            return profile
        except User.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(f"No user found with email: {email}")

class GetAllRentersAPIView(generics.ListAPIView):
    """Get all renters"""

    permission_classes = (permissions.AllowAny,)
    serializer_class = RenterProfileSerializer
    queryset = RenterProfile.objects.all()


class IncreaseMerchantViewsAPIView(APIView):
    """
    Increase views count for a merchant profile
    URL: /api/user/merchant-profile/increase-views/{merchant_id}/
    Method: POST
    """
    permission_classes = [permissions.AllowAny]  # Allow anyone to view merchant profiles

    def post(self, request, merchant_id):
        try:
            # Get the merchant profile by ID
            merchant_profile = get_object_or_404(MerchantProfile, id=merchant_id)
            
            # Increment the views count
            merchant_profile.views += 1
            merchant_profile.save()
            
            return Response({
                'success': True,
                'message': 'Views count increased successfully',
                'merchant_id': merchant_profile.id,
                'current_views': merchant_profile.views,
                'merchant_name': merchant_profile.display_name
            }, status=status.HTTP_200_OK)
            
        except MerchantProfile.DoesNotExist:
            return Response({
                'error': 'Merchant profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            import traceback
            print(f"DEBUG: Error in IncreaseMerchantViewsAPIView: {str(e)}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
