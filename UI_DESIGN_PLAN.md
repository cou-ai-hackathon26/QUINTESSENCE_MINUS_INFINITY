# Shongoti UI direction and landing-page redesign

Research/design date: **23 November 2026, Asia/Dhaka**.
Status: **design proposal and isolated concept study, not a shipped UI or usability result**.

The user requested design research and ideas before implementation. Antigravity is concurrently changing this repository. This work does not edit application source, dependencies, its phase trackers or its in-progress backend work. Coordinate ownership before implementing shared files. Preserve `EXTENSION_PLAN.md`, exact financial rules and source-backed confidence/agent contracts.

Open [the interactive direction study](docs/design/shongoti-directions.html) to compare four proposed directions and a synthetic evidence interaction. It is an isolated HTML study, not the React application, a real model call or a finished responsive product. No award badge, customer adoption, live provider or benchmark claim is implied.

## 1. Recommendation

Choose **Modern Khata + Evidence Lab**: warm paper, deep green/ink typography, a small vivid lime signal, source-linked document visuals, precise agent/task motion and a calm readable working application. Give the public landing an expressive story; keep frequent merchant tasks fast and legible.

Signature interaction: **the evidence becomes the interface**. A bill, payment and return visibly connect to the question that blocks a supported decision. The visitor changes a supplier reply and sees the correct payable alternatives change. The UI communicates intelligence through what it finds, asks and updates.

This is a design judgment, not a proven conversion winner. Four meaningful directions and several implementation combinations were compared conceptually; no claim is made that every possible combination or real-user preference has been tested. Do not equate an impressive portfolio site with a usable financial product.

## 2. What the current source explains

Inspected `apps/web/src/pages/LandingPage.tsx`, `components/Navbar.tsx`, `src/index.css`, `src/i18n/translations.ts`, `apps/web/index.html` and the web manifest. Source baseline is the existing React 18/Vite application with Lucide; no Motion/GSAP dependency was present in the inspected web manifest. Concurrent changes may supersede this snapshot.

- Landing is predominantly a centered title/badge, two CTAs and three similarly styled bordered feature cards. It does not give the central evidence investigation a distinct visual form.
- Inline colors/sizes/radii compete with the rudimentary global tokens. There is little variation in section scale, layout or information rhythm.
- Copy includes implementation language such as floating-point precision and ledger internals where a new merchant needs understandable outcomes.
- Public Navbar defaults to a “Live” account badge even on the landing when no tenant state was established. Its status must derive from actual context, and public navigation needs a marketing variant.
- Bengali headings use a tight 1.2 line height; test actual conjuncts/ascenders before adopting it. Source inspection alone cannot prove clipping. Existing font loading requests Hind Siliguri and Inter, while an 800 heading weight exceeds the requested Hind weights up to 700.
- The current label “নকল তথ্য” can be replaced with truthful, clearer “ডেমো তথ্য.” Actual technical status must remain explicit in context.
- Public navigation exposes the working dashboard as an ordinary destination. Give landing navigation a clear demo/onboarding/login hierarchy and keep auth/tenant boundaries unchanged.

These are source-based findings, not observations of a rendered current page. The in-app browser failed during initialization in this session; no current-page screenshot, live animation playback or responsive visual QA was obtained.

## 3. Updated reference research: what to borrow

Use references for principles and examine their own source/asset rights before implementation; do not copy entire compositions, illustrations or brands. Award status does not establish accessibility, performance or suitability for Bangladesh.

