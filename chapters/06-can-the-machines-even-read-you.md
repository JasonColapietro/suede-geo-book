# PART II: THE FIX

# Chapter 6: Can the Machines Even Read You?

> "Fetch the file and read the rules. Do not assume."
> Source: Suede AI SEO methodology

Every repair in this book depends on one precondition: when an AI crawler shows up at your site, it gets your content. Not a block, not a challenge page, not an empty JavaScript shell. Your actual words.

This is the least glamorous chapter in the book and the first one for a reason. Access problems are severe precisely because they can be invisible from inside the company. The site looks perfect in every browser anyone has opened while a search crawler may receive a block, challenge page, or empty shell, with no internal alert recording the refusal. Silent failure, exactly as Chapter 3 promised.

The good news: access is the most mechanically checkable thing in this entire field. No judgment calls, no engine mystique. A file either allows a bot or it does not. A URL either returns your content or it does not. You can verify every piece of this yourself in under fifteen minutes.

## Know the bots by name

The bot names matter, but they do not all do the same job. A search crawler can make a page eligible for retrieval. A user-request fetcher may retrieve a page after someone asks for it. A model-development crawler concerns training, not live search inclusion. Keep those lanes separate:

- **OAI-SearchBot** is OpenAI's search crawler. **ChatGPT-User** fetches pages in response to a user's request. **GPTBot** is the separate model-development crawler. OpenAI documents those roles independently in its [publisher guidance](https://help.openai.com/en/articles/9237897).
- **PerplexityBot** builds Perplexity's search index. **Perplexity-User** supports user-requested fetches. Perplexity says PerplexityBot is not used to build foundation models in its [crawler documentation](https://docs.perplexity.ai/docs/resources/perplexity-crawlers).
- **Claude-SearchBot** supports search discovery, **Claude-User** supports user-requested retrieval, and **ClaudeBot** is Anthropic's model-development crawler. Anthropic separates the three in its [crawler guidance](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler).
- **Googlebot** feeds Google Search, including the pages that can appear in AI Overviews and AI Mode. **Google-Extended** is a separate product token for Gemini Apps and Vertex AI training and grounding. Google says Google-Extended does not affect inclusion or ranking in Google Search in its [AI features guidance](https://developers.google.com/search/docs/appearance/ai-features).
- **Bingbot** feeds Microsoft Copilot through the Bing index.
- **CCBot** collects for Common Crawl, a dataset used in model development and other research.

These are different doors. It is entirely possible to be discoverable in Google Search, absent from another search index, open to a user-request fetch, and closed to model development, without anyone in the company having made those choices deliberately. Access can make retrieval possible. It cannot guarantee a citation, a brand mention, a recommendation, or a factually accurate answer.

## Check one: robots.txt, actually read

Your robots.txt file, at yourdomain.com/robots.txt, is the posted policy for crawlers. My methodology note for this check is four words long: fetch the file and read the rules, do not assume. Assumption is how these blocks survive for years.

Open the file in a browser. Reading it takes one rule: a Disallow line belongs to the User-agent line above it, and a `User-agent: *` block applies to every bot that does not have its own block. So `User-agent: *` followed by `Disallow: /` blocks everyone from everything, including all the bots above. A specific block like `User-agent: GPTBot / Disallow: /` shuts out exactly one platform.

What you are looking for: any of the named bots blocked, or a blanket rule doing it wholesale. If the file fails to load at all, that is a finding too. Treat access as unverified, not as open, and find out why.

One nuance before you reach for the delete key. Blocking AI bots is a legitimate business decision for some companies; publishers with licensing concerns, for instance, block model-development crawlers on purpose. The problem is not blocking. The problem is blocking by accident, inherited from an old contractor's template. A deliberate policy can allow search crawlers such as OAI-SearchBot, Claude-SearchBot, PerplexityBot, Googlebot, and Bingbot while blocking model-development crawlers such as GPTBot, ClaudeBot, and CCBot. Google-Extended belongs in that policy conversation too, but it is not the control for Google Search or Google's AI search features. Whatever you choose, document it per bot and verify the result.

## Check two: what the bot actually receives

Robots.txt is the policy. Now verify the practice, because plenty of sites say "allowed" in the policy and serve something else in fact.

The common offenders sit in front of your site: CDN bot protection, web application firewalls, DDoS shields. These layers score visitors, and crawlers that are not Googlebot often score badly, receiving a challenge page, an error status, or a refused connection. Nobody configured this on purpose. It shipped as a default setting labeled something reassuring like "bot fight mode."

The other offender is your own rendering. Text-first crawlers do best with content present in the initial HTML response. If your pages arrive as a nearly empty shell that assembles itself in the visitor's browser via JavaScript, a crawler that does not execute your scripts fetches the shell. Quick test: view your key page's source, the raw source, not the browser's rendered inspector, and search for a sentence of your actual copy. If your pricing, your product description, and your answers are not in that raw response, the machines may not be reading the page you think you published.

If you want the fifteen minutes done for you, this is exactly what the free check at **optimize.suedeai.ai** does: ten seconds, no email, and it tells you whether AI crawlers can even read your site. It is the front door of the same diagnosis this chapter just taught you to run by hand.

## Check three: can the machines find everything

Access is not only the front door. A crawler that can read you still needs to discover the pages that matter. Confirm you have a sitemap listed in robots.txt, confirm your important pages are in it, and confirm those pages do not carry stray noindex tags or point their canonical URLs somewhere unintended. These are classic SEO hygiene items, and Chapter 4 explained why they now pay double: the same crawl that feeds your rankings feeds the answer layer built on top of them.

## The finding, written down

Run all three checks and write down the result per bot: allowed, blocked, or unverified, with the reason. That per-bot line is the professional standard for this diagnosis, and "unverified" is an honest and common answer; a fetch that fails tells you less than a rule that says Disallow, and the two should never be reported as the same thing.

If everything came back open, congratulations: your problem is upstream, in structure and evidence, which is where the next chapters live. If you found blocks, fix them before touching anything else in this book. Every hour spent on content while the crawlers bounce off your firewall is an hour spent decorating a room the machines cannot enter.

## Check this yourself right now

Open **yourdomain.com/robots.txt** and read it against the bot list above, block by block. Then run **optimize.suedeai.ai** and compare its result with your reading. Write the per-bot verdict into your notes: allowed, blocked, or unverified. That one line of notes is the foundation the next four chapters build on.
