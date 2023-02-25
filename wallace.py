import requests
import time
import sys


LAST_RUN_FILE_LOCATION = "./last-run"
CONFIG_FILE_LOCATION = "./conf"


def readEnvFile():
    env_conf = dict()
    with open(CONFIG_FILE_LOCATION) as env_file:
        for line in env_file:
            key, value = line.strip().split('=', maxsplit=1)
            if key == '':
                print("Config file not in format KEY=VALUE.")
                sys.exit(1)
            if value == '':
                print(f"Key '{key}' has no value in the config file.")
                sys.exit(1)
            env_conf[key] = value
    return env_conf


class Wallabag():
    def __init__(self, conf):
        url = conf["WALLABAG_URL"]
        self.url       = url if url.endswith('/') else url + '/'
        self.username  = conf["WALLABAG_USERNAME"]
        self.password  = conf["WALLABAG_PASSWORD"]
        self.client_id = conf["WALLABAG_CLIENT_ID"]
        self.client_secret = conf["WALLABAG_CLIENT_SECRET"]
        self.access_token = self._getToken()


    def _getToken(self):
        # https://doc.wallabag.org/en/developer/api/oauth.html
        r = requests.post(self.url + "oauth/v2/token",
                auth=(self.client_id, self.client_secret),
                data={
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password
                }
            )
        rjson = r.json()
        if r.status_code != requests.codes.ok:
            print(f"Error getting Wallabag access token:", rjson)
            sys.exit(1)
        return rjson["access_token"]


    def getUpdatesSince(self, time_since):
        # https://app.wallabag.it/api/doc
        r = requests.get(self.url + "api/entries.json",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={
                    "since": time_since,
                    "perPage": 10000,
                    "detail": "metadata",
                    # Change to 0 to sync all links from Wallabag, not just the archived ones.
                    "archive": 1
                }
            )
        rjson = r.json()
        if r.status_code != requests.codes.ok:
            print(f"Error getting Wallabag updates since {time_since}:", rjson)
            sys.exit(1)
        return rjson


class Linkace():
    def __init__(self, conf):
        url = conf["LINKACE_URL"]
        self.url       = url if url.endswith('/') else url + '/'
        self.api_token = conf["LINKACE_API_KEY"]


    def postUpdates(self, new_site, notes_for_site):
        # https://api-docs.linkace.org/#tag/links/operation/post-api-v1-links
        r = requests.post(self.url + "api/v1/links",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Accept": "application/json"
                },
                data=new_site
            )
        rjson = r.json()
        if r.status_code != requests.codes.ok:
            print(f"Could not add site '{new_site['url']}' to Linkace:", rjson)
            return 0

        for note in notes_for_site:
            rn = requests.post(self.url + "api/v1/notes",
                    headers={
                        "Authorization": f"Bearer {self.api_token}",
                        "Accept": "application/json"
                    },
                    data={"note": note, "link_id": rjson["id"]}
                )
            if rn.status_code != requests.codes.ok:
                print(f"Could not add note to site '{new_site['url']}' (not fatal; continuing):", rn.json())
        return 1


def main():
    env_conf = readEnvFile()

    wallabag_handler = Wallabag(env_conf)
    linkace_handler = Linkace(env_conf)

    current_time = int(time.time())
    with open(LAST_RUN_FILE_LOCATION) as last_run_file:
        last_run_time = int(last_run_file.read())

    updated_links = wallabag_handler.getUpdatesSince(last_run_time)

    count_succesful = 0
    for site in updated_links["_embedded"]["items"]:
        new_site = {
            "title": site["title"],
            "url": site["given_url"],
            "tags": ','.join(tag["label"] for tag in site["tags"])
        }
        notes_for_site = [f"Annotation: {annotation['text']} --- Quote: {annotation['quote']}"
                          for annotation in site["annotations"]]
        count_succesful += linkace_handler.postUpdates(new_site, notes_for_site)
        # Prevent "Too Many Attempts" from Linkace.
        time.sleep(0.1)


    with open(LAST_RUN_FILE_LOCATION, 'w') as last_run_file:
        last_run_file.write(f"{current_time}\n")

    print(f"Added {count_succesful} articles since {time.ctime(last_run_time)}")


if __name__ == "__main__":
    main()
    sys.exit(0)
