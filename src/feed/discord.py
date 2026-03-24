from requests import post, exceptions

from feed.source import Entry

def send(webhook: str, source: Entry, name: str):

    data = {}

    data["embeds"] = [{"url": source.url, "title": name+" | "+source.title}]

    if source.preview_image_url != "":
        data["embeds"][0]["image"] = {"url": source.preview_image_url}

    result = post(webhook, json = data)

    try:
        result.raise_for_status()
    except exceptions.HTTPError as err:
        print(err)

def send_summary(webhook: str, entries: list[Entry], name: str):

    data = {}

    data["content"] = f"## Top {name} articles of the last 24 hours."

    data["embeds"] = []
    for source in entries:
        embed = {"url": source.url, "title": source.title}
        if source.preview_image_url != "":
            embed["image"] = {"url": source.preview_image_url}
        data["embeds"].append(embed)

    result = post(webhook, json = data)

    try:
        result.raise_for_status()
    except exceptions.HTTPError as err:
        print(err)