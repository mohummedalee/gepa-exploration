import json
import gepa
from gepa.adapters.default_adapter.default_adapter import EvaluationResult


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]


trainset = load_jsonl("train.jsonl")
valset = load_jsonl("val.jsonl")


# ---------------------------------------------------------------------------
# Evaluator
# Receives the data example and the model's raw response string.
# Returns EvaluationResult(score, feedback, objective_scores)
# ---------------------------------------------------------------------------
def evaluator(data, response) -> EvaluationResult:
    if "</think>" in response:
        # Remove thinking, if present
        response = response.split("</think>")[-1]
    prediction = response.strip().lower()
    correct = prediction == data["answer"]
    score = 1.0 if correct else 0.0
    feedback = (
        f"Correct."
        if correct
        else f"Wrong. Expected '{data['answer']}', got '{prediction}'."
    )
    return EvaluationResult(score=score, feedback=feedback)


# ---------------------------------------------------------------------------
# Optimize
# task_lm:       the model that answers each classification question
# reflection_lm: the model that reads failure traces and rewrites the prompt
# ---------------------------------------------------------------------------
result = gepa.optimize(
    seed_candidate={
        "system_prompt": "Classify the text as 'complaint' or 'not_complaint'. Reply with only one of those two labels."
    },
    trainset=trainset,
    valset=valset,
    task_lm="ollama/qwen3:8b",
    evaluator=evaluator,
    reflection_lm="anthropic/claude-sonnet-4-6",
    max_metric_calls=60,
)

print("Best prompt:\n", result.best_candidate["system_prompt"])
print("Val score:  ", result.best_score)
