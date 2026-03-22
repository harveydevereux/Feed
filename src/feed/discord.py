from requests import post, exceptions

from feed.source import Entry

def send(webhook: str, source: Entry):

    data = {}

    data["embeds"] = [{"url": source.url, "title": source.title}]

    if source.preview_image_url != "":
        data["embeds"][0]["image"] = {"url": source.preview_image_url}

    result = post(webhook, json = data)

    try:
        result.raise_for_status()
    except exceptions.HTTPError as err:
        print(err)