| Primary reference, checked 23 November 2026 | Verified information | Application to Shongoti |
|---|---|---|
| [Oryzo AI — Awwwards](https://www.awwwards.com/sites/oryzo-ai) | SOTD 13 April 2026. Gallery lists WebGL sketches, 3D/2D transitions and a restrained dark/orange palette. | One distinctive interactive metaphor can communicate a product. Our metaphor is source evidence connecting to a decision, rather than reproducing its visual assets or assuming WebGL is required. |
| [Why Zero — Awwwards](https://www.awwwards.com/sites/why-zero) | SOTD 7 September 2026. Gallery lists narrative scroll and interactive UI elements. | Give scrolling a meaningful beginning/question/resolution and make one visitor action consequential. Do not import page-unlock friction into shop work. |
| [garcy.studio — CSS Design Awards](https://www.cssdesignawards.com/sites/garcy-studio/50409/) | WOTD 20 November 2026; description highlights playful interactions and analog textures. | Warm material cues and an authored illustration system can distinguish the brand. Keep analog texture subtle and out of data/text surfaces. |
| [Chande Bootcamp 2026 — CSS Design Awards](https://www.cssdesignawards.com/sites/chande-bootcamp-2026/50426/) | WOTD 19 November 2026; animated/scroll/WebGL tags and a locally grounded community theme. | Local identity can coexist with an international presentation. Develop Bangla-first typographic rhythm instead of adding generic flag decorations. |
| [CSSDA current homepage](https://www.cssdesignawards.com/) | Homepage labeled Ethiack awarded 23 November 2026, an agentic-AI service. Its older detail snapshot still showed nomination information. | Relevant current AI presentation reference; preserve the date/cache distinction. Do not assert an unseen animation or infer its technology beyond the published tags. |
| [Linear](https://linear.app/) | Current site presents teams and agents through product/issue/activity examples. | Make agent contributions readable inside actual work, with current task, outcome and review state. Borrow information clarity, not its full visual shell. |
| [Ramp](https://ramp.com/) | Current finance positioning explicitly features agents and workflow demos. | Explain an AI finance product through business jobs and visible examples. Its customer counts/automation promises are not Shongoti claims. |
| [2026 Webby Best Use of AI](https://winners.webbyawards.com/winners/websites-and-mobile-sites/features-design/best-use-of-ai) | Category states that AI use is judged; names Suno Studio and a Google Cloud generative experience among winners. | Visual polish and actual AI usefulness are separate proof obligations. This is not a hackathon scoring rubric. |

The official galleries provide descriptions, dates, palettes and element listings; full live visual/motion behavior was not observed in this session. Some overview/reference fetches timed out. All proposed Shongoti layouts below are original design recommendations, not claims about unobserved reference details.

## 4. Four design directions

### A — Evidence Lab

- Look: deep ink/green stage, warm document sheets, vivid lime only at the active evidence/task connection; asymmetrical hero.
- Main art: invoice and voice/receipt fragments connect to a concise source-backed decision, with visible agent roles.
- Type: confident Bangla display plus disciplined Latin labels and aligned money columns.
- Motion: paper layers align into a case; one edge highlights which source supports the current question.
- Strength: strongest immediate AI explanation and memorable product metaphor.
- Risk: a dark technical graph can overwhelm first-time merchants. Use a short sequence, clear labels and a light app surface.

### B — Modern Khata

- Look: chalk/paper, forest-green ink, small terracotta annotation, generous readable typography and an editorial rhythm.
- Main art: a recognisable bill/return/dues story, with a precise contemporary agent panel alongside it.
- Motion: receipt unfolds, a relevant line highlights, a disputed claim opens into a question.
- Strength: warm, Bangladesh-relevant, distinctive without relying on generic AI gradients.
- Risk: purely stationery-like visuals may hide technical capability. Keep agent collaboration, sources and the copilot interaction visible.

### C — Mission Control

- Look: restrained navy, cobalt, light surfaces, instrument-like case panels and a visible task/activity rail.
- Main art: one merchant decision with coordinated agents, source inspector and current readiness.
- Motion: task handoffs, changing dependencies and an inspectable answer/plan update.
- Strength: judges can quickly understand the system architecture and AI behavior.
- Risk: can resemble a generic SaaS dashboard or developer console. Remove unnecessary telemetry and label tasks in merchant language.

### D — Merchant World

- Look: original flat/isometric shop illustration, tangible shelves and receipts, small AI connection lines; cream with controlled orange/teal.
- Main art: a day in a shop moves through order, delivery, sale and credit follow-up.
- Motion: one focused shop moment reveals its real document/task, not endless decorative objects.
- Strength: memorable context and approachable storytelling.
- Risk: custom illustration/3D needs time and may compete with the financial task. Use as a later editorial chapter, not a blocking 3D introduction.

**Recommended combination:** B's materials/typography + A's evidence-to-decision hero + C's readable agent workspace. Use D only as a small original contextual illustration if the team has time. This is a coherent art direction; do not stack four complete visual styles on one page.

## 5. Landing-page blueprint

### 5.1 Public navigation

Brand mark and “সংগতি / Shongoti”; anchors for “কীভাবে কাজ করে”, “AI সহকারী”, “নিরাপত্তা”; language toggle, login and one primary demo CTA. Marketing Navbar does not show an unverified Live tenant badge. Phone layout uses an accessible menu and visible primary CTA, not seven tiny links.

### 5.2 First screen: make the task visible

Suggested headline:

> দোকানের হিসাব বুঝুক AI।  
> সিদ্ধান্ত থাকুক আপনার।

Supporting copy:

> বিল, ভয়েস আর supplier-এর কথাবার্তা মিলিয়ে দেখুন—কোথায় অমিল, কোন প্রশ্ন বাকি, এখন কী করবেন।

Primary CTA **“নিজে ডেমো চালান”**. Secondary **“আমার দোকান শুরু করি”** when onboarding is working. Microcopy: “ডেমোতে উদাহরণ তথ্য ব্যবহার করা হয়েছে।” Avoid unmeasured savings, customer logos/counts, invented awards or a live-model badge.

Layout: editorial headline on one side, a large custom evidence/case composition on the other. Immediate static content and CTA must render before animation, fonts or optional art. On phones place headline/CTA first, then a compact full-width interactive example.

Hero evidence example:

1. Supplier demand: BDT 25,000. Payment BDT 4,000 belongs to this bill. Accepted return BDT 3,000 is explicitly confirmed not included in this demand.
2. Missing fact: was the payment already deducted? Initially show **two supported possibilities: BDT 22,000 or BDT 18,000** and the blocking question.
3. Visitor selects “আগেই কাটা হয়েছে” → BDT 22,000; “এখনো কাটা হয়নি” → BDT 18,000; “জানা নেই” → both possibilities remain.
4. Source/payment/return cards remain inspectable. All numbers are labeled synthetic demo facts. A public deterministic illustration is not claimed as actual model inference.

This interaction teaches why interpretation is necessary. Do not animate straight from 25,000 to 18,000 without establishing inclusion facts. Do not count up through misleading intermediate financial values; replace the canonical value and briefly highlight its reason.

### 5.3 The source-to-question chapter

One three-step scene: “প্রমাণ দিন → অমিল বুঝুন → উত্তর দিয়ে সিদ্ধান্ত নিন”. Use invoice/photo/voice/document elements with small agent handoffs. Desktop may use a short sticky scene beside readable prose; phones show ordinary vertical steps and a next/replay control. No mandatory scroll unlock or horizontal scroll trap.

### 5.4 A real day, not a grid of every feature

Three editorial chapters, each with a different composition:

- **কেনার আগে:** compare supplier offer/pack/payment terms and cash effect.
- **মাল আসার পরে:** actual versus billed quantity, claim, accepted credit and later application.
- **দিনের শেষে:** current money, unresolved tasks and a user-started voice brief.

Bring unmet requests, return deadlines and customer orders into the relevant chapter. Keep small remaining features in an expandable overview rather than twelve identical cards.

### 5.5 Visible AI team

Show the coordinator's business question and a few legible specialist roles: “বিল পড়ছে”, “শর্ত মিলাচ্ছে”, “মজুদ দেখছে”, “প্রমাণ যাচাই করছে”. In public illustrative mode these are labeled process steps. In the signed-in product, actual backend events drive queued/working/waiting/completed/failed/skipped states.

Click/tap a role to see its task, source and concise finding. Use an ordered accessible list below any visual graph. Do not draw a fictional live completion, fake latency, chain of thought, or always-active agent count.

### 5.6 Copilot and confidence demonstration

Prompt chips: “এই bill-এ কী প্রশ্ন বাকি?”, “কাল cash-এ কী দিতে হবে?”, “ফেরত দেওয়ার credit কোথায়?” A public example is clearly labeled and uses only its provided facts; real chat deep-links to the current actual feature when available.

Confidence is a source-support index under `EXTENSION_PLAN.md` D, with readable reasons and critical blockers. An unresolved inclusion question stays visibly limited, even if most fields are supported. Show “কেন এই score?” and the next action. A high score is not posting permission or an accuracy percentage.

### 5.7 Trust, FAQ and final invitation

Explain source review, unknown facts, merchant approval, private access and provider state in plain Bangla. Link technical details rather than making them the hero. FAQ covers evidence, voice, missing information, demo versus actual data and what the system can execute. Final CTA repeats one action, with a precise current capability statement.

Footer identifies the team/build accurately. Do not manufacture merchant quotes, coverage, security certifications or regulatory endorsement.

## 6. Design system for the recommended direction

Initial tokens, to validate in real components:

| Token | Value | Use |
|---|---|---|
| Paper | `#F7F5EE` | Main calm light canvas |
| Ink | `#12251F` | Headings, important figures, dark stage |
| Forest | `#0A6650` | Primary actions and selected controls |
| Lime | `#D9FF6E` | Small active AI/connection cue with dark text |
| Muted | `#586C62` | Supporting text on paper |
| Amber surface / text | `#FFF2D5` / `#805000` | Needs clarification, not success |
| Terracotta | `#B9573A` | Sparse annotation; check contrast for the actual pairing |

Calculated solid-color contrast ratios in this session: ink/paper **14.69**, muted/paper **5.15**, white/forest **6.93**, ink/lime **14.11**, amber text/surface **6.17**. These are pair calculations, not full-page accessibility certification. Recheck opacity, backgrounds, focus, hover/disabled states and final fonts. Never use white text on a pale lime CTA.

Spacing rhythm: 4/8/12/16/24/32/48/64/96px. Suggested radii: 10px controls, 16px content cards, 24px major scene; use pills for short status/category controls, not every block. Thin strong structural lines and restrained shadows establish depth. Texture belongs in illustrations/backgrounds, not behind financial tables or text.

Prefer one Bangla family for both headings/body: evaluate **Anek Bangla**, with existing **Hind Siliguri** as a low-change alternative, and retain Inter for Latin where useful. Compare actual rendered Bangla before choosing. Do not ship three font families just to express variety. Verify license/weights and self-host only needed subsets/assets. [Google's Anek Bangla source](https://github.com/google/fonts/tree/main/ofl/anekbangla).

Starting type targets, not final guarantees: mobile Bangla hero 34–42px with approximately 1.3–1.4 line height; desktop 60–76px with approximately 1.2–1.3 after glyph testing; body 17–18px with 1.65–1.8; UI labels 14–16px. Avoid arbitrary letter spacing, character-level reveal/scramble and `word-break: break-all` on Bangla. Animate a whole line/word wrapper while preserving shaped syllables. Recheck conjuncts such as “প্রমাণ”, “ব্যবসা”, “বিক্রয়”, “সমন্বয়”, “দায়িত্ব” and all vowel marks.

Use current language context; document/segment `lang` follows selected language. Bangla is left-to-right. Keep meaning natural rather than showing every label twice with parenthetical English. Clearly distinguish cash “নগদ টাকা” from the Nagad wallet. Format numbers consistently, preserve exact values and right-align amount columns; verify numeral font alignment rather than assuming every Bangla font supports tabular figures. Use ASCII for technical invoice/transaction references when needed.

## 7. Motion: select tools by responsibility

| Combination | Suitable output | Decision |
|---|---|---|
| CSS + Motion for React + SVG | Product transitions, confidence/source reveal, case activity, responsive interactive hero | **Default foundation** |
| Foundation + route-lazy GSAP/ScrollTrigger | One carefully sequenced evidence-story chapter | **Recommended enhancement after a storyboard proves its need** |
| Foundation + Rive OR dotLottie | A crafted stateful/illustrated asset with a real authoring workflow | Optional only when an actual owned asset improves the story |
| GSAP + React Three Fiber/WebGL scene | Experimental cinematic merchant-world introduction | Separate optional spike, not a primary dependency or first release gate |
| Lenis + many scroll effects + multiple canvas runtimes | More systems to synchronize and test | Do not adopt by default; native scrolling meets the proposed experience |

Official findings:

- [Motion for React](https://motion.dev/docs/react) is the current name of the library previously called Framer Motion. Verify installed React/package compatibility; do not install both packages or assume Framer's site builder is the same thing. Use [lazy features](https://motion.dev/docs/react-reduce-bundle-size) and [reduced-motion support](https://motion.dev/docs/react-accessibility).
- [GSAP React guidance](https://gsap.com/resources/React/) and [matchMedia](https://gsap.com/docs/v3/GSAP/gsap.matchMedia()/) support scoped setup/cleanup and responsive motion. Limit GSAP to the scene/timeline it owns. Motion and GSAP must not animate the same element/property simultaneously.
- [Rive's React runtime](https://rive.app/docs/runtimes/react/react) supports real `.riv` state machines/data binding. It does not author a quality animation by adding a package. Check actual renderer/asset cost and provide a static equivalent.
- [dotLottie](https://docs.lottiefiles.com/en) is an authored animation delivery option, not a reason to add a stock robot mascot.
- [React Flow](https://reactflow.dev/) fits larger interactive node workspaces. A fixed five-role hero can use HTML/SVG; add a graph library only when actual navigation/layout needs justify it.
- [React Three Fiber](https://r3f.docs.pmnd.rs/getting-started/introduction) explicitly pairs major versions with React; current docs say v8 for React 18 and v9 for React 19. Do not upgrade the application's React to obtain decorative 3D or blindly install an incompatible latest renderer.
- [Lenis](https://lenis.dev/) offers scroll smoothing; this plan selects native scroll first. Marketing claims about accessibility do not replace our own input/keyboard tests.

No motion package was installed in this research session. Exact versions/licensing/entry points must be rechecked against current official docs when implementation begins.

## 8. Motion score: proposed durations and semantics

These are initial design timings to prototype, not measured performance results:

| Moment | Motion | Initial target and fallback |
|---|---|---|
| Hero entry | Composition settles; headline/CTA already readable | 500–800ms once; static layout with reduced motion |
| Evidence inspected | Relevant source line/edge highlights | 180–260ms; instant highlight remains meaningful |
| Agent handoff | Highlight edge and task state from an event | 220–360ms; static state/list fallback |
| Clarification | Question panel opens, focus moves predictably | 180–240ms; user-controlled, no shaking |
| Supported reply | Replace outcome and explain changed fact | 180–280ms crossfade; canonical amount changes immediately |
| Confidence | Bar settles to the actual computed index | 200–320ms; exact numeric label is immediate, never a random/counting accuracy display |
| Copilot | Cited answer/section appears when available | Short grouped reveal, not artificial token slowness |
| Voice | Waveform represents actual input/playback when active | User initiated; static illustrative waveform explicitly labeled |
| Landing scroll chapter | One short document-to-case narrative | Desktop enhancement only; normal steps on mobile |

Prefer transform/opacity for decorative movement; avoid layout thrash/large animated blur, full-screen shader/video backgrounds and continuous high-power loops. Pause offscreen animation. An initial flourish ends and remains inspectable; Replay is explicit. No modal intro, cursor replacement, magnetic money buttons, bouncing amount rows, confetti for debt or autoplay speech.

Respect OS reduced motion plus an in-page animation control. Auto motion presented beside content for more than five seconds needs pause/stop/hide where applicable; [W3C Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html). W3C's [Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) is AAA guidance; use its user-control principle without falsely calling it a general AA requirement. Preserve educational meaning in static mode.

## 9. Make the app feel intelligent during real use

Carry the same brand into existing pages, with more restrained motion:

- Today: clear “এখন কী করা দরকার” list beside canonical money, not a grid dominated by decorative stats.
- Capture: visible attached bill/voice, source quality and proposed interpretation; an unsure field looks unsure.
- Case workspace: evidence on one side, task/answer on the other, real agent activity and merchant approval in one coherent space.
- Copilot: persistent small entry and context chip; large full conversation only when needed. Preserve source links, score reasons, drafts and failure states.
- Confidence: text/icon/bar and why/next-action; high score is not a green permission to pay.
- Notifications/brief: actionable rows, user-controlled audio, timestamp and pending-versus-actual distinctions.
- Tables/forms: generous targets, stable aligned amounts, minimal motion and immediate error correction.

Useful AI cues are task planning, source-grounded answers, contextual follow-ups and a visible change after new evidence. A glowing sphere alone cannot communicate these capabilities. Dark and light states must reflect a visual system rather than marking every normal action “AI.”

## 10. What tends to make a layout feel generic

This is an editorial checklist, not a scientific detector of AI authorship:

- Repeated identical cards, icon-in-circle rows and oversized round corners regardless of content.
- Vague hero copy, decorative purple/blue mist and a fake chat response unrelated to the product.
- Random impressive metrics, testimonial headshots, fake “trusted by” logos or unverified live status.
- Motion added after layout with no information hierarchy or user-controlled story.
- English-first spacing with Bengali squeezed into the same line boxes; machine-translated labels and excessive parentheticals.
- Stock robot/brain art, unowned illustrations or unrelated 3D objects replacing a meaningful product example.

The corrective approach: one original evidence illustration system; natural local copy; a clear grid/type hierarchy; differing section compositions; consistent actual states; deliberate line breaks; useful source interaction; a few strong motion moments; full mobile/error/unknown design. Human authorship is a design process, not a library setting.

## 11. Performance, accessibility and validation targets

Current [Core Web Vitals guidance](https://web.dev/articles/vitals) targets LCP ≤2.5s, INP ≤200ms, CLS ≤0.1 at the 75th percentile, segmented for device. These are goals, not achieved results. Use lab checks during development; do not call a Lighthouse run a field p75 result or use TBT as if it were measured INP.

Initial engineering budgets, to validate against the current Vite build: extra landing motion code ≤80KB gzip, fonts ≤200KB transferred for the chosen first view and first-view original art ≤250KB; no eager 3D/video dependency. These are project-selected budgets, not an industry standard. Measure actual route chunks and transfer requests; revise explicitly if real measurements justify it. First headline/CTA/content must work before JS animation and optional art.

Test 360/390/768/1440px, 200% zoom, keyboard/focus, reduced motion, animations paused, no custom font, slow network, source unavailable, demo versus signed-in, long Bangla labels and both language directions/number formats. Aim for 44px primary touch controls as a product choice; WCAG 2.2 AA's [target-size criterion](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) is 24px with documented exceptions/spacing, not universally 44px.

Run contrast checks on all actual states, automated accessibility checks plus manual focus/reading order and screen-reader status behavior. Static screenshot/source tests cannot prove interactive usability. Do not claim that merchants understand the UI until tested with merchants; team five-second checks are labeled internal proxies.

## 12. Coordinated UI implementation track

Do not renumber Phase 13–26 or let a visual polish task falsely complete a backend/AI gate. The IDs below are a **proposed UI subtrack**, to adopt with the owner of the active implementation. Work on dedicated components/branch or agree file ownership before editing shared Navbar, CSS, translations, routes or dependency lockfiles. Never stage the other agent's changes or run migrations to test a landing page.

| UI package | Tasks | Completion gate |
|---|---|---|
| UI-01 — design decision | Inspect actual rendered app when preview works; compare the four directions; choose tokens/type/copy and finite storyboards; agree ownership | Selected art direction and desktop/mobile/static/reduced-motion designs, not only a moodboard |
| UI-02 — foundations | Extract scoped tokens/public Navbar, typography and common controls; preserve app routes/language/auth behavior | Contrast, natural Bangla, correct public account status, keyboard/mobile navigation and no global-style regressions |
| UI-03 — landing first | Implement original hero and the source/question interaction, then narrative chapters/CTA/FAQ | Correct 22k/18k/unknown demo branches; synthetic label; source inspection; real responsive rendered journey |
| UI-04 — motion pass | Motion foundation; add one lazy GSAP sequence only if needed; finite replay, offscreen pause and static fallback | Actual device/browser timing/profile, accessible controls and no hidden content when motion/JS/font fails |
| UI-05 — product consistency | Apply design system to Today, evidence/case, agent workspace, copilot, notifications and forms as actual backend features become available | Every claim/state matches real backend; no artificial success, score or active-agent status; scenario/actual values remain distinct |
| UI-06 — validation and handoff | Real browser tests/screenshots, route/build regression, language/keyboard/reduced-motion/performance evidence | Measured results/limits saved, original financial tests unaffected, agreed UI work committed/pushed under its actual task/phase ownership |

Landing visual design and clearly labeled public demo can proceed independently of unavailable live models. Real agent/coplan/voice status cannot. Preserve `EXTENSION_PLAN.md` task prerequisites and actual phase checkpoint rules; do not create a fake completed phase just because a new landing renders.

## 13. Prompt for the implementing developer

```text
Improve Shongoti's UI on top of the existing React application using
UI_DESIGN_PLAN.md. Read AGENTS.md, the current extension contract/trackers and
the design proposal. Another agent may be changing backend/shared files:
inspect current Git changes and agree file ownership; preserve all their work.

Start with public landing design, not a backend rewrite. Use the recommended
Modern Khata + Evidence Lab direction and the isolated direction study as a
reference, not production code. Inspect actual current rendering before edits.
Build a strong Bangla-first type/grid/token system, public Navbar and original
evidence-to-question hero. Keep the 22k/18k/unknown synthetic demo financially
correct and explicitly labeled. Add motion only with defined informational
purpose, user controls, reduced-motion/static/mobile fallbacks and real cleanup.

Use Motion for ordinary React interactions; add one route-lazy GSAP scene only
when its storyboard warrants it. Verify installed/current APIs and compatibility.
Do not install every suggested library or upgrade React for decorative 3D.

Preserve actual ledger, approvals, language context and backend contracts.
Actual agent states, confidence and source answers must come from the existing
real services when implemented; public illustrations are clearly labeled.
Run real browser/keyboard/Bangla/responsive checks, relevant tests/build and
measure performance. Save observed evidence and exact remaining gaps. Do not
claim merchant validation, awards or live AI from a visual prototype. Commit
and push the agreed completed work under the canonical phase/checkpoint rules.
```

## 14. Research session limitations

Official pages/source were reviewed; a live-browser initialization failure prevented rendered visual QA. Public reference HTML/gallery entries do not prove their animation behavior on our target devices. The direction study is original HTML/CSS/JS with synthetic data; it has no real AI/provider call and has not been browser-verified here. Its structural/interaction calculations can be checked separately without claiming a usability/performance pass.

No application source, package/lockfile, database or active progress tracker is modified by this research deliverable. No real competition outcome, user adoption or conversion result is predicted.
