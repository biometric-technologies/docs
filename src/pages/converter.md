---
title: Biometric Converter
nav: Biometric Converter
desc: Convert fingerprint images to ISO/IEC 19794-2 and ANSI INCITS 378 minutiae templates and between template formats.
---
# Biometric Converter

<p class="lead">Converts fingerprint images into minutiae templates and templates between the ISO and ANSI interchange formats. Built on NIST NBIS (WSQ codec, MINDTCT minutiae detector) and NIST BiomDI (finger minutiae records). Ships as a C library, a command-line tool, a REST service in Docker and a WebAssembly build that runs in the browser.</p>

Typical uses: migrating an AFIS or access-control database from one vendor's format to another, feeding scans from a new sensor into an existing matcher, and auditing what a template file actually contains.

**Try it without installing anything:** the [browser demo](https://www.iriscan.com/biometric-data-interchange#demo) converts files locally on your machine.

## Formats

| Kind | Name | Code |
|---|---|---|
| Image | WSQ (FBI Wavelet Scalar Quantization) | `WSQ` |
| Image | JPEG, JPEG 2000, PNG, NIST IHead | detected automatically |
| Minutiae | ISO/IEC 19794-2:2005 record | `ISO` |
| Minutiae | ISO/IEC 19794-2 normal-size card | `ISONC` |
| Minutiae | ISO/IEC 19794-2 compact card | `ISOCC` |
| Minutiae | ANSI INCITS 378-2004 | `ANSI` |

Conversions:

- image → any minutiae format (MINDTCT extraction);
- `ANSI` ↔ `ISO`, and from `ANSI` to either card format;
- card formats → `ANSI`/`ISO`, given the image resolution (card formats do not store it).

A template cannot be turned back into a fingerprint image: minutiae keep positions, angles and types of ridge endings and bifurcations, not the ridges themselves. To check a template visually, plot its minutiae, as the browser demo does.

Angles are stored in 2° units in ANSI and 360/256° units in ISO, so an ISO → ANSI → ISO round trip can move individual angles by one unit. Coordinates and types are preserved exactly.

## Docker

The quickest way to run the converter.

```sh
# command line
docker run -i --rm -v "$PWD/work:/opt/work" biometrictechnologies/biometric-converter-cli \
  convert -i /opt/work/finger.wsq -ti WSQ -o /opt/work/finger.ist -to ISO

# REST service on port 8080
docker run -d -p 8080:8080 biometrictechnologies/biometric-converter
```

## REST API

Requests and responses are JSON; files travel as base64.

### Convert one file

```http
POST /convert
Content-Type: application/json

{
  "input": "<base64 WSQ>",
  "inputType": "WSQ",
  "outputType": "ISO"
}
```

```json
{ "output": "<base64 ISO/IEC 19794-2 record>" }
```

`imageResX` and `imageResY` (pixels per centimetre) are required only when the input is a card format.

### Convert a batch

```http
POST /convert-batch
Content-Type: application/json

{
  "data": [
    { "id": "subject-17-r-index", "input": "<base64>", "inputType": "WSQ", "outputType": "ANSI" },
    { "id": "subject-17-l-index", "input": "<base64>", "inputType": "WSQ", "outputType": "ANSI" }
  ]
}
```

Files are converted in parallel and the response order is not guaranteed; match results by `id`.

```json
{ "data": [ { "id": "subject-17-l-index", "output": "<base64>" }, … ] }
```

## Command line

```sh
convert -i <input file> -ti <input type> -o <output file> -to <output type>
```

For image input the type is detected from the file header; `-ti` only matters for minutiae input.

## C library

```c
#include <converter.h>

/* image (WSQ, JPEG, JPEG 2000, PNG, IHead) -> minutiae record */
int img2fmr(unsigned char *idata, int ilen, char *otype,
            unsigned char **odata, int *olen);

/* minutiae record -> minutiae record */
int fmr2fmr(unsigned char *idata, int ilen, unsigned char **odata, int *olen,
            char *in_type, char *out_type);

/* same, with the resolution needed for ISO card formats */
int fmr2fmr_iso_card(unsigned char *idata, int ilen, unsigned char **odata, int *olen,
                     char *in_type, char *out_type, int xres, int yres);
```

Output buffers are allocated by the library; free them with `free()`. Build instructions (NBIS and BiomDI first, then CMake) are in the [repository README](https://github.com/biometric-technologies/biometric-converter).

## WebAssembly

The browser build exposes the same pipeline to JavaScript: WSQ decoding and encoding, raw grayscale image → ISO/ANSI template, and ISO ↔ ANSI. Source and build script: [`tools/bdi-wasm`](https://github.com/polyakoff/iriscan.com/tree/main/tools/bdi-wasm). It is 180 KB and needs no server, which makes it suitable for privacy-sensitive tools where biometric files must not leave the operator's machine.

## Enterprise conversion

For large migrations Iriscan runs the converter as a batch pipeline, on-premise or in your cloud, with format auditing (what each record actually contains, including personal data embedded in ANSI/NIST-ITL transactions), progress reporting and verification by re-matching. [Contact us](https://www.iriscan.com/get-started).
