from typing import Iterator, Tuple


class TextSample:
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
