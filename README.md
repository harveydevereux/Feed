### Sources of interesting, often positive news.

This CLI program is intented to function on an automated schedule (e.g. Cron). New articles are posted to a Discord webhook if supplied on the CLI.

## There are two main modes

### Invoke to update you on various sources as they appear,

```shell
# Call regularly, e.g. with Cron each hour.
feed update --webhook https://discord.com/api/webhooks/YOUR/WEBHOOK/URL
```

Currently these include the BBC's "In Pictures" and "Future" series, Nature's News page, and the Guardian's "Week In Wildlife" and "Photos of the Day".

Note URLs stored in `data/` will not be sent multiple times.

---
#### Invoke to update you on the top stories of a subreddit in the last 24 hours,

```shell
feed update-subreddit SUBREDDIT --webhook https://discord.com/api/webhooks/YOUR/WEBHOOK/URL
```

This will obtain the top entries (Top/Today) for the subreddit `SUBREDDIT`. Note URLs stored in `data/` will not be sent multiple times.

---

## Under the hood

By default Feed will store its data in YAML files within `data/` relative to the invocation of Feed.

Specific sources will store their data in named YAML files, for example for BBC's "In Pictures"

```yaml
# data/bbcinpcitures.yml
'2026-02-27':
- preview_image_url: https://...
  title: Playful seal pups shot clinches underwater photo prize
  url: https://www.bbc.co.uk/news/...
'2026-03-01':
- preview_image_url: https://...
  title: '''Wonderful'' war photographer Paul Conroy dies'
  url: https://www.bbc.co.uk/news/...
'2026-03-03':
- preview_image_url: https://...
  title: Peregrine falcon exhibition to land at cathedral
  url: https://www.bbc.co.uk/news/...
...
```

This is to ensure messages are not sent twice. These data are not deleted automatically.