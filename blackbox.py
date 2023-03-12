from transformers import pipeline
import pprint
from typing import Iterator, Tuple, Type
from dataclasses import dataclass
import random


class BlackBox:
    def predict(self, text: str) -> dict[str, float]:
        raise NotImplementedError()


class BertEmotionBlackBoxed(BlackBox):
    def __init__(self):
        super().__init__()
        self.clf = pipeline(
            "text-classification",
            model='bhadresh-savani/distilbert-base-uncased-emotion',
            return_all_scores=True,
        )

    def predict(self, text: str) -> dict[str, float]:
        raw_predictions = self.clf(text,)[0]
        predictions = {}
        for item in raw_predictions:
            predictions[item["label"]] = item["score"]
        return predictions


class Text:
    def __init__(self, line: str):
        self.line = line
        self.tokens = line.split()
        self.patched_tokens = self.tokens[:]

    def raw(self) -> str:
        return self.line
    
    def patched(self) -> str:
        return ' '.join(self.patched_tokens)

    def iter_drop_token(self) -> Iterator[Tuple[str, str]]:
        for idx in range(len(self.tokens)):
            missing_token = self.tokens[idx]
            other_tokens = self.tokens[:idx] + self.tokens[idx+1:]
            text_without_token = ' '.join(other_tokens)
            yield missing_token, text_without_token

    def try_patch(self, idx: int, new_token: str) -> str:
        old_token = self.patched_tokens[idx]
        self.patched_tokens[idx] = new_token
        result = ' '.join(self.patched_tokens)
        self.patched_tokens[idx] = old_token
        return result
    
    def apply_patch(self, idx: int, new_token: str):
        self.patched_tokens[idx] = new_token


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

    def estimate_all(self, model: Type[BlackBox], text: Text, label: str, base_score: float):
        result = []
        for (idx, (token, line_without_token)) in enumerate(text.iter_drop_token()):
            importance = self._estimate(model, line_without_token, label, base_score)
            result.append(TokenImportance(token, importance, idx))
        return list(sorted(result, reverse=True))


class Atack:
    def __init__(self, target: Type[BlackBox], estimator: Type[ImportanceEstimator], verbose: bool = True):
        self.target = target
        self.estimator = estimator
        self.verbose = verbose

    def atack(self, line: str) -> str:
        text = Text(line)
        base_label, base_score = self._get_base_prediction(text.raw())
        importance = self._get_importance(text, base_label, base_score)
        self._atack(text, importance, base_label, base_score)
        return text.raw()
    
    def _atack(self, text: Text, imporatance: list[TokenImportance], base_label: str, base_score: float):
        raise NotImplementedError()

    def _get_importance(self, text: Text, base_label: str, base_score: float) -> list[TokenImportance]:
        if self.verbose:
            print(f"base label: {base_label} ; base_score: {base_score}")
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


class BurgerAtack(Atack):
    def _atack(self, text: Text, importance: list[TokenImportance], base_label: str, base_score: float):
        n_trials = 5  # just random number
        global_best_score = base_score
        for item in importance:
            token = item.token
            candidates = set()

            for _ in range(n_trials):
                candidates.add(self.insert(token))
                candidates.add(self.delete(token))
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

            new_class, _ = self._get_base_prediction(text.patched())
            if self.verbose:
                print("patched text: ", text.patched())
                print(f"new class {new_class}")
            if new_class != base_label:
                break
   
    @staticmethod
    def insert(token: str) -> str:
        """Insert a space into the word"""
        try:
            idx = random.randint(1, len(token) - 1)  # TODO: check bounds
            return token[:idx] + ' ' + token[idx + 1:]
        except:
            print("err: ")
            return token

    @staticmethod 
    def delete(token: str) -> str:
        """Delete a random character of the word except for the first and the last character"""
        try:
            idx = random.randint(1, len(token)-1)  # TODO: check bounds
            return token[:idx] + token[idx + 1:]
        except:
            print("err: ")
            return token

    @staticmethod
    def swap(token: str) -> str:
        raise NotImplementedError()

    @staticmethod
    def subc(token: str) -> str:
        raise NotImplementedError()




def main():
    line = "I love using transformers. The best part is wide range of support and its easy to use"

    boxed = BertEmotionBlackBoxed()
    estimator = ImportanceEstimator()

    atack = BurgerAtack(boxed, estimator)
    atack.atack(line)
    


if __name__ == "__main__":
    main()

    """
    boxed = BertEmotionBlackBoxed()

    # text = Text("I love using transformers. The best part is wide range of support and its easy to use")
    text = Text("I l0ve using transformers. The b est part is w1de range of support and its easy to use")
    prediction = boxed.predict(text.raw())
    pprint.pprint(prediction)

    top_score, top_label = 0, ""
    for key, val in prediction.items():
        if val > top_score:
            top_label = key
            top_score = val

    print("top label / score: ", top_label, top_score)

    importance = []
    for (idx, (token, text_without_token)) in enumerate(text.iter_drop_token()):
        sample_pred = boxed.predict(text_without_token)

        sample_score = sample_pred[top_label]
        token_importance = top_score - sample_score
        importance.append((token_importance, idx, token))

    pprint.pprint(list(sorted(importance)))
    """
