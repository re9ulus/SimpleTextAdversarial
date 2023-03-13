from typing import Tuple, Type
import pprint
import random
from blackbox import BlackBox
from dataclasses import dataclass
from text_sample import TextSample


@dataclass
class TokenImportance:
    token: str
    importance: float
    idx: int

    def __lt__(self, other: "TokenImportance") -> bool:
        return self.importance < other.importance

    def __str__(self) -> str:
        return f"{self.token} / {self.idx} : self.importance"


class ImportanceEstimator:
    def _estimate(self, model: Type[BlackBox], line: str, label: str, base_score: float):
        pred = model.predict(line)
        current_score = pred[label]
        return base_score - current_score

    def estimate_all(self, model: Type[BlackBox], text: TextSample, label: str, base_score: float):
        result = []
        for (idx, (token, line_without_token)) in enumerate(text.iter_drop_token()):
            importance = self._estimate(model, line_without_token, label, base_score)
            result.append(TokenImportance(token, importance, idx))
        return list(sorted(result, reverse=True))


class BaseAttack:
    """
    Base class to simplify attack on NLP model

    Inherit your attack from it and override _attack method
    """
    def __init__(self, target: Type[BlackBox], estimator: Type[ImportanceEstimator], verbose: bool = True):
        self.target = target
        self.estimator = estimator
        self.verbose = verbose

    def attack(self, line: str) -> str:
        text = TextSample(line)
        base_label, base_score = self._get_base_prediction(text.raw())
        importance = self._get_importance(text, base_label, base_score)
        self._attack(text, importance, base_label, base_score)
        return text.raw()
    
    def _attack(self, text: TextSample, imporatance: list[TokenImportance], base_label: str, base_score: float):
        raise NotImplementedError()

    def _get_importance(self, text: TextSample, base_label: str, base_score: float) -> list[TokenImportance]:
        if self.verbose:
            print(f"base label: {base_label}")
            print(f"score: {base_score}")
        importance = self.estimator.estimate_all(self.target, text, base_label, base_score)
        if self.verbose:
            print("importance:")
            # TODO: Print in table
            pprint.pprint(importance)
        return importance

    def _get_base_prediction(self, line: str) -> Tuple[str, float]:
        prediction = self.target.predict(line)
        top_label, top_score = "", 0
        for label, score in prediction.items():
            if score > top_score:
                top_label, top_score = label, score
        return top_label, top_score


def _insert(token: str) -> str:
    """Insert a space into the word"""
    if len(token) <= 2:
        return token
    idx = random.randint(1, len(token) - 2)
    return token[:idx] + ' ' + token[idx + 1:]


def _delete(token: str) -> str:
    """Delete a random character of the word except for the first and the last character"""
    if len(token) <= 2:
        return token
    idx = random.randint(1, len(token)-2)  # TODO: check bounds
    return token[:idx] + token[idx + 1:]


def _swap(token: str) -> str:
    first = random.randint(0, len(token) - 1)
    second = random.randint(0, len(token) - 1)
    if first == second:
        return token
    arr = list(token)
    arr[first], arr[second] = arr[second], arr[first]
    return ''.join(arr)


def _subc(token: str) -> str:
    raise NotImplementedError()


class BurgerAttack(BaseAttack):
    def _attack(self, text: TextSample, importance: list[TokenImportance], base_label: str, base_score: float):
        n_trials = 5  # just random number
        global_best_score = base_score

        possible_bugs = [
            _insert,
            _delete,
            _swap,
        ]

        for item in importance:
            token = item.token
            candidates = set()

            for _ in range(n_trials):
                for bugf in possible_bugs:
                    candidates.add(bugf(token))
            candidates = list(candidates)

            best_score, best_candidate = global_best_score, candidates[0]
            for candidate_token in candidates:
                patched_text = text.try_patch(item.idx, candidate_token)
                pred = self.target.predict(patched_text)
                score = pred[base_label]
                if score < best_score:
                    best_score, best_candidate = score, candidate_token

            if best_score < global_best_score:
                global_best_score = best_score
                text.apply_patch(item.idx, best_candidate)

            new_label, _ = self._get_base_prediction(text.patched())
            if self.verbose:
                print(f"new label {new_label}")
            print("patched text: ", text.patched())
            if new_label != base_label:
                break
   
