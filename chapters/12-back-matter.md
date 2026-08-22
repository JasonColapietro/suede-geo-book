# Appendix A: The Founder's AI Visibility Checklist

Print this. It is the whole book in one page, in severity order.

**Baseline (Chapter 10, Lane 1)**
- [ ] Prompt set written: 10 to 20 buying questions (category, best-for, versus, how-to, pricing)
- [ ] Run across ChatGPT, Perplexity, Gemini, AI Overviews, Copilot, Claude
- [ ] Screenshots dated; named/not-named and citations recorded per engine
- [ ] Login conditions noted

**Access (Chapter 6): fix before everything else**
- [ ] robots.txt fetched and read block by block
- [ ] Per-role access verdict written: search discovery (OAI-SearchBot, PerplexityBot, Claude-SearchBot, Googlebot, Bingbot), user-request fetches (ChatGPT-User, Perplexity-User, Claude-User), and model-development controls (GPTBot, ClaudeBot, CCBot, Google-Extended): allowed / blocked / unverified with reason
- [ ] Bot-protection and firewall layers checked for AI-crawler challenges
- [ ] Raw-source test: real copy present in initial HTML of money pages
- [ ] Sitemap present, listed in robots.txt, contains money pages
- [ ] No stray noindex or misaimed canonicals on money pages
- [ ] Ten-second check run at optimize.suedeai.ai

**Money pages (Chapter 8)**
- [ ] Definition in the first paragraph of each money page
- [ ] Key claims pass the extraction test (true, complete, attributable, alone)
- [ ] Answers-first FAQ, phrased as buyers ask
- [ ] Comparison table where the buying question calls for one
- [ ] Headings are signposts, not slogans
- [ ] Supported schema only (Organization, Product, FAQPage, Article, HowTo), validated, matching visible content
- [ ] Visible, truthful updated dates
- [ ] llms.txt shipped, claims kept modest

**Evidence (Chapter 9)**
- [ ] Claims-versus-receipts count run on money pages
- [ ] Named authors with real bios and Person schema on key content
- [ ] Numbers carry dates, sources, or methodology
- [ ] Disclosures present where a skeptic would want them
- [ ] Review-platform presence accurate; happy customers actually asked
- [ ] Offsite trail checked: "What do people say about [company]? Include sources."

**Entity (Chapters 7, 10)**
- [ ] One consistent organization name and description everywhere
- [ ] Organization and Person schema connect people, product, and site
- [ ] "What do you know about [company]?" asked across engines; coherence graded

**Rhythm (Chapter 11)**
- [ ] Repairs logged with ship dates
- [ ] Inputs verified live before each repeat measurement (the day-6 lesson)
- [ ] Monthly 30-minute measurement on the calendar, same prompts, same file
- [ ] Deltas read as trend, displacement, and input correlation; single-month wobble ignored

# Appendix B: Glossary

**AI Overviews.** Google's synthesized answers at the top of search results, built on its core ranking and quality systems.

**Answer engine.** Any system that responds to a question with a synthesized answer naming sources or companies, rather than a list of links.

**Citation.** An engine using, and often linking, a specific page as a source for its answer. The unit of victory in this book.

**Crawler / bot.** Software an engine sends to fetch web pages. Examples include OAI-SearchBot, PerplexityBot, Claude-SearchBot, Googlebot, Bingbot, GPTBot, ClaudeBot, and CCBot.

**Google-Extended.** A robots.txt product token that controls certain uses of crawled content for Gemini and Vertex AI systems. It is not a separate crawler and does not control inclusion or ranking in Google Search.

**Delta.** The change between two dated readings of the same prompt set. The only measurement this book trusts.

**E-E-A-T.** Experience, Expertise, Authoritativeness, Trustworthiness: the quality framework behind Google's guidelines, read in this book as a checklist of unforgeable signals.

**Entity.** A thing machines can identify unambiguously: a company, person, or product. Entity clarity is being one consistent thing everywhere.

**Extraction test.** Pulled out alone, does the passage still say something true, complete, and attributable?

**GEO.** Generative engine optimization: the practice of earning presence in AI-generated answers. Also called AI SEO, AEO (answer engine optimization), and LLMO. All one discipline: access, structure, evidence, entity, rhythm.

**Knowledge Graph.** Google's structured map of entities and relationships, feeding Gemini and the entity lane of the audit.

**llms.txt.** A proposed convention: a machine-readable file at your domain root mapping your key pages for AI systems. Cheap, modest, unevenly supported.

**Point-in-time.** The status of every AI answer ever captured. Answers move between days, sessions, and accounts; screenshots are dated for a reason.

**Prompt set.** Your standing list of 10 to 20 buying questions, run identically each month.

**Query fan-out.** Google's AI generating related queries under the hood and synthesizing across them; the reason topical coverage beats keyword sniping.

**Schema / structured data.** JSON-LD in your pages stating facts in a standard vocabulary machines parse directly.

**Zero-click search.** A query answered on the results surface itself, with no visit to any website.

# Appendix C: The Tools

Everything in this book can be done by hand. These are the shortcuts, disclosed plainly per Chapter 9.

**optimize.suedeai.ai**: free, ten seconds, no email. Checks whether AI crawlers can read your site: the access lane's front door.

**seo.suedeai.ai**: the done-for-you version. The same five lanes run continuously as a retainer, with PR, entity and reputation work beside them, for a small number of companies: the baseline measured for you, the repairs shipped as pull requests and CMS edits, and Chapter 11 kept running without you. Scope and price are quoted by reply, because both depend on the site. This book, in both editions, lives at seo.suedeai.ai/book.

Every engagement carries a point-in-time disclaimer and a refund policy. None of them guarantees a citation, a ranking, or a recommendation, because nobody honest can.

*The Screenshot* is a Johnny Suede Press book by Jason Colapietro, founder of Suede Labs. All engine behaviors described were observed as of this edition's writing and will drift; the discipline is built to outlast the details. Trademarks belong to their owners; the engines named here are products of their respective companies, and nothing in this book implies their endorsement.
