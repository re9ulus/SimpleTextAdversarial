from blackbox import BertEmotionBlackBoxed
from attack import ImportanceEstimator
from attack import BurgerAttack
import click


@click.group()
def cli():
    pass


@cli.command("attack")
@click.argument("line", type=str, required=True)
@click.option("--verbose", is_flag=True, show_default=True, default=False)
def cli_attack(line: str, verbose: bool):
    boxed = BertEmotionBlackBoxed()
    estimator = ImportanceEstimator()

    attack = BurgerAttack(boxed, estimator, verbose=verbose)
    attack.attack(line)


def main():
    cli()


if __name__ == "__main__":
    main()
