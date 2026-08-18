# Chapter 7: The Six Engines and Who Each One Trusts

> "I audit how ChatGPT, Perplexity, and Gemini answer your category, then ship the fix the same day."
> — Jason Colapietro, @johnnysuede bio

Founders talk about "AI" as if it were one place, the way people once said "the internet." Operationally, there is no such place. There are six engines that matter for buying questions, each with its own way of finding sources, its own trust preferences, and its own failure modes. Treating them as one thing produces the classic mistake of optimizing hard for a behavior only one engine has.

This chapter is the field guide. It is deliberately practical: for each engine, how it selects, and what that means for your pages. Two honest caveats first. These systems change fast, so treat this as the map I would draw today, not scripture; the verification habit from Part I is what keeps your map current. And none of this is inside knowledge of proprietary ranking systems. It is the published guidance plus what the engines observably do when you run real category questions through them, which you now know how to do.

## Google AI Overviews and AI Mode

The synthesized answers inside Google Search are, by Google's own explicit statement, rooted in its core search ranking and quality systems. That single sentence sets your whole strategy for this engine: whatever earns you strong ordinary rankings is what earns you presence in the answers assembled above them.

Google is unusually direct about what not to do. No special markup or files are required. Do not chunk your content into artificial fragments for AI. Do not write separate content for machines; that path risks tripping spam policies about scaled content abuse. Write helpful, people-first content with normal headings and paragraphs, demonstrate real experience and expertise, and keep your indexability clean.

One Google behavior deserves special attention: query fan-out. Google's AI features do not answer only the literal question asked. They generate related queries under the hood, retrieve for each, and synthesize across the set. A user asking about fixing lawns triggers hidden retrievals about herbicides, prevention, chemical-free methods. The implication for you is significant: covering your topic comprehensively, the parent question and its natural sub-questions, makes you retrievable across the fan-out. Ten shallow pages targeting ten keywords are worth less than one page, or one connected cluster, that genuinely covers the territory.

## ChatGPT

ChatGPT answers from two layers: its training data, the accumulated public web as of a cutoff, and live web search when it browses. The two layers fail differently. Training data is why it can describe your company confidently and wrongly, using facts from two years ago. Live search, via GPTBot and ChatGPT-User, is where today's pages compete for citation.

What ChatGPT observably rewards is extractable structure: passages that answer a question in one self-contained block, FAQs, comparison tables, definitions that stand alone. It draws from a wider pool than the top of Google's rankings, which makes it one of the friendliest arenas for the decoupling in Chapter 4: a modest-ranking site with quotable structure gets named. It also leans noticeably on third-party surfaces, review sites, comparison articles, community threads, when recommending in a category.

## Perplexity

Perplexity is the transparency engine: always searching, always citing, links visible on every answer. That transparency makes it your best diagnostic instrument, the engine where you can see exactly which pages taught the machine its answer, which you exploited in Chapter 2.

It favors authoritative, recent, well-structured content, and its freshness preference is real enough to act on: stale pages lose citations here first. Keep your key pages visibly current, dates included, and Perplexity is winnable structure-first territory. PerplexityBot must be able to reach you, which Chapter 6 already had you verify.

## Gemini

Google's assistant draws on the Google index and, critically, the Knowledge Graph, Google's structured understanding of entities: companies, products, people, and how they relate. Gemini rewards being a well-defined entity, not just a well-ranked page. Is your company unambiguous to Google: consistent name, consistent description, structured data connecting your organization to your site, coherent presence on the surfaces Google trusts? Chapter 8 covers the schema markup that feeds this. Access-wise, Google-Extended is the switch; you checked it in Chapter 6.

A field note from my own scan runbook, as a reminder that these engines are living systems: during one client-scan period, Gemini's logged-out interface accepted a typed prompt and returned nothing at all. No error, just an empty box. Blocked silently, worse than an error. Verify your engines are actually responding when you run your checks, and note the conditions, logged in or out, which account, what day.

## Microsoft Copilot

Copilot is Bing-powered, which makes it the engine founders most consistently forget, because founders forgot Bing. The Bing index is its retrieval pool, Bingbot is its crawler, and classic Bing hygiene, indexability and Bing Webmaster Tools, its verification tooling, is the unglamorous work. It matters more than its mindshare suggests because Copilot ships inside Windows, Edge, and Microsoft 365, surfaces where a large share of B2B buyers spend their working day. If your buyer is a corporate employee, there is a real chance their first AI answer about your category comes from Copilot.

## Claude

Anthropic's Claude answers primarily from training data, plus web search where enabled, drawing on an external search index. The operational notes are simple: ClaudeBot and anthropic-ai are the crawlers to allow, and your durable public footprint, the evidence trail from Chapters 5 and 9, is what a training-data-weighted engine most reflects. Claude also matters for a reason beyond its chat interface: it is widely embedded inside other products and agent workflows, answering category questions in places you will never see.

## Reading the table

Six engines, three families of trust. Google's surfaces, AI Overviews and Gemini, trust their own ranking and entity systems: win them with fundamentals and structured entity clarity. The live searchers, ChatGPT, Perplexity, Copilot, trust what they can fetch and quote today: win them with access, extractable structure, and freshness. The training-data-weighted layer, Claude, and every engine's offline knowledge, trusts the durable public record: win it with the evidence trail, which is Chapter 9's subject.

Notice what every column shares: readable access, clear structure, real evidence. That is why this book's repairs are not six playbooks. They are one playbook with engine-specific accents, and the next chapter starts executing it.

## Check this yourself right now

Take your single most important buying question and run it through three engines you have not yet tested as a set: Gemini, Copilot, and Claude. Same question, word for word. Add the results to your panel with dates and login conditions noted.

You now have readings across the major engines. Look at the spread. Named in some and absent in others is the normal finding, and it is good news: it tells you which family of trust you already satisfy and which repairs, structure, entity, or evidence, the next three chapters should get first.
