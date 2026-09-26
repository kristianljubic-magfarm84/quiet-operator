# Setup — @daily.quietoperator

One-time. Budget 90 minutes. Do it in order; each step produces something the next step needs.

At the end you will have: a repo that posts one card to Instagram every morning at 05:07 UTC, by itself, for the next 120 days, at zero cost.

---

## Before you start

You should already have:

- [x] The Instagram account `@daily.quietoperator`, set to **Business**
- [ ] A Facebook Page linked to it
- [ ] A GitHub account

If the Page isn't linked yet, do that first — nothing below works without it.

**Linking the Page (the step people get wrong):**
Do it from **Instagram**, not from Facebook. Instagram app → Settings → *Sharing and linking* (older versions: *Accounts Centre* → *Connected experiences*) → Facebook → choose your Page.

Verify it took: open Meta Business Suite at business.facebook.com. If your Instagram account shows up there next to the Page, the link is real. If it doesn't, the API won't see it either, no matter what the Instagram app says.

---

## 1. Create the repo

github.com → New repository.

- Name: `quiet-operator`
- **Public** (this matters — the card images are served from the repo, and private repos don't serve raw files publicly)
- Don't add a README

Upload everything from the folder I sent you. Easiest path: on the empty repo page, click *uploading an existing file*, then drag the whole contents in. Keep the folder structure — `.github/workflows/`, `docs/cards/`, `fonts/` all need to land as-is.

> GitHub's web uploader sometimes hides dotfolders. If `.github` doesn't appear after upload, create it manually: *Add file → Create new file*, type `.github/workflows/publish.yml` as the filename (the slashes create the folders), and paste the contents in.

## 2. Point the repo at itself

Edit `config.json` in GitHub, replace `REPLACE_ME` with your GitHub username, commit.

```json
"github_user": "your-username",
```

This is how Instagram finds the images. Get it wrong and every post fails at the container step.

## 3. Create the Meta app

developers.facebook.com → My Apps → Create App.

- Use case: **Other** → Type: **Business**
- Name: anything (`quiet-operator-poster`). Users never see this.
- No Business Portfolio needed for now

On the app dashboard: *Add Product* → **Instagram** → Set up.

Leave the app in **Development mode**. You are posting only to your own account, so you do **not** need App Review. This is the single biggest shortcut in the whole build — most guides send you into a weeks-long review process you don't need.

## 4. Collect your app credentials

App dashboard → *App settings* → *Basic*.

Copy down:
- **App ID**
- **App Secret** (click Show)

## 5. Get your Instagram user ID and a long-lived token

Go to the **Graph API Explorer**: developers.facebook.com/tools/explorer

**a.** Top right: select your app from the dropdown.

**b.** Click *Generate Access Token*. Grant these permissions:

```
instagram_basic
instagram_content_publish
pages_show_list
pages_read_engagement
business_management
```

**c.** Find your Page ID — run this query in the Explorer:

```
me/accounts
```

Copy the `id` of your Page.

**d.** Find your Instagram user ID:

```
<PAGE_ID>?fields=instagram_business_account
```

The number that comes back is your **IG_USER_ID**. Write it down.

> Empty result here means the Page↔Instagram link didn't take. Go back to the top of this file.

**e.** Get the Page access token:

```
me/accounts?fields=access_token
```

Copy the `access_token` for your Page. **This is the token that does the posting** — not the user token from step b.

**f.** Make it permanent. Go to the **Access Token Debugger**: developers.facebook.com/tools/debug/accesstoken

Paste the Page token → Debug → click **Extend Access Token** at the bottom. Copy the extended token.

A Page token derived from an extended user token has no expiry date. It can still be killed by a Facebook password change or a Meta permissions review — that's what the weekly health check is for.

## 6. Add the secrets

Repo → Settings → *Secrets and variables* → *Actions* → *New repository secret*.

| Name | Value |
|---|---|
| `IG_ACCESS_TOKEN` | the extended Page token from 5f |
| `IG_USER_ID` | the number from 5d |
| `IG_APP_ID` | from step 4 |
| `IG_APP_SECRET` | from step 4 |

Secrets are write-only. You can overwrite them but never read them back, so keep the token somewhere safe too.

**If you ever need to regenerate the token** (the health check will email you): repeat step 5 from **b**, then overwrite `IG_ACCESS_TOKEN`. Nothing else changes.

## 7. Test before you let it run

Repo → *Actions* → *Daily post* → *Run workflow* → tick **dry_run** → Run.

It should log the line, the image URL, and `DRY_RUN — nothing posted`. **Open that image URL in a browser.** If it doesn't load, Instagram can't load it either — check step 2.

Then run it again with dry_run **unticked**. Check your Instagram. Card 001 should be there.

That's it. It now runs every morning on its own.

---

## Your profile

**Name:** The Quiet Operator
**Handle:** @daily.quietoperator

**Bio:**

```
Daily notes on decisions, restraint and the long game.
Original lines. Written and posted by AI.
One a day, 05:07 UTC.
```

The AI disclosure is deliberate. Meta is tightening on undisclosed synthetic content, and an account that states it plainly is both safer and, in this niche, more interesting than one pretending otherwise.

**Profile picture:** `docs/cards/profile.png` if I've included one, otherwise a flat `#0E0F11` square. Resist the urge to add a logo. The feed is the identity.

---

## Running it

| What | When | Your involvement |
|---|---|---|
| Daily post | 05:07 UTC | none |
| Token health check | Mondays | none unless it fails |
| Queue top-up | before card 120 | ask me |

**Failures email you.** GitHub notifies on failed Actions runs by default — that's the alerting, and it's why every script exits non-zero rather than failing quietly.

**The queue does not loop.** At card 120 it stops and fails rather than reposting. That's intentional: a silent repeat is worse than a visible stop. You'll get roughly four months of runway, and the monthly top-up should keep you well ahead of it.

**To change a line:** edit `quotes.json`, delete the matching PNG from `docs/cards/`, run `build_cards.py` (or ask me), commit. Already-posted cards can't be changed — Instagram holds its own copy.

## Cost

€0. Public repos get unlimited Actions minutes; this uses about 90 seconds a day. The Meta API is free at this volume — the publishing limit is 50 posts per rolling 24 hours and you're using one.
