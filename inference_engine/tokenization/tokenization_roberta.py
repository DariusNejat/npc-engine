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
"""Tokenization classes for RoBERTa."""

import warnings
from typing import List, Optional

from tokenizers.processors import RobertaProcessing

from .tokenization_gpt2 import GPT2TokenizerFast
from .tokenization_utils_base import AddedToken
import logging

logger = logging.getLogger(__name__)

VOCAB_FILES_NAMES = {
    "vocab_file": "vocab.json",
    "merges_file": "merges.txt",
}

PRETRAINED_VOCAB_FILES_MAP = {
    "vocab_file": {
        "roberta-base": "https://s3.amazonaws.com/models.huggingface.co/bert/roberta-base-vocab.json",
        "roberta-large": "https://s3.amazonaws.com/models.huggingface.co/bert/roberta-large-vocab.json",
        "roberta-large-mnli": "https://s3.amazonaws.com/models.huggingface.co/bert/roberta-large-mnli-vocab.json",
        "distilroberta-base": "https://s3.amazonaws.com/models.huggingface.co/bert/distilroberta-base-vocab.json",
        "roberta-base-openai-detector": "https://s3.amazonaws.com/models.huggingface.co/bert/roberta-base-vocab.json",
        "roberta-large-openai-detector": "https://s3.amazonaws.com/models.huggingface.co/bert/roberta-large-vocab.json",
    },
    "merges_file": {
        "roberta-base": "https://s3.amazonaws.com/models.huggingface.co/bert/roberta-base-merges.txt",
        "roberta-large": "https://s3.amazonaws.com/models.huggingface.co/bert/roberta-large-merges.txt",
        "roberta-large-mnli": "https://s3.amazonaws.com/models.huggingface.co/bert/roberta-large-mnli-merges.txt",
        "distilroberta-base": "https://s3.amazonaws.com/models.huggingface.co/bert/distilroberta-base-merges.txt",
        "roberta-base-openai-detector": "https://s3.amazonaws.com/models.huggingface.co/bert/roberta-base-merges.txt",
        "roberta-large-openai-detector": "https://s3.amazonaws.com/models.huggingface.co/bert/roberta-large-merges.txt",
    },
}

PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES = {
    "roberta-base": 512,
    "roberta-large": 512,
    "roberta-large-mnli": 512,
    "distilroberta-base": 512,
    "roberta-base-openai-detector": 512,
    "roberta-large-openai-detector": 512,
}


class RobertaTokenizerFast(GPT2TokenizerFast):
    """
    Constructs a "Fast" RoBERTa BPE tokenizer (backed by HuggingFace's `tokenizers` library), derived from the GPT-2
    tokenizer, using byte-level Byte-Pair-Encoding.

    This tokenizer has been trained to treat spaces like parts of the tokens (a bit like sentencepiece) so a word will
    be encoded differently whether it is at the beginning of the sentence (without space) or not:

    ::

        >>> from transformers import RobertaTokenizerFast
        >>> tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")
        >>> tokenizer("Hello world")['input_ids']
        [0, 31414, 232, 328, 2]
        >>> tokenizer(" Hello world")['input_ids']
        [0, 20920, 232, 2]

    You can get around that behavior by passing ``add_prefix_space=True`` when instantiating this tokenizer or when you
    call it on some text, but since the model was not pretrained this way, it might yield a decrease in performance.

    .. note::

        When used with ``is_split_into_words=True``, this tokenizer needs to be instantiated with
        ``add_prefix_space=True``.

    This tokenizer inherits from :class:`~transformers.PreTrainedTokenizerFast` which contains most of the methods. Users
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
        errors="replace",
        bos_token="<s>",
        eos_token="</s>",
        sep_token="</s>",
        cls_token="<s>",
        unk_token="<unk>",
        pad_token="<pad>",
        mask_token="<mask>",
        add_prefix_space=False,
        trim_offsets=True,
        **kwargs
    ):
        # Mask token behave like a normal word, i.e. include the space before it
        mask_token = AddedToken(mask_token, lstrip=True, rstrip=False) if isinstance(mask_token, str) else mask_token

        kwargs.setdefault("pad_token", pad_token)
        kwargs.setdefault("sep_token", sep_token)
        kwargs.setdefault("cls_token", cls_token)
        kwargs.setdefault("mask_token", mask_token)

        super().__init__(
            vocab_file=vocab_file,
            merges_file=merges_file,
            unk_token=unk_token,
            bos_token=bos_token,
            eos_token=eos_token,
            add_prefix_space=add_prefix_space,
            trim_offsets=trim_offsets,
            **kwargs,
        )

        # This will add the necessary special tokens to the vocabulary if needed
        self.sanitize_special_tokens()

        self.backend_tokenizer._tokenizer.post_processor = RobertaProcessing(
            sep=(sep_token, self.sep_token_id),
            cls=(cls_token, self.cls_token_id),
            add_prefix_space=add_prefix_space,
            trim_offsets=trim_offsets,
        )

    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        output = [self.bos_token_id] + token_ids_0 + [self.eos_token_id]
        if token_ids_1 is None:
            return output

        return output + [self.eos_token_id] + token_ids_1 + [self.eos_token_id]

    def create_token_type_ids_from_sequences(
        self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None
    ) -> List[int]:
        """
        Creates a mask from the two sequences passed to be used in a sequence-pair classification task.
        RoBERTa does not make use of token type ids, therefore a list of zeros is returned.

        Args:
            token_ids_0 (:obj:`List[int]`):
                List of ids.
            token_ids_1 (:obj:`List[int]`, `optional`):
                Optional second list of IDs for sequence pairs.

        Returns:
            :obj:`List[int]`: List of zeros.

        """
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]

        if token_ids_1 is None:
            return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep + sep + token_ids_1 + sep) * [0]