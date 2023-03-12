from blackbox import BertEmotionBlackBoxed
from attack import ImportanceEstimator
from attack import BurgerAttack


def main():
    line = "I love using transformers. The best part is wide range of support and its easy to use"

    boxed = BertEmotionBlackBoxed()
    estimator = ImportanceEstimator()

    attack = BurgerAttack(boxed, estimator)
    attack.attack(line)


if __name__ == "__main__":
    main()
