import argparse
import os
import re
import numpy as np
from hparams import hparams, hparams_debug_string
from synthesizer import Synthesizer
from util import audio

sentences = [
  # 장기하와 얼굴들 ㅋ 가사:
#   '친구야 뜨신 거 먹으면 좀 내려갈 거신디.',
#   '아 말이 그렇다는 기지 말이',
#   '하느님의 빛과 어둠을 나노서',
#   '한 주간의 소식을 전해드리는 리포터유',
#   '엄마 눈에는 아이보이겠지만 아가 이기적이구 편협한데'
#   '정성스럽게 적었던 거야.',
    '이모티콘 하나마저 조심스럽게 정했어.',
    # '하나님이 그들에게 복을 주시니',
    '네가 그의 날개 아래에 피하리로다.',
    '그의 진실함은 방패와 손 방패가 되시나니',

    '모든 걸 마무리해버렸어.',
#   '나는 큰 결심을 하고서 보낸 문잔데.',
#   # 장기하와 얼굴들 새해복 가사:
#   '완전히 쾅 닫힌 대화창뿐이네.',
#   '새해복 많이 많으세요.',
#   '새해 복만으로는 안돼.',
#   '너가 잘해야지'
]


def get_output_base_path(checkpoint_path):
    base_dir = os.path.dirname(checkpoint_path)
    m = re.compile(r'.*?\.ckpt\-([0-9]+)').match(checkpoint_path)
    name = 'eval-%d' % int(m.group(1)) if m else 'eval'
    return os.path.join(base_dir, name)


def run_eval(args):
    print(hparams_debug_string())
    reference_mel = None
    synth = Synthesizer()
    synth.load(args.checkpoint, args.reference_audio)

    if args.reference_audio is not None:
        ref_wav = audio.load_wav(args.reference_audio)
        reference_mel = audio.melspectrogram(ref_wav).astype(np.float32).T

    base_path = get_output_base_path(args.checkpoint)

    for i, text in enumerate(sentences):
        path = '%s_%d_%.1f_%d.wav' % (base_path+'_gst', hparams.gst_index, hparams.gst_scale, i)
        print('Synthesizing: %s' % path)
        with open(path, 'wb') as f:
            f.write(synth.synthesize(text, reference_mel=reference_mel))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', required=True, help='Path to model checkpoint')
    parser.add_argument('--hparams', default='',
        help='Hyperparameter overrides as a comma-separated list of name=value pairs')
    parser.add_argument('--gpu', default='1')
    parser.add_argument('--reference_audio', default=None, help='Reference audio path')
    args = parser.parse_args()
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    hparams.parse(args.hparams)
    run_eval(args)


if __name__ == '__main__':
  main()
