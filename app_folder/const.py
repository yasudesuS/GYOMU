from django.conf import settings


def constant_text(request):
    return {
        'COMPANY_NAME': settings.COMPANY_NAME,
        'EMP_ID': 20,
    }