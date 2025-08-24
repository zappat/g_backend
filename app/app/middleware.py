import logging
import traceback
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class ErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.error(f"Error processing request: {request.path}")
        logger.error(f"Exception: {str(exception)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JsonResponse({
            'error': str(exception),
            'path': request.path,
        }, status=500)