from h2o_wave import ui
import torch
from transformers import Wav2Vec2Model, Wav2Vec2Processor
from transformers.pipelines.audio_utils import ffmpeg_read


def get_inline_script(text: str) -> ui.InlineScript:
    """
    Get Wave's Inline Script.
    """

    return ui.inline_script(text)


def generate_transcription(audio_path: str, model: Wav2Vec2Model, processor: Wav2Vec2Processor) -> str:
    """
    Generate transcription from audio file.
    """

    with open(audio_path, 'rb') as f:
        audio_file = f.read()

    audio_input = ffmpeg_read(bpayload=audio_file, sampling_rate=16000)
    audio_input_values = processor(audio_input, return_tensors='pt').input_values

    with torch.no_grad():
        logits = model(audio_input_values).logits

    predicted_ids = torch.argmax(logits, dim=-1)

    return processor.batch_decode(predicted_ids)[0]
