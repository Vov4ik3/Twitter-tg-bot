# Twitter/X → Telegram group bot

DM it a twitter.com/x.com link, it downloads the video (yt-dlp handles this
natively — no ssstwitter needed) and posts it straight into your group.

## 1. Get a bot token

Talk to [@BotFather](https://t.me/BotFather) in Telegram → `/newbot` → follow
the prompts → copy the token it gives you.

## 2. Add the bot to your meme group

Add it as a regular member (it doesn't need admin rights just to post
messages, unless you've locked the group down further).

## 3. Get your group's chat ID

Easiest way: add [@RawDataBot](https://t.me/RawDataBot) or
[@userinfobot](https://t.me/userinfobot) to the group temporarily, send any
message, it'll reply with the chat ID (a negative number like
`-1001234567890`). Remove it afterward if you like.

## 4. Get your own user ID

DM [@userinfobot](https://t.me/userinfobot) — it replies with your numeric
Telegram user ID. This is what keeps random people from DMing your bot and
getting it to post into your group.

## 5. Install & configure

```bash
cd twitter-tg-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env   # fill in BOT_TOKEN, TARGET_CHAT_ID, ALLOWED_USER_IDS
```

## 6. Run it

```bash
python bot.py
```

Send it a twitter/x link from your account — it should reply "Downloading...",
then post the video into your group and edit its status message to "Posted ✅".

## 7. (Optional) Keep it running as a systemd service

```bash
mkdir -p ~/.config/systemd/user
cp twitter-tg-bot.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now twitter-tg-bot.service

# check it's alive / see logs
systemctl --user status twitter-tg-bot.service
journalctl --user -u twitter-tg-bot.service -f
```

`WorkingDirectory` and `ExecStart` in the service file assume you put the
project at `~/twitter-tg-bot` with the venv inside it — adjust the paths if
you put it somewhere else.

## Notes / limitations

- **50MB upload cap.** That's a hard Telegram Bot API limit, not something
  in the code. Almost all tweet videos are fine; if one isn't, the bot tells
  you instead of hanging. (The only way around this is running your own
  local Bot API server, which raises the limit to 2GB — overkill unless you
  regularly hit long videos.)
- **"GIFs" on Twitter are actually mp4s** under the hood, so they're handled
  by the same code path as videos — no special-casing needed.
- If a tweet has multiple videos, only the first one downloaded gets
  posted. Easy to extend to a loop if you want all of them.
- If Twitter changes something and downloads start failing, `pip install -U
  yt-dlp` first — that's almost always the fix, since extractor updates
  ship constantly.
