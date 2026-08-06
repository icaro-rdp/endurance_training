---
name: transcript-to-episode-note
description: Convert podcast or video transcripts into the project’s structured episode-note markdown format, and use when turning raw transcript text into readable guide-style notes that match the Empirical Cycling Podcast files in this repo.
---

# Transcript to Episode Note

## Goal

Turn a raw transcript into a clean markdown note that reads like a reference guide, not a transcript dump.

## Workflow

1. Read the transcript for the main topic, speakers, recurring claims, and any explicit structure.
2. Identify the best target category or folder pattern from the repo if the user specifies one.
3. Write a title that summarizes the topic as a usable guide.
4. Add a source line that names the original episode, podcast, or speaker set.
5. Rewrite spoken language into concise reference prose.
6. Group content into clear sections with headings, tables, bullets, and callouts where they help.
7. Preserve the original meaning, and avoid inventing details that are not in the transcript.

## Output Style

- Match the tone of the existing `Episodes/Empirical_cycling_podcast/` files: practical, analytical, and structured.
- Start with `#` for the title, then a `_Source: ..._` line, then `---`.
- Use section names that fit the material, such as:
  - `## What Is ...?`
  - `## How to Think About It`
  - `## How to Apply It`
  - `## When to Use It`
  - `## Key Metrics or Signals`
  - `## Pros and Cons Summary`
  - `## Decision Checklist`
- Use tables for comparisons, thresholds, and decision rules.
- Use bullets for examples, use cases, and checklists.
- Keep direct quotes only when they add emphasis or preserve a memorable line.

## Content Rules

- Preserve the transcript’s actual claims and avoid unsupported additions.
- If the transcript is noisy or incomplete, infer only the minimum needed structure from context.
- If the transcript contains a framework, convert it into a decision tree, checklist, or comparison table.
- If the transcript centers on a workout, concept, or method, explain:
  - what it is
  - how to recognize or prescribe it
  - when to use it
  - what to track
  - common mistakes or limitations
- If there is no obvious training concept, still format it as a readable guide with the strongest available structure.

## Reference Template

Use [references/episode-template.md](references/episode-template.md) when you want a starting point for formatting, note that it's just a template and not a strict requirement. The goal is to produce a readable, structured note that captures the essence of the transcript.

