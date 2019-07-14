import requests


# Similar to IslandoraClient, reflecting some KU local "v1ku" custom endpoints

class IslandoraClientKU(requests.Session):

    def __init__(self, rest_url=None, user=None, token=None):
        super(__class__, self).__init__()
        self.url_base = rest_url
        if self.url_base[-1] != "/":
            self.url_base = rest_url + "/"
        if user and token:
            self.auth = (user, token)

    def request(self, method, url, **kwargs):
        modified_url = self.url_base + 'v1ku/' + url
        return super(__class__, self).request(method, modified_url,
                                              **kwargs)

    def regen(self, pid, dsid='DC'):
        if not pid:
            raise Exception("Missing PID")
        url = "regen/{}/{}".format(pid, dsid)
        response = self.put(url)
        response.raise_for_status()
        return response
