---
title: Cloud Iris API
nav: Cloud Iris API
desc: REST API for iris enrolment, 1:N identification and 1:1 verification.
---
# Cloud Iris API

<p class="lead">Iris recognition as a REST service. Enrol a person with left and right eye images, then find them among everyone enrolled (1:N) or confirm a claimed identity (1:1). Each customer is a tenant with its own isolated database.</p>

Base URL:

```
https://api.iriscan.net
```

## Authentication

Every request carries the tenant's API key in the `Api-Key` header.

```sh
curl https://api.iriscan.net/persons/query?page=0&pageSize=20 \
  -H "Api-Key: $IRISCAN_API_KEY"
```

API keys are issued per tenant together with the monthly plan. To get one, [contact us](https://www.iriscan.com/get-started) with the expected number of enrolments and identifications per month; on-premise deployment with the [Edge service](edge.html) is arranged the same way.

## How matching works

When a person is enrolled, each eye image is segmented, the iris ring is unwrapped and encoded into a binary iris code with a mask of unusable bits (eyelids, lashes, reflections). The response returns both, plus `blackPercentage`, the share of the iris hidden by occlusion. A high value means too little texture was visible, and the image is worth retaking.

`find` compares a probe eye against every enrolled template of the tenant and returns the best match, or `404` when nobody matches. `verify` compares the probe only against the given person and returns `412` when it does not match. Images are sent as base64 strings; near-infrared images from dedicated iris scanners give the best results.

## Errors

| Status | Meaning |
|---|---|
| `400` | Malformed request or image |
| `401` | Missing or invalid `Api-Key` |
| `404` | Person not found, or no match for `find` |
| `412` | `verify`: the eye does not match the person |
| `422` | Validation failed; `errors` lists the fields |

Error bodies have the same shape:

```json
{
  "timestamp": "2021-03-02T10:15:30Z",
  "status": "UNPROCESSABLE_ENTITY",
  "message": "Validation failed",
  "errors": ["name: must not be blank"]
}
```

## Reference

{{REFERENCE}}
