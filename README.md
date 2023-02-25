## Description

Sync the links you have saved in Wallbag to Linkace. Links are synced with their tags and annotations.

Syncs only archived links. You can easily change this in the python script.


## Setup

You need a [Wallabag client ID and secret](https://doc.wallabag.org/en/developer/api/oauth.html#creating-a-new-api-client), and a [Linkace API key](https://api-docs.linkace.org/).
Then, edit `conf`:

```
LINKACE_URL=<Full URL to your Linkace installation (e.g., https://example.org/linkace/public/)>
LINKACE_API_KEY=<Linkace API key>
WALLABAG_URL=<Full URL to your wallabag installation (e.g., https://example.org/wallabag/web/)>
WALLABAG_CLIENT_ID=<Wallabag API client ID>
WALLABAG_CLIENT_SECRET=<Wallabag API client secret>
WALLABAG_USERNAME=<Wallabag account username>
WALLABAG_PASSWORD=<Wallabag account password>
```

After, just run `python wallabag.py`.


## Timer
You can use the following service/timer files. Replace where appropriate.

wallace.service
```
[Unit]
Description=Wallace, Wallbag to Linkace sync
Documentation=https://github.com/jrcruz/wallace

[Service]
Type=oneshot
WorkingDirectory=<PATH TO WALLACE REPO>
ExecStart=/usr/bin/python <PATH TO WALLACE REPO>/wallace.py
```

wallace.timer
```
[Unit]
Description=Sync Wallabag with Linkace every 6h

[Timer]
OnCalendar=00/6:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Put `wallace.service` and `wallace.timer` in `/etc/systemd/system/`. Then run:
```
systemctl daemon-reload
systemctl enable wallace.timer
```
