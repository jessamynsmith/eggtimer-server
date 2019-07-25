class AddAuthTokenMiddleware(object):
    """
        Adds auth_token cookie to response
    """
    def process_response(self, request, response):
        if hasattr(request, 'user') and request.user and request.user.is_authenticated():
            auth_token = request.user.auth_token
            if auth_token:
                response.set_cookie('auth_token', auth_token)
        return response
