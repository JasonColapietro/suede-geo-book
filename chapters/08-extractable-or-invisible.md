# Chapter 8: Extractable or Invisible

> "AI systems extract passages, not pages."
> — from the Suede AI SEO methodology

The machines can read you. You know which engines trust what. Now comes the chapter where you change your site, and it starts with the five-word sentence at the top, which is the closest thing this field has to a law of physics.

AI systems extract passages, not pages. When an engine cites you, it does not present your page. It lifts a passage, a sentence to a short paragraph, and builds its answer from that. Which means the unit of AI visibility is not the page you have been polishing. It is the passage, and most sites, including most well-written ones, contain almost no passages that survive extraction.

## The extraction test

Take any paragraph from your site and apply one test: pulled out alone, with no surrounding context, does it still say something true, complete, and attributable?

Most marketing copy fails instantly. "We take a fundamentally different approach" extracts to nothing; different from what, at what? "That's why thousands of teams trust us" fails on both attribution and content; who is we, trusted to do what? These sentences work on the page, where headers and context carry the meaning. Extracted, they are fog.

Now the passing version: "Acme is project management software for construction subcontractors; it tracks change orders, lien deadlines, and payment schedules in one dashboard, with plans starting at $49 per month." Ripped from the page and dropped into an AI answer, that passage still works. Every claim is self-contained: who, for whom, what, how much. That is an extractable passage, and building them is a discipline of one rule: write every key claim so it survives alone.

## The blocks that get lifted

You do not have to guess which shapes engines quote. Watch the answers, as you have been doing since Chapter 1, and the same few blocks appear over and over. Build these, in normal prose, on the pages that matter:

**Definition blocks.** For "what is" questions. One tight paragraph, early in the page, naming the thing and what it does. Your product page should define your product in its first breath, not after the hero video.

**Step blocks.** For "how to" questions. Numbered, each step a verb with a result.

**Comparison tables.** For "X vs Y" questions, which are pure buying intent. A real table with honest rows. Engines lift tables gratefully, and so do buyers.

**FAQ blocks.** Real questions phrased the way buyers ask them, each with a direct answer in the first sentence. This is also where Chapter 7's fan-out pays off: the sub-questions Google retrieves for are exactly what a good FAQ covers.

**Evidence blocks.** A specific claim with its source and date attached. The next chapter is entirely about why these outperform adjectives.

Aim answers at roughly the 40-to-60-word mark: a complete thought, quotable whole. And answer first, then elaborate. The machine does not dig, and increasingly, neither does the human.

## Structure is signposting, not decoration

Around the passages goes the page's skeleton, and here the rule is boring on purpose: one H1 that says what the page is about, H2s and H3s that name their sections honestly, headings that match how buyers phrase questions. A heading is a signpost telling a machine "the answer to this lives here." "How much does Acme cost" is a signpost. "Flexible plans for every journey" is interior decorating.

Recall Google's guidance from Chapter 7, because it draws the line perfectly: do not chunk content into artificial fragments for AI, do not write separate machine-facing content. Write for people, organize for clarity. Everything in this chapter lives on the right side of that line. An extractable passage is just a clear paragraph. A signpost heading is just an honest one. You are not gaming anything; you are removing the fog that kept machines, and skimming humans, from using what you wrote.

## Schema: say it in the machines' grammar

Structured data, schema markup, is a block of JSON-LD in your page that states facts in a standard vocabulary: this page describes an Organization with this name and logo; this is a Product with this price; these are FAQ questions with these answers. It feeds Google's entity understanding, the Knowledge Graph plumbing behind Gemini from Chapter 7, and removes ambiguity about who and what you are.

Three rules keep you out of trouble. Mark up only what is visibly true on the page; schema that contradicts your content is worse than none. Use the boring, supported types: Organization, Product, FAQPage, Article, HowTo, BreadcrumbList. And keep your identity consistent: your organization should be one entity across your site, not a slightly different name and description on every page. Validate what you ship with Google's Rich Results Test rather than trusting that it parses.

## llms.txt: what is real and what is hype

You will hear about llms.txt: a proposed convention, a plain-text-markdown file at your domain root that gives AI systems a curated map of your site, your key pages and what they contain, in a format built for machine reading.

The honest status report: it is a proposal, not a standard. Google has said plainly that no special files are required for its AI features. Some other engines parse llms.txt and similar machine-readable files when present; support is uneven and shifting. So the claim I will make is deliberately modest: it is cheap, it cannot hurt, and for the engines that do read it, it hands them your site's map in their native grammar. I ship one in most repair engagements, in about twenty minutes, and I would never claim it guarantees anything. That modest claim generalizes: anyone selling you a secret file, tag, or trick that "gets you into AI answers" is selling weather again. Access, passages, structure, schema, evidence. There is no sixth secret.

## The one-page drill

Do not renovate the whole site this week. Take one page, the one that should answer your category's biggest buying question, and run the drill: define the thing in the first paragraph. Convert the key claims into passages that pass the extraction test. Add the comparison table and the FAQ if the question warrants them. Fix the headings into signposts. Add the supported schema. Then reread it as a human and confirm it got better for them too. It will have. That is the tell that you did this right.

## Check this yourself right now

Open your most important page and view the raw source. Find the paragraph that is supposed to answer your buyer's main question. Copy it out, paste it somewhere blank, alone, and apply the test: true, complete, attributable, with no help from the rest of the page?

Then rewrite it until it passes, and ship that one paragraph. One passing passage on your most-asked question is the smallest real repair in this book, and you can have it live within the hour.
