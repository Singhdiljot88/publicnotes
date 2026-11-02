# UPSC 300 and Current Affairs 100: status and handover

Last updated: 2 November 2026.

## How the notes are built

1. **Drafts:** `generator/drafts/` holds the editable sources, one file per theme. `u01.txt`–`u30.txt` are UPSC 300 and `c01.txt`… are Current Affairs 100.
   - `# THEME n` starts a theme.
   - `## slug | Title` starts a note.
   - Paragraphs are separated by blank lines.
   - `- ` lines are the key takeaways (3 or more).
   - `W:` is "Why it matters for UPSC".
   - `Q:` is the practice or discussion question.
   - `S: Source name | URL` lists a source. Current Affairs notes must have at least one.
2. **Compose:** this turns the drafts into note HTML in `src/posts/<series>/`. Notes are numbered in order across the files. It also checks for missing parts and duplicate slugs.
   ```
   cd generator
   python3 compose.py upsc-300 drafts/u*.txt
   python3 compose.py current-affairs-100 drafts/c*.txt
   ```
3. **Build:** this writes the static site into `site/`.
   ```
   python3 build.py src ../site --email ds@publicnotes.org
   ```
   - The build warns while a series is short of its target count, but still builds.
   - Run `python3 og.py src assets/logo.png` only to regenerate share cards. It also rewrites the existing PNGs (they come out byte-different), so run `git checkout -- generator/assets` afterwards and keep only the new `upsc-300-*` and `current-affairs-100-*` cards.

**Theme list:** `generator/series_data.py`, in `UPSC_THEMES` and `CA_THEMES`. Each theme has its slug, name, icon, GS paper and intro.

**Pages generated:**
- `/upsc-300.html` and `/current-affairs-100.html` (hubs)
- `/<series>/themes/<slug>.html` (theme pages)
- the notes themselves
- RSS, sitemap and nav entries
- a "by paper" section on the UPSC map

## UPSC 300: 300 of 300 notes written

| Themes | Status |
|---|---|
| 1–16: Ancient India to International relations | Written and fact-checked. Recent facts were confirmed by web search, for example Sarnath as the 45th UNESCO site, the November 2025 labour codes, DPDP Rules and tribunals judgment, the presidential-reference opinion on assent timelines, the Attorney General's reappointment, Putin's December 2025 visit and the India–US 10-year defence framework. A few uncertain figures were softened, such as the Seventh Schedule entry counts and the Eastern Ghats' highest peak. |
| 25–27: Biodiversity, Climate & disasters, Internal security | Written and fact-checked by web search, including tiger, lion and dolphin counts, the 2035 NDC, COP30 and COP31, the Naxal statement of 30 March 2026, and Manipur President's rule. Uncertain counts are given as ranges or thresholds, for example Ramsar sites "crossed 100" and cheetahs "around fifty". |
| 28–30: Ethics (two themes) and General science | Written and checked. CPI 2025 rank and the SHANTI Act were confirmed by search. These standard figures went in from memory and are worth a spot-check: nuclear capacity of about 8.8 GW, PFBR core loading in 2024, ICMR diabetes at 10.1 crore, Genome India's 10,000 genomes, and UJALA's 36 crore bulbs. |
| 17–24: Economy, Banking, Public finance, Agriculture, Industry, Science & tech, Space & digital, Environment | Written. The writer was told to web-verify recent figures, but its session hit a usage limit before it could report what it checked. **Needs a fact-check pass** before publishing, on any recent number: GDP and CPI new series, repo rate, Budget 2026-27 figures, GST, NPAs, forex, renewable capacity, ISRO missions, semiconductors. |

## Current Affairs 100: 30 of 100 notes written

| Theme | Status |
|---|---|
| 1. Polity, Parliament & courts | **Done.** 10 notes, each with 2–4 sources. |
| 2. Elections & states | **Done.** 10 notes, each with 2–4 sources. |
| 3. Economy | **Missing.** Suggested topics: Budget 2026-27, Economic Survey, the new GDP and CPI series, RBI policy, the Income-tax Act 2025 in force from 1 April 2026, labour codes, VB-G RAM G from 1 July 2026, GST. |
| 4. Trade deals & tariffs | **Done.** 10 notes with sources. |
| 5. India & the world | **Missing.** Suggested topics: BRICS New Delhi summit and declaration (September 2026), the Iran war and the Strait of Hormuz, the neighbourhood, the Quad. |
| 6. Security & defence | **Missing.** Suggested topics: the Naxal end announcement, the NIA Pahalgam chargesheet, the new CDS and Army chief, missile tests, the Pakistan Navy collision of 15 September. |
| 7. Science, tech & space | **Missing.** |
| 8. Environment & disasters | **Missing.** |
| 9. Education, health & society | **Missing.** |
| 10. Sports, culture & people | **Missing.** |

Notes for whoever picks this up:
- **Theme order:** compose numbers notes in file order, so add `c03.txt` and `c05.txt`–`c10.txt` with matching `# THEME n` headers. Note numbers will then shift into theme order automatically.
- **Sources:** every current affairs fact should be checked against news or official sources and listed in `S:` lines. Leave out anything that can't be confirmed.
- **Wikipedia leads:** the "2026 in India" article was used only for leads, never as the sole source.

## Not done yet

- Deployment. Nothing has been merged to `main`.
- Images in the new notes. They use the theme share card instead.
- Quizzes for the new series.
