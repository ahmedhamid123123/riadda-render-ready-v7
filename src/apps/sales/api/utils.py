from rest_framework.response import Response

def api_response(code, message, status_code=200, data=None):
    response = {
        'code': code,
        'message': message
    }

    if data is not None:
        response['data'] = data

    return Response(response, status=status_code)
