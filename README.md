# Public Notes

Source for [publicnotes.org](https://publicnotes.org).

- `site/` is the built static site that Vercel serves (project root directory: `site`, no build step).
- `generator/` holds the Python build scripts and the note sources.

Rebuild after editing notes in `generator/src`:

```
cd generator
python3 og.py src assets/logo.png      # only if titles changed (share cards)
python3 build.py src ../site --email ds@publicnotes.org
```

Then commit and push; Vercel deploys `main` automatically.

## Study library and learning pages

The companion Word collection is imported into `generator/library-notes.json`.
This source preserves 300 UPSC foundation notes and 100 current affairs explainers.
It deliberately omits the reference document's image material. Collection dates
are separated from event dates; the explainers are background reading, not a
monthly magazine or live news service.

Rebuild the library, homepage, classroom pages, shared navigation and sitemap:

```
python generator/upgrade_website.py
```

To re-import a revised companion document, use
`python generator/upgrade_website.py --reference PATH_TO_DOCX`.
The original `build.py` also invokes this upgrade after a full rebuild.
The website remains static. Email requests explicitly open the reader's own
email application; no signup backend, payment collection or analytics service
is implied.
