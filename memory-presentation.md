# Presentation Notes

## Context

Presenting GEPA to the engineering team of an internal audit department. They write GenAI software regularly but have no formal ML/AI background. Presentation is Thursday (2026-05-15). Slides are in `slides.md`, rendered to `slides.html` via Marp.

## Audience

- Write GenAI apps in production
- No formal training in ML or AI research
- Won't know what GRPO, RLHF, Pareto optimality, or minibatches are
- Will immediately ask "why not just paste the prompt into ChatGPT?"
- Care about practical outcomes: cost, reliability, how much work it is

## Slide Deck (`slides.md`)

Built with Marp. Render with:
```bash
marp --html slides.md
```

For portable output (images embedded):
```bash
marp --html --allow-local-files slides.md -o slides.pdf
marp --html --allow-local-files slides.md -o slides.pptx
```

Note: Marp HTML does NOT embed images — it uses relative paths. Keep `assets/` alongside `slides.html` if presenting from HTML. There is no `--self-contained` HTML option.

Note: Marp does NOT support Mermaid diagrams natively — use ASCII art in code blocks instead. Also, `---` inside code blocks gets parsed as a slide break — use `- - -` as a workaround.

### Current slide order
1. Title + GEPA paper image (`assets/GEPA.png`)
2. How we write prompts today (the vibes problem)
3. The prerequisite: evals (objective vs subjective)
4. Once you have an eval, you can optimize
5. Why not just ask Claude?
6. GEPA architecture (`assets/GEPA-arch.png`)
7. Glossary: paper speak → plain English
8. What a single mutation looks like (8-step walkthrough)
9. The two-model architecture (task LM vs reflection LM)
10. What the Pareto frontier is (with checkmark table)
11. Two datasets, two jobs (train vs val)
12. Why only 3 examples at a time (minibatch rationale)
13. What the reflection LM actually sees (concrete complaint example)
14. What you get at the end (`assets/example-prompt.png`)
15. When GEPA won't help (limits)
16. The practical takeaway (5 bullets)
17. Questions + links

### Commented-out slides (available to restore)
- What the paper actually tested on (HotpotQA, HoVer, IFBench, PUPA benchmark table)
- Real results from the paper (improvement numbers table)
- GEPA vs reinforcement learning (GRPO comparison table)

### Key design decisions
- Complaint classification used as the running example throughout (not AIME or academic tasks)
- Pareto frontier explained via checkmark table, not math. Definition: "you can't improve one thing without making another worse." Frontier = set of prompts where that's true.
- Named after Vilfredo Pareto (economist, trade-offs). Same person as 80-20 rule but unrelated concept.
- Mutation is directed not random — this distinction is load-bearing for the whole talk
- Merge mechanism intentionally omitted from slides (too much detail for this audience)
- "Mutation is directed, not random" slide was removed — covered implicitly by the reflection LM slides

### Things NOT in the slides (intentionally)
- The merge mechanism (algorithmic, no LLM call — combines two specialist candidates into one generalist using component-level git-merge-style logic. Only useful with multi-component prompts.)
- System-aware merge LLM vs no-LLM distinction
- frontier_type parameter options
- The family tree / fan-out mechanics
- Anything about implementing a custom GEPAAdapter
- How parents get discarded (passive — Pareto filtering drops a prompt only when another dominates it on ALL val examples, not eagerly)
- Final prompt selection (highest average val score — frontier is a search strategy, not a final selection strategy)

## Concepts to Have Ready for Q&A

**"How is this different from just prompting a model to improve the prompt?"**
GEPA runs the prompt against real data and feeds actual failure traces back in. A one-shot ChatGPT rewrite is guessing what might go wrong. GEPA knows exactly what went wrong.

**"Does this change the model?"**
No. Weights are frozen. Output is just a better text prompt. Drop-in replacement.

**"How much does it cost?"**
Cheap model for task (99% of calls), smart model for reflection (1%). A full run might cost a few dollars depending on dataset size and model choice.

**"How many examples do we need?"**
As few as 3 (paper claim). More is better. 10-20 is a reasonable starting point. 50/50 train/val split for small datasets.

**"What if our task is subjective?"**
Use an LLM as judge in the evaluator. The judge returns a score and feedback, GEPA treats it the same as any other evaluator.

**"Why is it called Genetic-Pareto?"**
Genetic = evolutionary analogy (mutation, selection). Pareto = keeps candidates that are best at something, not just the global best. Both are slightly misleading names but they're what the paper uses.

**"Is this the same Pareto as the 80-20 rule?"**
Same person (Vilfredo Pareto, Italian economist), different idea. 80-20 is about unequal distributions. Pareto optimality is about trade-offs where you can't improve one thing without worsening another. Unrelated concepts.

## Blog Post (in progress)

Planned after the presentation. Audience: ML engineers (broader, more technical than audit team).

Goal: concrete experiment with a real dataset showing GEPA actually doing something — seed prompt failing in interesting ways, reflection LM diagnosing failures, optimized prompt with visible improvements.

Next step: pick a HuggingFace dataset. See `memory-experiment.md` for requirements.
