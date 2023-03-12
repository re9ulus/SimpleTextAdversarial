from transformers import pipeline


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
