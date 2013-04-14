


class Version(object):
    def process_request(self, request):
        try:
            request.webcab_version=open('/opt/ebs/web/ebscab/version', 'r').read()
            request.server_version=open('/opt/ebs/data/version', 'r').read()
        except Exception, e:
            # assumed that user is Anonimous
            request.webcab_version = 0
            request.server_version = 0
            pass

