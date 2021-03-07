# coding=utf-8
# Copyright 2018 The Open AI Team Authors and The HuggingFace Inc. team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tokenization classes for OpenAI GPT."""

from tokenizers import ByteLevelBPETokenizer

from .tokenization_utils_base import BatchEncoding
from .tokenization_utils_fast import PreTrainedTokenizerFast


VOCAB_FILES_NAMES = {
    "vocab_file": "vocab.json",
    "merges_file": "merges.txt",
}

PRETRAINED_VOCAB_FILES_MAP = {
    "vocab_file": {
        "gpt2": "https://s3.amazonaws.com/models.huggingface.co/bert/gpt2-vocab.json",
        "gpt2-medium": "https://s3.amazonaws.com/models.huggingface.co/bert/gpt2-medium-vocab.json",
        "gpt2-large": "https://s3.amazonaws.com/models.huggingface.co/bert/gpt2-large-vocab.json",
        "gpt2-xl": "https://s3.amazonaws.com/models.huggingface.co/bert/gpt2-xl-vocab.json",
        "distilgpt2": "https://s3.amazonaws.com/models.huggingface.co/bert/distilgpt2-vocab.json",
    },
    "merges_file": {
        "gpt2": "https://s3.amazonaws.com/models.huggingface.co/bert/gpt2-merges.txt",
        "gpt2-medium": "https://s3.amazonaws.com/models.huggingface.co/bert/gpt2-medium-merges.txt",
        "gpt2-large": "https://s3.amazonaws.com/models.huggingface.co/bert/gpt2-large-merges.txt",
        "gpt2-xl": "https://s3.amazonaws.com/models.huggingface.co/bert/gpt2-xl-merges.txt",
        "distilgpt2": "https://s3.amazonaws.com/models.huggingface.co/bert/distilgpt2-merges.txt",
    },
}

PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES = {
    "gpt2": 1024,
    "gpt2-medium": 1024,
    "gpt2-large": 1024,
    "gpt2-xl": 1024,
    "distilgpt2": 1024,
}


class GPT2TokenizerFast(PreTrainedTokenizerFast):
    """
    Constructs a "Fast" GPT-2 BPE tokenizer (backed by HuggingFace's `tokenizers` library), using byte-level
    Byte-Pair-Encoding.

    This tokenizer has been trained to treat spaces like parts of the tokens (a bit like sentencepiece) so a word will
    be encoded differently whether it is at the beginning of the sentence (without space) or not:

    ::

        >>> from transformers import GPT2TokenizerFast
        >>> tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        >>> tokenizer("Hello world")['input_ids']
        [15496, 995]
        >>> tokenizer(" Hello world")['input_ids']
        [18435, 995]

    You can get around that behavior by passing ``add_prefix_space=True`` when instantiating this tokenizer or when you
    call it on some text, but since the model was not pretrained this way, it might yield a decrease in performance.

    .. note::

        When used with ``is_pretokenized=True``, this tokenizer needs to be instantiated with
        ``add_prefix_space=True``.

    This tokenizer inherits from :class:`~transformers.PreTrainedTokenizer` which contains most of the methods. Users
    should refer to the superclass for more information regarding methods.

    Args:
        vocab_file (:obj:`str`):
            Path to the vocabulary file.
        merges_file (:obj:`str`):
            Path to the merges file.
        errors (:obj:`str`, `optional`, defaults to "replace"):
            Paradigm to follow when decoding bytes to UTF-8. See `bytes.decode
            <https://docs.python.org/3/library/stdtypes.html#bytes.decode>`__ for more information.
        unk_token (:obj:`string`, `optional`, defaults to `<|endoftext|>`):
            The unknown token. A token that is not in the vocabulary cannot be converted to an ID and is set to be this
            token instead.
        bos_token (:obj:`string`, `optional`, defaults to `<|endoftext|>`):
            The beginning of sequence token.
        eos_token (:obj:`string`, `optional`, defaults to `<|endoftext|>`):
            The end of sequence token.
        add_prefix_space (:obj:`bool`, `optional`, defaults to `False`):
            Whether to add a leading space to the first word.
            This allows to treat the leading word just as any other word.
            (GPT2 tokenizer detect beginning of words by the preceeding space)
        trim_offsets (:obj:`bool`, `optional`, defaults to `True`):
            Whether the post processing step should trim offsets to avoid including whitespaces.
    """

    vocab_files_names = VOCAB_FILES_NAMES
    pretrained_vocab_files_map = PRETRAINED_VOCAB_FILES_MAP
    max_model_input_sizes = PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES
    model_input_names = ["attention_mask"]

    def __init__(
        self,
        vocab_file,
        merges_file,
        unk_token="<|endoftext|>",
        bos_token="<|endoftext|>",
        eos_token="<|endoftext|>",
        add_prefix_space=False,
        trim_offsets=True,
        **kwargs
    ):
        super().__init__(
            ByteLevelBPETokenizer(
                vocab_file=vocab_file,
                merges_file=merges_file,
                add_prefix_space=add_prefix_space,
                trim_offsets=trim_offsets,
            ),
            bos_token=bos_token,
            eos_token=eos_token,
            unk_token=unk_token,
            **kwargs,
        )
        self.add_prefix_space = add_prefix_space

    def _batch_encode_plus(self, *args, **kwargs) -> BatchEncoding:

        is_pretokenized = kwargs.get("is_pretokenized", False)
        assert self.add_prefix_space or not is_pretokenized, (
            f"You need to instantiate {self.__class__.__name__} with add_prefix_space=True "
            "to use it with pretokenized inputs."
        )

        return super()._batch_encode_plus(*args, **kwargs)

    def _encode_plus(self, *args, **kwargs) -> BatchEncoding:

        is_pretokenized = kwargs.get("is_pretokenized", False)
        assert self.add_prefix_space or not is_pretokenized, (
            f"You need to instantiate {self.__class__.__name__} with add_prefix_space=True "
            "to use it with pretokenized inputs."
        )

        return super()._encode_plus(*args, **kwargs)