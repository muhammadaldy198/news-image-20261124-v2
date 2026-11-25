# Tuesday 24 November 2026 — The World in One Day

![competition](https://make.fun/badge/news-image-20261124.svg)
![rank](https://make.fun/badge/news-image-20261124/muhammadaldy198/news-image-20261124-v2/rank.svg)
![reward](https://make.fun/badge/news-image-20261124/muhammadaldy198/news-image-20261124-v2/reward.svg)

One broadsheet page summing up Tuesday 24 November 2026: **37 dated
stories, 7 regions, all from this one day**. Three heroes — Shanghai's
party chief under investigation, Huawei guilty on 10 of 12 counts, the
Russian raid on Zaporizhzhia — plus 10 minis, 24 more briefs, a UTC
timeline, a numbers strip, a pin map, and a date check listing what was
deliberately left out as other days' news.

Every story carries a verification label (CONFIRMED / OFFICIAL /
REPORTED / CLAIM / ONGOING) and a named source. Claims are labelled as
claims, never shown as fact.

## How it is made

`stories.json` holds the 37 stories. `draw.py` (Python 3.13, Pillow,
no network) renders them into `entry.png` (1024×1024, deterministic).
`verify.py` checks story counts, region sums, file gates, and banner
pixels. `main.ts` (Node 22, stdlib only) is copy-only: it copies the
committed `entry.png` to the output directory.

```sh
python3 draw.py    # regenerate entry.png
python3 verify.py  # checks; exits non-zero on failure
```

## Sources

Xinhua via AP, Reuters, CNN, AP, Kyiv Independent, Sanofi, NYSE,
MarketWatch, Arianespace, Spaceflight Now, Al Jazeera, CAF, JCS,
Yonhap, Iraqi government, and others — named on each item in the image.
