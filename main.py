from blackbox import BertEmotionBlackBoxed
from attack import ImportanceEstimator
from attack import BurgerAttack
import click


@click.group()
def cli():
    pass


@cli.command("attack")
@click.option("--line", type=str, required=True)
def cli_attack(line: str):
    boxed = BertEmotionBlackBoxed()
    estimator = ImportanceEstimator()

    attack = BurgerAttack(boxed, estimator)
    attack.attack(line)


def main():
    cli()
    # line = "I love using transformers. The best part is wide range of support and its easy to use"

    # boxed = BertEmotionBlackBoxed()
    # estimator = ImportanceEstimator()

    # attack = BurgerAttack(boxed, estimator)
    # attack.attack(line)


if __name__ == "__main__":
    main()
