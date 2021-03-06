import os
import io
import falcon
import requests

ALLOWED_STYLES = ("flat-square", "plastic")


def get_badge(name: str, style: str = None):
    if style and style in ALLOWED_STYLES:
        image_path = os.path.join(os.getcwd(), f"img/{name}-{style}.svg")
    else:
        image_path = os.path.join(os.getcwd(), f"img/{name}.svg")

    stream = io.open(image_path, "rb")
    content_length = os.path.getsize(image_path)

    return stream, content_length


class HerokuBadge:
    def on_get(self, req, resp):
        if not req.params:
            resp.content_type = "text/html"
            resp.status = falcon.HTTP_200
            with io.open("index.html", "rb") as f:
                resp.body = f.read()
                return

        app = req.params.get("app")
        if not app:
            resp.status = falcon.HTTP_501
            return
        style = req.params.get("style")

        url = f"https://{app}.herokuapp.com/"
        r = requests.get(url)

        resp.cache_control = ("max-age=0", "no-cache", "no-store", "must-revalidate")
        resp.append_header("pragma", "no-cache")
        resp.append_header("expires", 0)
        resp.content_type = "image/svg+xml"

        if r.status_code == 200:
            resp.stream, resp.content_length = get_badge(name="deployed", style=style)
        elif r.status_code == 404:
            resp.stream, resp.content_length = get_badge(name="not-found", style=style)
        else:
            resp.stream, resp.content_length = get_badge(name="failed", style=style)


application = falcon.API()
application.add_route("/", HerokuBadge())
