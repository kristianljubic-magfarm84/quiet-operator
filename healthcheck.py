#!/usr/bin/env python3
"""Weekly token health check.

The Page access token used for publishing is long-lived and in normal operation
does not expire. It CAN still be invalidated: a Facebook password change, a
permissions review, or Meta's periodic data-access expiry will kill it.

This job fails loudly (which emails you) while there is still time to fix it,
rather than letting you discover it from a silent gap in the feed.
"""
import json, os, sys, time, urllib.parse, urllib.request

API = os.environ.get("IG_API_VERSION", "v23.0")
TOKEN = os.environ.get("IG_ACCESS_TOKEN")
APP_ID = os.environ.get("IG_APP_ID")
APP_SECRET = os.environ.get("IG_APP_SECRET")
WARN_DAYS = 21


def get(url, params):
    with urllib.request.urlopen(url + "?" + urllib.parse.urlencode(params), timeout=30) as r:
        return json.loads(r.read())


def main():
    if not all([TOKEN, APP_ID, APP_SECRET]):
        print("ERROR: IG_ACCESS_TOKEN, IG_APP_ID, IG_APP_SECRET must all be set",
              file=sys.stderr)
        sys.exit(1)

    try:
        d = get(f"https://graph.facebook.com/{API}/debug_token",
                {"input_token": TOKEN,
                 "access_token": f"{APP_ID}|{APP_SECRET}"}).get("data", {})
    except Exception as e:
        print(f"ERROR: could not inspect token: {e}", file=sys.stderr)
        sys.exit(1)

    if not d.get("is_valid"):
        print(f"ERROR: token is INVALID — {d.get('error', {}).get('message', 'no reason given')}\n"
              f"Regenerate it and update the IG_ACCESS_TOKEN repository secret. "
              f"See SETUP.md step 6.", file=sys.stderr)
        sys.exit(1)

    exp = d.get("expires_at", 0)
    data_exp = d.get("data_access_expires_at", 0)

    if exp == 0:
        print("token: valid, no expiry set (long-lived Page token)")
    else:
        days = (exp - time.time()) / 86400
        print(f"token: valid, expires in {days:.0f} days")
        if days < WARN_DAYS:
            print(f"ERROR: token expires in {days:.0f} days — regenerate now. "
                  f"See SETUP.md step 6.", file=sys.stderr)
            sys.exit(1)

    if data_exp:
        days = (data_exp - time.time()) / 86400
        print(f"data access expires in {days:.0f} days")
        if days < WARN_DAYS:
            print(f"ERROR: data access expires in {days:.0f} days — "
                  f"re-authorise the app. See SETUP.md step 6.", file=sys.stderr)
            sys.exit(1)

    print("OK")


if __name__ == "__main__":
    main()
