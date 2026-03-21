from requests import post, exceptions

from feed.source import Source

def send(webhook: str, source: Source):

    data = {}

    data["embeds"] = [{"url": source.url, "title": source.title}]

    if source.preview_image_url != "":
        data["embeds"][0]["image"] = {"url": source.preview_image_url}

    print(data)
    result = post(webhook, json = data)

    try:
        result.raise_for_status()
    except exceptions.HTTPError as err:
        print(err)