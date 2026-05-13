# GEPA Exploration

Learning repo for [GEPA](https://github.com/gepa-ai/gepa) — a prompt optimization framework that uses LLM-based reflection and Pareto-efficient evolutionary search.

Paper: [Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457)

## What's here

**`experiment.py`**
A toy complaint classification experiment using `gepa.optimize()`. Uses `ollama/qwen3:8b` as the task model and `claude-sonnet-4-6` as the reflection model. Dataset is in `train.jsonl` / `val.jsonl`. Currently too easy to trigger real optimization — next step is replacing it with a real HuggingFace dataset.

**`train.jsonl` / `val.jsonl`**
8 training + 4 validation examples of complaint vs non-complaint customer messages.

**`slides.md`**
A Marp presentation explaining GEPA to a non-ML engineering audience. Covers evals, the optimization loop, the Pareto frontier, how mutation works, and results from the paper. Render with:
```bash
marp --html slides.md
```

**`presentation-script.md`**
Audience notes and outline used to build the slides.

**`memory-experiment.md`**
Dense notes on the GEPA codebase internals, how the experiment is set up, and what needs to happen next. Written so another agent or future session can pick this up without re-reading everything.

**`memory-presentation.md`**
Presentation context: audience profile, slide structure, Q&A prep, and blog post direction.

## Setup

Requires the GEPA library cloned separately:
```bash
git clone https://github.com/gepa-ai/gepa
cd gepa
uv sync --extra dev
```

Then run the experiment from inside the `gepa/` directory:
```bash
ANTHROPIC_API_KEY=your-key uv run python ../experiment.py
```

Ollama must be running with `qwen3:8b` pulled:
```bash
ollama pull qwen3:8b
```

## What's next

- Pick a real HuggingFace dataset where a naive prompt actually struggles
- Run a proper optimization and document the before/after
- Write a blog post showing the full loop: seed prompt → failures → reflection → improved prompt
