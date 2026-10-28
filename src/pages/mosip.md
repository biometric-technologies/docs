---
title: MOSIP and Inji
nav: MOSIP and Inji
desc: How the Iriscan face match SDK is used in Inji Wallet, the reference wallet of MOSIP.
---
# MOSIP and Inji

<p class="lead">MOSIP is an open-source platform for national ID systems. Inji Wallet is its reference mobile wallet for verifiable credentials. Inji uses the Iriscan Biometric SDK, through the React Native package, as its face match component.</p>

## What it does in Inji

Before a resident shares a credential, either offline over Bluetooth or online by logging in to a relying party, Inji asks for a selfie and compares it with the photo inside the credential. The comparison runs on the phone. No image or template leaves the device, which is what makes offline verification possible and keeps the flow compatible with MOSIP's rules for face SDKs: no personal data or device identifiers in logs or telemetry.

MOSIP's documentation credits the Iriscan team for providing the open-source face match SDK used in the reference integration: [Inji documentation, Face Match](https://github.com/inji/documentation/blob/master/inji-wallet/inji-mobile/technical-overview/integration-guide/building-verifiable-credentials-wallet-with-inji-libraries/face-match.md).

## Integration

Inji depends on `@iriscan/biometric-sdk-react-native` and configures it at startup with a FaceNet model (160×160 input, 512-value embedding), the model's checksum and a distance threshold of 1.0:

```js
import { configure, faceCompare } from '@iriscan/biometric-sdk-react-native';

await configure({
  withFace: {
    encoder: {
      tfModel: {
        path: FACE_SDK_MODEL_PATH,
        inputWidth: 160, inputHeight: 160, outputLength: 512,
        modelChecksum: FACE_SDK_MODEL_CHECKSUM,
      },
    },
    matcher: { threshold: 1 },
  },
});

const verified = await faceCompare(selfieBase64, credentialPhotoBase64);
```

The model path and checksum come from the wallet's build configuration, so a deployment can ship its own model without touching the code. See [Biometric SDK → React Native](sdk.html#react-native) for the full API, including liveness.

## For implementers

Wallet providers and country integrators building on Inji can use the SDK as is, swap in a model trained on their own population, or add liveness and head-pose challenges, which the SDK already exposes. Iriscan provides model retraining and evaluation on representative data, tuning of thresholds for a target false-accept rate, and integration support: [info@iriscan.net](mailto:info@iriscan.net).
