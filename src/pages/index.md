---
title: Iriscan developer documentation
nav: Overview
desc: Documentation for the Iriscan Biometric SDK, Biometric Converter, Cloud Iris API and Edge service.
---
# Iriscan developer documentation

<p class="lead">Iriscan builds biometric components that you can run on your own infrastructure: face, liveness and iris recognition for mobile and server, fingerprint template conversion between ISO and ANSI formats, and a REST service for iris enrolment and matching. The core libraries are open source.</p>

<div class="cards">
<a class="card" href="sdk.html"><h3>Biometric SDK</h3><p>Face detection, FaceNet templates, liveness and iris recognition on Android, iOS, JVM and React Native. Runs on the device, no server required.</p><span class="tag">Open source · Kotlin Multiplatform</span></a>
<a class="card" href="converter.html"><h3>Biometric Converter</h3><p>Fingerprint images (WSQ, PNG, JPEG, JPEG 2000) to minutiae templates and templates between ISO/IEC 19794-2 and ANSI INCITS 378.</p><span class="tag">Open source · C · REST · WebAssembly</span></a>
<a class="card" href="cloud-api.html"><h3>Cloud Iris API</h3><p>Enrol people with left and right eye images, identify them 1:N or verify 1:1 over REST. Each tenant gets an isolated database.</p><span class="tag">REST · API key</span></a>
<a class="card" href="edge.html"><h3>Edge service</h3><p>A local service for Iritech iris scanners and webcams: capture, quality score, live preview and an encrypted local person store that syncs with the cloud.</p><span class="tag">Windows · Linux</span></a>
<a class="card" href="mosip.html"><h3>MOSIP and Inji</h3><p>The face match SDK used by Inji Wallet, the reference wallet of the MOSIP national ID platform, for offline selfie verification.</p><span class="tag">Integration</span></a>
</div>

## Where things live

| Component | Package | Source |
|---|---|---|
| Biometric SDK, Android | `net.iriscan:biometric-sdk-android` (Maven Central) | [biometric-sdk](https://github.com/biometric-technologies/biometric-sdk) |
| Biometric SDK, JVM | `net.iriscan:biometric-sdk-jvm` (Maven Central) | same |
| Biometric SDK, iOS | `BiometricSdk` (CocoaPods) | same |
| React Native wrapper | `@iriscan/biometric-sdk-react-native` (npm) | [biometric-sdk-react-native](https://github.com/biometric-technologies/biometric-sdk-react-native) |
| Biometric Converter | `biometrictechnologies/biometric-converter` (Docker Hub) | [biometric-converter](https://github.com/biometric-technologies/biometric-converter) |
| Liveness model | `deePix.tflite` release asset | [liveness-detection-model](https://github.com/biometric-technologies/liveness-detection-model) |

## Support

Bug reports and feature requests go to the issue tracker of the relevant repository. For production deployments, custom model training, integration work and support contracts, write to [info@iriscan.net](mailto:info@iriscan.net).
