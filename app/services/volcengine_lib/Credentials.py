
class Credentials(object):
    def __init__(self, ak, sk, service, region, session_token=''):
        self.ak = ak
        self.sk = sk
        self.service = service
        self.region = region
        self.session_token = session_token
