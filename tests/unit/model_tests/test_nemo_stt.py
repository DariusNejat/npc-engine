"""Similarity test."""
import os
from npc_engine import models
import time
import pytest
import numpy
import scipy.signal
from pydub import AudioSegment
import numpy as np
from pyctcdecode import build_ctcdecoder


@pytest.mark.skip()
def test_sanity_check():
    try:
        stt = models.Model.load(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "npc_engine",
                "resources",
                "models",
                "stt",
            )
        )
    except FileNotFoundError:
        return
    device = input(f"Select device: \n {stt.get_devices()} \n")
    stt.select_device(device)
    stt.initialize_microphone_input()
    while True:
        print("Listening...")
        result = stt.listen("hello how is it going")
        print(f"Result: {result}")


@pytest.mark.skip()
def test_tune_decoder_parameters():
    """Tune decoder parameters.
    
    Requires additional packages:
        - datasets
        - scikit-optimize
        - jiwer
    """
    from datasets import load_dataset
    from skopt import gp_minimize
    from skopt.space import Real
    from jiwer import compute_measures
    import re
    from torch.utils.data import DataLoader
    from tqdm import tqdm

    try:
        stt = models.Model.load(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "npc_engine",
                "resources",
                "models",
                "stt",
            )
        )
    except FileNotFoundError:
        return
    validation_data = load_dataset(
        "librispeech_asr", "clean", cache_dir="D:\\datasets_cache", split="validation"
    )
    alpha_space = Real(low=0.0, high=2.0, prior="uniform", name="alpha")
    beta_space = Real(low=0.0, high=2.0, prior="uniform", name="beta")

    def map_fetch_text_and_audio(data):
        data["processed_audio"] = data["audio"]["array"]
        data["processed_text"] = data["text"]
        return data

    validation_data = validation_data.select(range(700)).map(
        map_fetch_text_and_audio, remove_columns=validation_data.column_names
    )

    data_loader = DataLoader(
        validation_data, batch_size=1, shuffle=False, num_workers=0
    )

    print("Optimizing decoder parameters...")

    def objective(params):

        stt.decoder = build_ctcdecoder(
            stt.asr_vocab,
            kenlm_model_path=os.path.join(
                "npc_engine",
                "resources",
                "models",
                "stt",
                "lowercase_3-gram.pruned.1e-7.arpa",
            ),
            alpha=params[0],  # tuned on a val set
            beta=params[1],  # tuned on a val set
        )
        wer_divident = 0
        wer_divisor = 0
        for batch in tqdm(data_loader):
            audio = batch["processed_audio"]
            text = batch["processed_text"]
            if not stt.predict_punctuation:
                text = [row.lower() for row in text]
            prediction = stt.stt(audio)
            score_dict = compute_measures(text, [prediction])
            wer_divident += (
                score_dict["substitutions"]
                + score_dict["insertions"]
                + score_dict["deletions"]
            )
            wer_divisor += (
                score_dict["hits"]
                + score_dict["substitutions"]
                + score_dict["deletions"]
            )
        print(
            "WER:", float(wer_divident) / float(wer_divisor) if wer_divisor != 0 else 1
        )
        return float(wer_divident) / float(wer_divisor) if wer_divisor != 0 else 1

    result = gp_minimize(
        objective, [alpha_space, beta_space], n_calls=10, n_random_starts=4,
    )
    print(result)

    print(f"Best parameters: {result.x}")
    print(f"Best score: {result.fun}")


@pytest.mark.skipif(
    not os.path.exists(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "npc_engine",
            "resources",
            "models",
            "stt",
            "config.yml",
        )
    ),
    reason="Model missing",
)
def test_transcribe():
    try:
        stt = models.Model.load(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "npc_engine",
                "resources",
                "models",
                "stt",
            )
        )
    except FileNotFoundError:
        return

    audio = AudioSegment.from_file(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "resources", "stt_test.m4a",
        )
    )
    audio = numpy.frombuffer(audio.raw_data, numpy.int16)
    s = scipy.signal.decimate(audio, 6)
    s = s / 32767
    print(s.max())
    print(s.min())
    signal = s.astype(numpy.float32)

    start_trs = time.time()
    result = stt.transcribe(signal)
    result = stt.decode(result)
    assert result == "hello how is it going"
    end_trs = time.time()
    result = stt.postprocess(result)
    print(
        f"Result: {result} with transcription in {end_trs - start_trs} and postprocess in {time.time() - end_trs}"
    )
    assert result == "hello how is it going"


@pytest.mark.skipif(
    not os.path.exists(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "npc_engine",
            "resources",
            "models",
            "stt",
            "config.yml",
        )
    ),
    reason="Model missing",
)
def test_decide_finished():
    try:
        stt = models.Model.load(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "npc_engine",
                "resources",
                "models",
                "stt",
            )
        )
    except FileNotFoundError:
        return

    assert stt.decide_finished("how do you feel", "i feel fine")
    assert not stt.decide_finished("how do you feel", "i feel")
