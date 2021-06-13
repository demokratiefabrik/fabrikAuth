import os


class FabrikMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # PREVENT TO STORE SESSION ID COOKIES
        # (This is a stateless app)
        MODE = os.environ.get('MODE')
        if response.status_code == 302 and MODE != 'DJANGO':
            if '?code' in response.url:
                response.delete_cookie('sessionid')
                pass
        return response
