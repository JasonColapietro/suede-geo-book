# Chapter 7: The Six Engines and Who Each One Trusts

> "I audit how ChatGPT, Perplexity, and Gemini answer your category, then ship the fix the same day."
> - Jason Colapietro, @johnnysuede bio

Founders talk about "AI" as if it were one place, the way people once said "the internet." Operationally, there is no such place. There are six engines that matter for buying questions, each with its own way of finding sources, its own trust preferences, and its own failure modes. Treating them as one thing produces the classic mistake of optimizing hard for a behavior only one engine has.

This chapter is the field guide. It is deliberately practical: for each engine, how it selects, and what that means for your pages. Two honest caveats first. These systems change fast, so treat this as the map I would draw today, not scripture; the verification habit from Part I is what keeps your map current. And none of this is inside knowledge of proprietary ranking systems. It is the published guidance plus what the engines observably do when you run real category questions through them, which you now know how to do.

## Google AI Overviews and AI Mode

The synthesized answers inside Google Search are, by Google's own explicit statement, rooted in its core search ranking and quality systems. That single sentence sets your whole strategy for this engine: whatever earns you strong ordinary rankings is what earns you presence in the answers assembled above them.

Google is unusually direct about what not to do. No special markup or files are required. Do not chunk your content into artificial fragments for AI. Do not write separate content for machines; that path risks tripping spam policies about scaled content abuse. Write helpful, people-first content with normal headings and paragraphs, demonstrate real experience and expertise, and keep your indexability clean.

One Google behavior deserves special attention: query fan-out. Google's AI features do not answer only the literal question asked. They generate related queries under the hood, retrieve for each, and synthesize across the set. A user asking about fixing lawns triggers hidden retrievals about herbicides, prevention, chemical-free methods. The implication for you is significant: covering your topic comprehensively, the parent question and its natural sub-questions, makes you retrievable across the fan-out. Ten shallow pages targeting ten keywords are worth less than one page, or one connected cluster, that genuinely covers the territory.

## ChatGPT

ChatGPT answers from two layers: model knowledge and live web search when it browses. The two layers fail differently. Model knowledge can preserve an old description of your company. For current web discovery, OpenAI identifies **OAI-SearchBot** as its search crawler; **ChatGPT-User** handles user-requested page fetches, while **GPTBot** is a separate model-development crawler. Access makes retrieval possible. Whether a retrieved page is cited, whether your brand is mentioned, whether it is recommended, and whether the answer is factually correct are four separate measurements.

What ChatGPT observably rewards is extractable structure: passages that answer a question in one self-contained block, FAQs, comparison tables, definitions that stand alone. It draws from a wider pool than the top of Google's rankings, which makes it one of the friendliest arenas for the decoupling in Chapter 4: a modest-ranking site with quotable structure gets named. It also leans noticeably on third-party surfaces, review sites, comparison articles, community threads, when recommending in a category.

## Perplexity

Perplexity is the transparency engine: it searches the web and normally shows links with its answer. That transparency makes it a useful diagnostic instrument because you can inspect the pages attached to a response, as you did in Chapter 2.

Keep your key pages accurate, structured, and honestly dated. **PerplexityBot** supports search indexing; **Perplexity-User** supports user-requested fetches. Chapter 6 had you verify both roles without treating access as proof that a page will be cited.

## Gemini

Google's AI search features draw on Google's search systems, including its index and structured understanding of entities: companies, products, people, and how they relate. Is your company unambiguous to Google: consistent name, consistent description, structured data connecting your organization to your site, coherent presence on the surfaces Google can verify? Chapter 8 covers the schema markup that supports this. **Googlebot** controls search discovery. **Google-Extended** does not control inclusion or ranking in Google Search, AI Overviews, or AI Mode; it governs separate Gemini Apps and Vertex AI training and grounding uses.

One operational warning matters because these engines are living systems: an interface can accept a typed prompt and return nothing at all. No error, just an empty box. Treat that as an engine failure, not as evidence about the company being checked. Verify that each engine actually responds, and record the conditions: logged in or out, which account, and what day.

## Microsoft Copilot

Copilot is Bing-powered, which makes it the engine founders most consistently forget, because founders forgot Bing. The Bing index is its retrieval pool, Bingbot is its crawler, and classic Bing hygiene, indexability and Bing Webmaster Tools, its verification tooling, is the unglamorous work. It matters more than its mindshare suggests because Copilot ships inside Windows, Edge, and Microsoft 365, surfaces where a large share of B2B buyers spend their working day. If your buyer is a corporate employee, there is a real chance their first AI answer about your category comes from Copilot.

## Claude

Claude combines model knowledge with web search where enabled. The access controls are role-specific: **Claude-SearchBot** supports search discovery, **Claude-User** supports user-requested retrieval, and **ClaudeBot** is the model-development crawler. Your durable public footprint still matters, but do not report an accessible page as a citation, a mention as a recommendation, or a recommendation as a factually correct description.

## Reading the table

Six engines, three families of trust. Google's surfaces, AI Overviews and Gemini, trust their own ranking and entity systems: win them with fundamentals and structured entity clarity. The live searchers, ChatGPT, Perplexity, Copilot, trust what they can fetch and quote today: win them with access, extractable structure, and freshness. The training-data-weighted layer, Claude, and every engine's offline knowledge, trusts the durable public record: win it with the evidence trail, which is Chapter 9's subject.

Notice what every column shares: readable access, clear structure, real evidence. That is why this book's repairs are not six playbooks. They are one playbook with engine-specific accents, and the next chapter starts executing it.

## Check this yourself right now

Take your single most important buying question and run it through three engines you have not yet tested as a set: Gemini, Copilot, and Claude. Same question, word for word. Add the results to your panel with dates and login conditions noted.

You now have readings across the major engines. Look at the spread. Named in some and absent in others is the normal finding, and it is good news: it tells you which family of trust you already satisfy and which repairs, structure, entity, or evidence, the next three chapters should get first.
