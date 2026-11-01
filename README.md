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
