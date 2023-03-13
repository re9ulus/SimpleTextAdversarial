from typing import Iterator, Tuple, Type, Optional


class BaseTokenizer:
    def tokenize(self, line: str) -> list[str]:
        """split text into tokens"""
        raise NotImplementedError()

    def collect(self, tokens: list[str]) -> str:
        """collect tokens into string"""
        raise NotImplementedError()


class SimplestTokenizer(BaseTokenizer):
    def tokenize(self, line: str) -> list[str]:
        return line.split()

    def collect(self, tokens: list[str]) -> str:
        return ' '.join(tokens)


class TextSample:

    def __init__(self, line: str, tokenizer: Optional[Type[BaseTokenizer]] = None):
        self.line = line
        self.tokenizer = tokenizer or SimplestTokenizer()
        self.tokens = self.tokenizer.tokenize(line)
        self.patched_tokens = self.tokens[:]

    def raw(self) -> str:
        return self.line
    
    def patched(self) -> str:
        return ' '.join(self.patched_tokens)

    def iter_drop_token(self) -> Iterator[Tuple[str, str]]:
        for idx in range(len(self.tokens)):
            dropped_token = self.tokens[idx]
            other_tokens = self.tokens[:idx] + self.tokens[idx+1:]
            text_without_token = self.tokenizer.collect(other_tokens)
            yield dropped_token, text_without_token

    def try_patch(self, idx: int, new_token: str) -> str:
        old_token = self.patched_tokens[idx]
        self.patched_tokens[idx] = new_token
        result = self.tokenizer.collect(self.patched_tokens)
        self.patched_tokens[idx] = old_token
        return result
    
    def apply_patch(self, idx: int, new_token: str):
        self.patched_tokens[idx] = new_token
