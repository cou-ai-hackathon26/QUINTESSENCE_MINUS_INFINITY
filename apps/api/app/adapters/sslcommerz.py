"""Explicit unavailable boundary until real session/validation transport is implemented and verified.

The previous generated checkout URL and client-payload validation were not a payment integration.
Never return those synthetic outputs as provider success, even when credentials are present.
Official contract: https://developer.sslcommerz.com/doc/v4/
"""

class PaymentProviderUnavailable(RuntimeError):
    pass

class SSLCommerzAdapter:
    def __init__(self,*args,**kwargs):
        self.is_live=False

    def init_payment_session(self,*args,**kwargs):
        raise PaymentProviderUnavailable('Real gateway session creation is not implemented/verified. No checkout was created.')

    def validate_callback(self,*args,**kwargs):
        raise PaymentProviderUnavailable('Real server-to-server validation is not implemented/verified. Client callback fields cannot establish payment.')
