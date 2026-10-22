"""User-approved game research sources; validate redirects before following them."""
from urllib.parse import urlsplit, parse_qs
from urllib.request import HTTPRedirectHandler, build_opener

def require_allowed(url):
    p = urlsplit(url)
    host = p.hostname
    allowed = p.scheme == 'https' and not p.username and not p.password and p.port in (None, 443) and (
        host == 'morrisrrrrrrr-svg.github.io' or
        (host == 'bobogameguides.com' and p.path.startswith('/maplestory-classic/')) or
        (host == 'forum.gamer.com.tw' and p.path in ('/B.php', '/C.php') and parse_qs(p.query).get('bsn') == ['85994']) or
        (host == 'maplestoryclassic.beanfun.com') or
        (host == 'maplestoryclassic-event.beanfun.com' and (p.path.startswith('/api/EventAd/') or p.path.startswith('/EventAD/')))
    )
    if not allowed:
        raise ValueError('來源未獲授權，停止讀取：' + url)
    return url

class ApprovedRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        require_allowed(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def approved_open(request, **kwargs):
    require_allowed(request if isinstance(request, str) else request.full_url)
    return build_opener(ApprovedRedirects()).open(request, **kwargs)
