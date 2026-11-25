# news-image-20261124-v2

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/muhammadaldy198/news-image-20261124-v2/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/muhammadaldy198/news-image-20261124-v2/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Tuesday 24 November 2026: the world in one day — 38 dated stories, 10 regions, all from Tuesday 24 November 2026. Three heroes (Shanghai party chief under probe, US jury finds Huawei guilty, Russian raid kills 9 across Ukraine), 10 minis with red banners inside the art, 25 also-on briefs, a numbered world map, a UTC timeline, an IN NUMBERS strip, and a DATE CHECK of what was left out as another day's news. Every story carries a verification label (CONFIRMED / OFFICIAL / REPORTED / CLAIM / ONGOING) and a named source.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` copies the pre-rendered `entry.png` (1024×1024, deterministic) to the output directory. To re-render the broadsheet from the story data: `python3 draw.py stories.json entry.png` (Pillow + Noto fonts, render-time only), then `python3 verify.py`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=3p0axm2p&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
