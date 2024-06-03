from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "Server is running"})

def custom_404(request, exception):
    return JsonResponse({'error': 'Not found'}, status=404)

def custom_500(request):
    return JsonResponse({'error': 'Server error'}, status=500)
