---
title: Biometric SDK
nav: Biometric SDK
desc: Face, liveness and iris recognition SDK for Android, iOS, JVM and React Native.
---
# Biometric SDK

<p class="lead">A Kotlin Multiplatform library for face and iris recognition that runs entirely on the device. One API across Android, iOS and the JVM, plus a React Native wrapper.</p>

What it does today:

- **Face**: detects the face (ML Kit on Android, Apple Vision on iOS, OpenCV on the JVM), aligns it by the eyes and turns it into a FaceNet embedding. Two embeddings are compared by Euclidean distance.
- **Liveness**: a TensorFlow Lite model scores a photo as real or spoof (printed photo, screen replay), and head pose from Euler angles supports challenge–response checks such as "turn left".
- **Iris**: locates pupil and iris boundaries, unwraps the iris texture and encodes it into a binary template. Templates are compared by the share of matching bits.
- **Records**: reads and writes ISO/IEC 19794-6 iris records and ISO/IEC 19794-2 finger minutiae records, plus PNG, BMP and JPEG images.

Models are loaded from a URL or from the app bundle, cached on the device and optionally verified by checksum, so you can ship your own retrained model without changing code.

## Installation

### Android

```kotlin
dependencies {
    implementation("net.iriscan:biometric-sdk-android:0.6.0")
}
```

Minimum Android API level is 23. TensorFlow Lite 2.12 and ML Kit face detection come as transitive dependencies.

### JVM

```kotlin
dependencies {
    implementation("net.iriscan:biometric-sdk-jvm:0.6.0")
}
```

The JVM build uses TensorFlow Lite through JavaCPP and OpenCV for face detection, so it runs on Linux, macOS and Windows servers.

### iOS

```ruby
pod 'BiometricSdk', '0.6.0'
```

### React Native

```sh
npm install @iriscan/biometric-sdk-react-native
cd ios && pod install
```

The package uses native modules and does not work in Expo Go; use a development build.

## Initialization

Initialize the SDK once, before any other call. Only the modules you configure are loaded.

```kotlin
val sdk = BiometricSdkFactory

sdk.initialize(
    sdk.configBuilder()
        .withContext(applicationContext)            // Android only
        .withFace(
            extractor = FaceExtractProperties(),
            encoder = FaceEncodeProperties(
                FaceNetModelConfiguration(
                    path = "https://github.com/biometric-technologies/tensorflow-facenet-model-test/raw/master/model.tflite",
                    inputWidth = 160,
                    inputHeight = 160,
                    outputLength = 512,
                ),
            ),
            matcher = FaceMatchProperties(threshold = 1.0),
            liveness = FaceLivenessDetectionProperties(
                photo = LivenessModelPhotoConfiguration(
                    path = "https://github.com/biometric-technologies/liveness-detection-model/releases/download/v0.2.0/deePix.tflite",
                    inputWidth = 224,
                    inputHeight = 224,
                    threshold = 0.5,
                ),
                position = LivenessModelPositionConfiguration(threshold = 15.0),
            ),
        )
        .withIris(IrisExtractProperties(), IrisEncodeProperties(), IrisMatchProperties())
        .build()
)

val ops = sdk.getInstance()!!
```

`initialize` downloads the models on first run and caches them; later starts read from the cache. To pin a model, pass `modelChecksum` and `modelChecksumMethod` in the model configuration. With `overrideCacheOnWrongChecksum = true` a cached file that fails the check is downloaded again.

Platform image types differ: `NativeImage` is `Bitmap` on Android, `CGImage` on iOS and `BufferedImage` on the JVM. `DataBytes` is `ByteArray` on Android and the JVM and `NSData` on iOS.

## Face recognition

```kotlin
val photo = ops.io().readNativeImage(photoBytes)
val selfie = ops.io().readNativeImage(selfieBytes)

val t1 = ops.face().encoder().extractAndEncode(photo) ?: error("no face on the photo")
val t2 = ops.face().encoder().extractAndEncode(selfie) ?: error("no face on the selfie")

val distance = ops.face().matcher().matchScore(t1, t2)   // lower means more similar
val samePerson = ops.face().matcher().matches(t1, t2)    // distance <= threshold
```

`extractAndEncode` returns `null` when no face is found or the eyes cannot be located. If you already have a cropped, aligned face, call `encoder().encode(image)` directly.

For 1:N search against a few enrolled templates, `matchesAny` and `matchScoreMin` take the minimum distance across a list. For large galleries, store the templates server-side and index them; the embedding is a plain float vector (big-endian, 4 bytes per value).

The threshold depends on the model. With the FaceNet model above, a distance around 1.0 is a reasonable starting point; tune it on your own data for the false-accept rate you need.

## Liveness

```kotlin
val spoofScore = ops.face().livenessPhoto().extractAndScore(selfie)  // 0.0 real … 1.0 spoof
val isLive = ops.face().livenessPhoto().extractAndValidate(selfie)   // score below threshold

val pose = ops.face().livenessPosition().detectPosition(selfie)
// 0 straight, 1 left, 2 right, 3 up, 4 down
```

The photo check catches prints and screen replays on a single frame. For higher assurance, combine it with a random head-turn challenge using `detectPosition` across consecutive frames. The model is MobileNetV2 trained on a CelebA-based spoofing dataset; the training code is in [liveness-detection-model](https://github.com/biometric-technologies/liveness-detection-model) if you want to retrain it on your capture conditions.

## Iris recognition

```kotlin
val eye1 = ops.io().readImage(eyeImageBytes1)   // near-infrared eye image, PNG/BMP/JPEG
val eye2 = ops.io().readImage(eyeImageBytes2)

val t1 = ops.iris().encoder().extractAndEncode(eye1) ?: error("iris not found")
val t2 = ops.iris().encoder().extractAndEncode(eye2) ?: error("iris not found")

val same = ops.iris().matcher().matches(t1, t2)  // share of equal bits >= threshold (0.7)
```

The extractor searches for the pupil and iris circles and unwraps the ring into a rectangular texture; `IrisExtractProperties` exposes the search ranges and step sizes if your images are unusually framed. `IrisEncodeProperties` sets the template size. Eye images from dedicated NIR scanners such as IriShield work best.

ISO/IEC 19794-6 records go through the same calls:

```kotlin
val record = ops.io().readRecord(isoBytes)               // BiometricRecord
val encoded = ops.iris().encoder().encode(record)
val isoOut = ops.io().writeRecord(encoded)
```

## React Native

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

## Versions

The current release is 0.6.0. Release notes and binaries are on the [GitHub releases page](https://github.com/biometric-technologies/biometric-sdk/releases). The SDK is licensed under GPL-3.0. For licensing questions, write to [info@iriscan.net](mailto:info@iriscan.net).
