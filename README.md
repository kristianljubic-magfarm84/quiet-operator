# quiet-operator

Autonomous daily-quote account for [@daily.quietoperator](https://instagram.com/daily.quietoperator).

Posts one pre-rendered card to Instagram every morning via GitHub Actions and the
Instagram Content Publishing API. No server, no cost, no manual step.

**Setup:** see [SETUP.md](SETUP.md).

| File | Role |
|---|---|
| `quotes.json` | the content bank — the only file worth editing by hand |
| `render.py` | draws one card |
| `build_cards.py` | pre-renders every card into `docs/cards/` |
| `publish.py` | posts the next card, advances `state.json` |
| `healthcheck.py` | weekly token check, fails loudly before the token dies |
| `config.json` | account name, handle, GitHub user |
| `state.json` | queue position — written by the workflow, don't edit |

All lines are original. Nothing here is quoted from another author.
