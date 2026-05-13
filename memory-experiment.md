# GEPA Experiment Notes

## What GEPA Is

GEPA (Genetic-Pareto) is a prompt optimization framework. Given a seed prompt, a dataset, and a scoring function, it iteratively improves the prompt using LLM-based reflection. Paper: arxiv.org/abs/2507.19457. Repo: github.com/gepa-ai/gepa.

Key claim: beats GRPO (a reinforcement learning method) at 35x fewer evaluations by using full execution traces instead of scalar rewards.

## Repo Structure

Cloned at `/Users/muhammadali/Desktop/building/GEPA/gepa/`. Uses `uv` for dependency management.

```
src/gepa/
  api.py                     # gepa.optimize() — the main entry point used in experiment
  optimize_anything.py       # higher-level API, not used yet
  core/                      # engine, state, adapter interface
  proposer/
    reflective_mutation/     # the main mutation mechanism (LLM-based)
    merge.py                 # system-aware merge (algorithmic, no LLM)
  adapters/
    default_adapter/         # what we're using — single-turn LLM tasks
  strategies/
    instruction_proposal.py  # the actual prompt sent to the reflection LM
```

Run the experiment from inside `gepa/`:
```bash
cd /Users/muhammadali/Desktop/building/GEPA/gepa
uv sync --extra dev
ANTHROPIC_API_KEY=... uv run python ../experiment.py
```

## How GEPA Works (Mechanically)

### Two datasets
- **trainset**: sampled for minibatches during reflection. The reflection LM reads these examples directly (input, output, feedback). Do NOT use for unbiased evaluation.
- **valset**: used to score candidates and maintain the Pareto frontier. Reflection LM never sees these. Separation prevents overfitting.

### One iteration
1. Pick a prompt from the Pareto frontier
2. Sample a minibatch (default 3 examples) from trainset
3. Run the prompt on the minibatch using task_lm
4. Collect: input, output, evaluator feedback
5. Send to reflection_lm: "here's the prompt, here's what it got wrong, write a better one"
6. Run new prompt on same minibatch — did it improve?
7. If yes: evaluate on full valset, update Pareto scores, add to pool
8. If no: discard

### Pareto frontier
Keep any candidate that is best at *something* (best on at least one val example). A candidate is dropped only when another beats it on everything simultaneously. This prevents losing specialized knowledge — a prompt that's the only one solving example 3 stays alive even if its average score is low.

### Two mutation mechanisms
1. **Reflective mutation** (default): one prompt → LLM reads failures → proposes improved prompt. LLM call happens here.
2. **System-aware merge** (opt-in, `use_merge=True`): two prompts + common ancestor → algorithmically swap components based on which descendant changed what. NO LLM call. Pure component selection from family tree.

### The reflection prompt (from instruction_proposal.py)
```
I provided an assistant with the following instructions:
<curr_param>

Here is how it performed on some examples:
<side_info>   ← input, output, evaluator feedback for each minibatch example

Write an improved version of the instructions.
```

### Fan-out / how multiple candidates accumulate
Not a population — strictly sequential. Each iteration proposes at most one new candidate. The tree of candidates in Figure 3 of the paper is the accumulated result of many iterations, not planned upfront. Branching happens naturally as different prompts get selected from the frontier and produce different descendants.

## The Experiment (experiment.py)

Toy complaint classification task. Binary label: `complaint` / `not_complaint`.

- **task_lm**: `ollama/qwen3:8b` (local, via Ollama)
- **reflection_lm**: `anthropic/claude-sonnet-4-6`
- **trainset**: 8 examples in `train.jsonl`
- **valset**: 4 examples in `val.jsonl`
- **max_metric_calls**: 60
- **API**: `gepa.optimize()` with `DefaultAdapter` (no custom adapter needed)

### Why it doesn't do anything useful yet
The task is too easy. Qwen3:8b gets 4/4 on the valset with the seed prompt. GEPA skips every iteration because `skip_perfect_score=True` by default — if all minibatch scores are perfect, there's nothing to reflect on.

### What the DefaultAdapter expects
Data format:
```python
{"input": str, "additional_context": dict, "answer": str}
```
Evaluator signature:
```python
def evaluator(data, response) -> EvaluationResult(score, feedback, objective_scores)
```
The `feedback` string goes directly into the reflection prompt as ASI.

### Qwen3 thinking tokens
Qwen3:8b outputs `<think>...</think>` blocks before answers. Handled in evaluator:
```python
if "</think>" in response:
    response = response.split("</think>")[-1]
```

## Next Step

**Pick a real dataset from HuggingFace and make the experiment interesting.**

Requirements for a good dataset:
- Clear right/wrong label (binary or small set of classes)
- Hard enough that qwen3:8b with a naive seed prompt actually fails on some examples
- Rich failure modes so the reflection LM has something to work with
- Relevant to ML engineers (the blog post audience)
- Not a pure academic benchmark (no AIME, GSM8K, etc.)

Directions being considered:
- Something domain-specific where naive prompts fail on jargon (e.g. financial sentiment)
- Something with genuinely confusable classes (e.g. emotion detection)
- Something ML engineers encounter in production (e.g. hallucination detection, content moderation)

The blog post story should be: seed prompt fails in interesting ways → GEPA shows its work → optimized prompt has specific rules targeting the failure modes → improvement is visible and explainable.

## Key Config Gotchas
- `litellm_config.yaml` contains API keys — in `.gitignore`, never commit
- Run from inside `gepa/` directory, script is at `../experiment.py`
- Ollama must be running and `qwen3:8b` pulled before running
- `ANTHROPIC_API_KEY` must be set in environment
- Docs recommend 50/50 train/val split for datasets under 200 examples
- Docs recommend `max_metric_calls` = at least 15-30x len(valset)
