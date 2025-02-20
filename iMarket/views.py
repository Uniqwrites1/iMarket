from django.http import JsonResponse

def home_view(request):
    return JsonResponse({"message": "Welcome to iMarket API"}, safe=False)
