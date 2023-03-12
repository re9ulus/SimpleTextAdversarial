from dataclasses import dataclass


@dataclass
class WordImportance:
    token: str
    score: float

    def __lt__(self, other: "WordImportance") -> bool:
        return self.score < other.score


# def ComputeWordImportance(line: str, blackbox: ) -> list[WordImportance]:
#     # todo: remove punctuation
#     parts = line.split()
    
