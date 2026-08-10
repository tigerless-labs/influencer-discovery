import json
import subprocess
import urllib.parse
import urllib.request

API = "https://sheets.googleapis.com/v4/spreadsheets"


class HeaderMismatch(Exception):
    pass


class SheetsUnavailable(Exception):
    pass


def access_token(account=None):
    cmd = ["gcloud", "auth", "print-access-token"]
    if account:
        cmd.append(f"--account={account}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SheetsUnavailable(proc.stderr.strip().splitlines()[0] if proc.stderr else "no token")
    return proc.stdout.strip()


class SheetsApi:
    def __init__(self, spreadsheet_id, token):
        self.spreadsheet_id = spreadsheet_id
        self.token = token

    def _call(self, path, method="GET", body=None, params=None):
        url = f"{API}/{self.spreadsheet_id}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Authorization", f"Bearer {self.token}")
        request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read())

    def tabs(self):
        meta = self._call("", params={"fields": "sheets.properties(sheetId,title)"})
        return {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta.get("sheets", [])}

    def read_headers(self, tab):
        rng = urllib.parse.quote(f"{tab}!1:1")
        values = self._call(f"/values/{rng}").get("values") or [[]]
        return values[0]

    def append(self, tab, values):
        rng = urllib.parse.quote(f"{tab}!A:A")
        self._call(
            f"/values/{rng}:append",
            method="POST",
            body={"values": values},
            params={"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"},
        )


class TargetSheet:
    def __init__(self, api, tab, mapping):
        self.api = api
        self.tab = tab
        self.mapping = mapping

    def _row_for(self, headers, candidate):
        email = candidate.email
        if not email:
            raise ValueError(f"{candidate.person_key} has no email; it must not reach the sheet")
        values = {
            self.mapping["display_name"]: candidate.display_name,
            self.mapping["channel"]: candidate.channel,
            self.mapping["profile_url"]: candidate.own_site or candidate.profile_url or "",
            self.mapping["contact"]: email,
            self.mapping["contact_kind"]: "email",
            self.mapping["status"]: "",
        }
        return [values.get(header, "") for header in headers]

    def append(self, candidates):
        if not candidates:
            return []
        headers = self.api.read_headers(self.tab)
        missing = [column for column in self.mapping.values() if column not in headers]
        if missing:
            raise HeaderMismatch(f"{self.tab} is missing columns: {missing}")
        rows = [self._row_for(headers, c) for c in candidates]
        self.api.append(self.tab, rows)
        return rows
