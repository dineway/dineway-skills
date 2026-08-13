# Local AI Visibility Observation

Use `dineway-content-ai-visibility` with the user's own ChatGPT, Perplexity, Claude, Gemini,
Google AI Overviews, Grok, and DeepSeek access. Browser Use or the local client performs the query;
Dineway and Forgeway do not run these observations on the user's behalf.

## Prompt set

Choose a bounded, versioned prompt set that reflects actual demand:

- primary product, service, topic, and local-intent questions;
- comparison and alternative questions;
- “best” or recommendation questions when commercially relevant;
- buyer objections and decision questions;
- first-party visitor questions only after Dineway's native NLWeb/Chat aggregate exists.

Keep wording, locale, market context, and evaluation method stable when comparing observations.
Record prompt additions/removals as methodology changes so they are not mistaken for visibility
movement.

## Observation record

For every engine and prompt, preserve:

- engine, prompt ID/text hash, locale/market, observed time, and access mode;
- availability independently for that engine;
- whether the target brand, entity, and exact native page are mentioned;
- citation URLs, cited page titles, quoted context when permitted, and competitor entities/URLs;
- a bounded raw local artifact reference and normalized native observation ID;
- material interface or answer-mode differences that affect comparability.

Never convert an unavailable engine, blocked session, CAPTCHA, missing citation panel, or parse
failure into a negative citation observation. One engine's failure does not suppress the others.

## Diagnose gaps

Classify conclusions as one or more evidence-backed gaps:

- content gap: no suitable page answers the observed demand;
- authority gap: a relevant page exists but lacks corroborated depth or trustworthy sourcing;
- entity gap: the site or byline is not clearly connected to the topic/entity;
- citation gap: useful content exists but lacks direct answers, attribution, or extractable
  structure;
- availability gap: the engine could not be observed and no visibility conclusion is allowed.

Treat differences between engines as observations, not permanent platform rules. Compare cited
competitor pages for freshness, evidence, entity clarity, answer structure, and page fit, then link
every recommendation to the captured result and current page evidence.

## After a revision

Preserve the pre-change observation set, publish only through the native reviewed flow, and let the
active Monitor policy determine the next due check. Do not promise a fixed recrawl interval or
claim causality from one changed answer. Require repeated comparable observations before reporting
a durable gain or loss.
