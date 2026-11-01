#!/usr/bin/env python3
"""Regenerates pages/sdk.md from the biometric-sdk README, the single source of the SDK documentation.

    python3 src/sync_sdk.py path/to/biometric-sdk/readme.md

Drops what only makes sense on GitHub (banner, badges, table of contents), turns links to files in
the SDK repository into GitHub links, rewrites in-page anchors to the slugs this site generates, and
keeps the React Native section, which documents a separate repository.
"""
import re
import sys
import os

SRC = os.path.dirname(os.path.abspath(__file__))
REPO = 'https://github.com/biometric-technologies/biometric-sdk'
RAW = 'https://raw.githubusercontent.com/biometric-technologies/biometric-sdk/master/'

FRONT = '''---
title: Biometric SDK
nav: Biometric SDK
desc: Open-source iris, face and liveness recognition for Android, iOS and the JVM, in Kotlin Multiplatform.
---
'''

REACT_NATIVE = '''## React Native

The [React Native wrapper](https://github.com/biometric-technologies/biometric-sdk-react-native)
exposes face match and liveness. It uses native modules and does not work in Expo Go; use a
development build.

```sh
npm install @iriscan/biometric-sdk-react-native
cd ios && pod install
```

```js
import {
  configure, faceCompare, faceScore,
  livenessScore, livenessValidate, livenessGetDirection,
} from '@iriscan/biometric-sdk-react-native';

await configure({
  withFace: {
    encoder: {
      tfModel: {
        path: 'https://github.com/biometric-technologies/tensorflow-facenet-model-test/raw/master/model.tflite',
        inputWidth: 160, inputHeight: 160, outputLength: 512,
      },
    },
    matcher: { threshold: 1.0 },
    liveness: {
      tfModel: {
        path: 'https://github.com/biometric-technologies/liveness-detection-model/releases/download/v0.2.0/deePix.tflite',
        inputWidth: 224, inputHeight: 224, threshold: 0.5,
      },
    },
  },
});

// images are base64 strings
const same = await faceCompare(selfieBase64, documentPhotoBase64);
const distance = await faceScore(selfieBase64, documentPhotoBase64);
const live = await livenessValidate(selfieBase64);
const direction = await livenessGetDirection(frameBase64); // 'STRAIGHT' | 'LEFT' | 'RIGHT' | 'UP' | 'DOWN'
```

This is the same API Inji Wallet calls for offline face verification; see [MOSIP and Inji](mosip.html).

'''


def site_slug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')


def github_slug(t):
    a = re.sub(r'[^\w\- ]', '', t.strip().lower())
    return a.replace(' ', '-')


def convert(readme):
    text = readme
    # GitHub-only header: banner, badges and the table of contents (the site has a sidebar)
    title = text.index('# Biometric SDK')
    text = text[title:]
    text = re.sub(r'(?m)^!\[[^\]]*\]\(https://github\.com/[^)]*badge\.svg\)\s*\n', '', text)
    text = re.sub(r'(?m)^\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)\s*\n', '', text)
    text = re.sub(r'(?ms)^## Contents\n.*?(?=^## )', '', text)

    # in-page anchors: GitHub slugs -> slugs of this site
    headings = re.findall(r'(?m)^#{2,4} (.+)$', text)
    mapping = {github_slug(h): site_slug(h) for h in headings}
    text = re.sub(r'\]\(#([^)]+)\)', lambda m: '](#' + mapping.get(m.group(1), m.group(1)) + ')', text)

    # files of the SDK repository: images from raw.githubusercontent, other files on GitHub
    def repo_link(m):
        bang, label, target = m.group(1), m.group(2), m.group(3)
        if re.match(r'(https?:|mailto:|#)', target):
            return m.group(0)
        target = re.sub(r'^\./', '', target)
        if bang:
            return f'![{label}]({RAW}{target})'
        if target.lower() in ('readme.md',):
            return f'[{label}]({REPO})'
        return f'[{label}]({REPO}/blob/master/{target})'
    text = re.sub(r'(!?)\[([^\]]*)\]\(([^)\s]+)\)', repo_link, text)

    # React Native goes before "Where it is used"
    text = text.replace('## Where it is used', REACT_NATIVE + '## Where it is used', 1)
    return FRONT + text


if __name__ == '__main__':
    readme = open(sys.argv[1], encoding='utf-8').read()
    out = os.path.join(SRC, 'pages', 'sdk.md')
    open(out, 'w', encoding='utf-8').write(convert(readme))
    print('wrote', out)
