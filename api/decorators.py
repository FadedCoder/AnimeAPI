from django.http import JsonResponse
from .models import ApiToken


def api_login_required(func):
    def inner(request, *args, **kwargs):
        invalid_msg = {'status': 'FORBIDDEN', 'message': 'You are not allowed to access this site.'}
        invalid_resp = JsonResponse(invalid_msg, status=403)
        valid = False
        token = request.GET.get('token')
        if token:
            try:
                tobj = ApiToken.objects.get(token=token)
                if tobj.enabled:
                    valid = True
            except ApiToken.DoesNotExist:
                valid = False
        if valid:
            return func(request, *args, **kwargs)
        else:
            return invalid_resp
    return inner
