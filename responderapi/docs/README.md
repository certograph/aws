Responder API -- mocking and testing APIs in the cloud
======================================================

* **ResponderAPI** is a zero-configuration mock HTTP server designed to make it easy to implement test APIs.
* **ResponderAPI** is available as a Docker container and is meant to run in **AWS Elastic Container Service (ECS)** 
clusters using **AWS EC2** or **AWS Fargate** hosts.

## Security and Data Safety

> **ResponderAPI** does not write to the local filesystem of the host. The only external calls made by **ResponderAPI**
> are to the AWS API to verify entitlement (presence of **AWS Marketplace** subscription) and register usage (time). 
> **ResponderAPI** does not store or share with any third-party any part of the data received or returned. All 
> **ResponderAPI** logs are sent to the **AWS CloudWatch** log groups in the same AWS account that **ResponderAPI** runs 
> in. 

## Deploying ResponderAPI

**ResponderAPI** is available from **AWS Marketplace**. Click here to add it to your organisation's own **AWS 
Marketplace Catalog**.

> Please note that while the **AWS Marketplace** website mentions *subscription* **ResponderAPI** pricing is based on 
> usage--the time an instance of the **ResponderAPI** container runs in your account.

Once you confirm your **AWS Marketplace** subscription, **ResponderAPI** container will be added to your AWS account's 
Marketplace and can be deployed into an **AWS ECS** cluster. Click [here](ECS.md) for instructions.

## Usage

**Responder API** is ready to use immediately after a successful deployment. You can test **ResponderAPI** using `curl` 
or any other HTTP client or HTTP test tool. It is as simple as:

```bash
$ curl -vvv 'remotehost:8080/'
```
> **NOTE:** You will see `remotehost:8080` used throughout this document. Replace `remotehost` with the public hostname
> of the **ResponderAPI** service running in your cluster.

The response you will get will look similar to this:

```json
{
  "protocol": "HTTP/1.1",
  "method": "GET",
  "user_agent": "curl/8.4.0",
  "client_address": "[::1]:64167",
  "host": "remotehost:8080",
  "url_path": "/",
  "content_type": "",
  "content_length": 0,
  "request_body": "",
  "found_headers": null,
  "params": {
    "random_delay": {}
  },
  "responderapi_id": "936a3c26-6e31-11ef-bde8-1ec32bd4abd5",
  "called_at": "2024-09-08T22:27:47.744046Z",
  "execution_time": "11µs"
}
```

> If you have trouble reading the JSON payload returned by **ResponderAPI**, copy and paste it into https://jsonlint.com
> and click **Validate** or install [jq](https://jqlang.github.io/jq/) and append ` | jq .` to the `curl` commands shown in this document, e.g.
> `$ curl -vvv 'remotehost:8080/' | jq .`

**ResponderAPI** will process each request in the following way:

1. Echo all requests in the response payload unless one of `body` or `no_body` query params is set in the request query params.
2. Log all responses to requests, even if the `no_body` request query param is set.

## Usage

You can modify responses returned by **ResponderAPI** using request query parameters as described in the following 
sections of this manual.

### `delay` -- delaying response by *N* milliseconds

**ResponderAPI** is quick. It will respond within a few milliseconds of receiving a request, but there are situations 
when you want to test what happens when there are delays. Such delays could be caused by misconfiguration of DNS, CDN, 
routing, proxies, firewalls or load balancers to name just a few possible points of failure. Forcing delays deliberately 
helps you discover those issues earlier.

```bash
$ curl -vvv 'remotehost:8080/fff?delay=3000'
```

> Please note that **ResponderAPI** will log the request before delaying response. This is to allow you to capture 
your request and its interpretation by **ResponderAPI** in case the request times out and you never see the response,
or when you request a response with an empty body using the `no_body` request query parameter. 

The response will return the delay value in the `params` object:

```json
{
  ...
  "url_path": "/?delay=3000",
  ...
  "params": {
    "delay": 300,
    ...
  },
  ...
  "called_at": "2024-09-08T22:38:55.504581Z",
  "execution_time": "300.017ms"
}
```

### `random_delay` -- delaying response by *N* to *M* milliseconds

If you want to introduce randomness into tests involving delaying response from **ResponderAPI**, use the `random_delay` 
param to set the range of delay times in milliseconds. For example, if you wanted to introduce random delay between
a quarter of a second a full second, you'd use the following notation. If you omit the first value it will be assumed
to be zero (no delay).

```bash
$ curl -vvv 'remotehost:8080/fff?random_delay=250,1000'
```

The output will look like this

```json
{
  ...,
  "url_path": "/?random_delay=200,300",
  ...
  "params": {
    "random_delay": {
      "min": 200,
      "max": 300
    }
  },
  ...
  "called_at": "2024-09-08T22:49:27.741989Z",
  "execution_time": "279.025ms"
}
```

If one of the two value of `random_delay` is missing, it is assumed to be equal to zero (no delay). E.g. the following
request set delay to a random number between 0 and 1 second:

```bash
$ curl -vvv 'remotehost:8080/fff?random_delay=,1000'
```

or

```bash
$ curl -vvv 'remotehost:8080/fff?random_delay=1000'
```

### `body` -- returning custom body

Unless instructed otherwise, ResponderAPI will return a JSON response object. If it is not what you want, you can 
instruct it to return a custom payload with the `body` query parameter. For example, if you wanted **ResponderAPI** to
respond with `"response body"`, try

```bash
$ curl -vvv 'remotehost:8080/fff?body=InJlc3BvbnNlIGJvZHki'
```

You can see the response body in the logged output:

```json
{
  ... 
  "url_path": "/fff?body=InJlc3BvbnNlIGJvZHki",
  ...
  "params": {
    ...
    "body": "InJlc3BvbnNlIGJvZHki"
  },
  ...
  "called_at": "2024-09-08T23:05:14.487961Z",
  "execution_time": "17µs"
}
```

The value of the `body` query param is encoded using base64 encoding to avoid issues with query string parsing. You can
do it programmatically, or using an online tool like [base64encode](https://www.base64encode.org/).

> If you want to change the default value of the `Content-Type` header to match the type of the content returned in the 
> response body, set it in the `headers` query param (see further down on this page).

### `no_body` -- returning empty body

Unless instructed otherwise, **ResponderAPI** returns a response with a JSON body containing diagnostic information 
about the request to allow you to debug your infrastructure setup, code, and tests. What if you wanted to hide that 
response?  The `no_body` request query parameter instructs **ResponderAPI** to return an empty body with 
`Content-Length: 0`. Try it for yourself:

```bash
$ curl -vvv 'remotehost:8080/fff?no_body'
```

> Please note that `no_body` will override the `body` request query parameter, if one is present in the request query
string.

### `status_code` -- returning custom HTTP status code

**ResponderAPI** returns the default `200 OK` response status code to any request sent to it. You can override response
status code with the `status_code` request query parameter. For example, `status_code=500` will instruct **ResponderAPI**
to return a `500 Internal Server Error` response status code.

```bash
$ curl -vvv 'remotehost:8080/fff?status_code=500'
```

What happens when you send an invalid HTTP status code to **ResponderAPI**? It will respond with a `400 Bad Request` 
response status code. Try it for yourself:

```bash
$ curl -vvv 'remotehost:8080/fff?status_code=290a'
```

### `headers` -- setting response headers 

**ResponderAPI** can return custom response headers. This feature is particularly useful when you want the 
value of the `Content-Type` header to match the type of the response body. Let's say you want to set it to
`Content-Type: application/whatever`. You need to base64 encode it, like this:

```bash
$ curl -vvv 'remotehost:8080?headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi93aGF0ZXZlcg=='
```

The response body returned by **ResponderAPI** will contain the following entries.

```json
{
  ...
  "url_path": "/?headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi93aGF0ZXZlcg==",
  ...
  "params": {
    ...
    "headers": [
      "Content-Type: application/whatever"
    ]
  },
  "called_at": "2024-09-09T10:01:56.766208Z",
  "execution_time": "26µs"
}
```

The response headers will contain the following:

```text
HTTP/1.1 200 OK
Content-Type: application/whatever
Date: Mon, 09 Sep 2024 10:01:56 GMT
Content-Length: 471
```

It is possible to set more than one header as long as you base64 encode them separately and separate them with commas:

```bash
$ curl -vvv 'remotehost:8080?headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi93aGF0ZXZlcg==,QWxsb3c6IE9QVElPTlMsIEdFVCwgSEVBRCwgUE9TVA==,Q2FjaGUtQ29udHJvbDogbWF4LWFnZT02MDQ4MDA=,U2VydmVyOiBSZXNwb25kZXJBUEkgMjAyNC0wMDM='
```

The headers passed in the `header` param will be listed in the response payload:

```json
{
  ...
  "url_path": "/?headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi93aGF0ZXZlcg==,QWxsb3c6IE9QVElPTlMsIEdFVCwgSEVBRCwgUE9TVA==,Q2FjaGUtQ29udHJvbDogbWF4LWFnZT02MDQ4MDA=,U2VydmVyOiBSZXNwb25kZXJBUEkgMjAyNC0wMDM=",
  ...
  "params": {
   ...
    "headers": [
      "Content-Type: application/whatever",
      "Allow: OPTIONS, GET, HEAD, POST",
      "Cache-Control: max-age=604800",
      "Server: ResponderAPI 2024-003"
    ]
  },
  ...
  "called_at": "2024-09-09T10:38:15.672904Z",
  "execution_time": "41µs"
}
```

The response headers will be returned as requested:

```text
HTTP/1.1 200 OK
Allow: OPTIONS, GET, HEAD, POST
Cache-Control: max-age=604800
Content-Type: application/whatever
Server: ResponderAPI 2024-003
Date: Mon, 09 Sep 2024 10:38:15 GMT
Content-Length: 695
```

### `expected_headers` - checking for request headers

If you want verify that certain headers are/are not being removed or modified 
You can list headers that you want to make sure 

request_headers


### `headers` vs. `expected_headers` -- the difference between request and response headers

The `headers` query param defines *response* headers, not *request* headers. These are set up by the HTTP client
when you are configuring your request. Response `headers` are independent of the request headers sent by the client.
When you want to check if headers you are expecting are being passed from the client to **ResponderAPI**, list their 
names in `expected_headers` like in the `curl` command below:

```bash
$ curl -vvv 'remotehost:8080?headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi93aGF0ZXZlcg==&expected_headers=Q29udGVudC1UeXBl,RG8tV2UtQ2FyZQ==' -H 'Content-Type: application/something'
```

Note that the command above sends one header (`Content-Type`), but expects two (`Content-Type`, `Do-We-Care`). Those two 
headers correctly appear in `expected_headers`, but only `Content-Type` appears in `found_headers` as shown below:

```json
{
  ...
  "url_path": "/?headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi93aGF0ZXZlcg==&expected_headers=Q29udGVudC1UeXBl,RG8tV2UtQ2FyZQ==",
  ...
  ... if ResponderAPI finds one or more "expected_headers", they will be listed in "found_headers" ...
  "found_headers": [
    "Content-Type: application/something"
  ],
  "params": {
    ...
    ... "headers" will be returned by ResponderAPI ...
    "headers": [
      "Content-Type: application/whatever"
    ],
    ...
    ... "expected_headers" will be listed in "found_headers" if they are found in the request headers sennt by the client ...
    "expected_headers": [
      "Content-Type",
      "Do-We-Care"
    ]
  },
  ...
  "called_at": "2024-09-09T20:59:52.916018Z",
  "execution_time": "21µs"
}

```

### `no_headers` -- removing (almost) all headers

Sometime you want to test client behaviour when some headers are missing. You can instruct **ResponderAPI** to remove (almost)
all of them with the `no_headers` query param:

```bash
$ curl -vvv 'remotehost:8080?no_headers&no_body'
```

> **ResponderAPI** will include `Date` and `Content-Length` headers.
> If you do not use `no_body` param in the request, you will also see `Content-Type`.


## Response Payload 

**ResponderAPI** returns a JSON payload that contains information about the request it received and the requested 
response. The only time you will not see it is when you use `no_body`, but you can still find the whole payload in the 
logs. The payload looks similar to the one below:

```json
{
  "protocol": "HTTP/1.1",
  "method": "GET",
  "user_agent": "curl/8.4.0",
  "client_address": "[::1]:54782",
  "host": "remotehost:8080",
  "url_path": "/?headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi93aGF0ZXZlcg==&expected_headers=Q29udGVudC1UeXBl,RG8tV2UtQ2FyZQ==",
  "content_type": "application/something",
  "content_length": 0,
  "request_body": "",
  "found_headers": [
    "Content-Type: application/something"
  ],
  "params": {
    "random_delay": {},
    "headers": [
      "Content-Type: application/whatever"
    ],
    "expected_headers": [
      "Content-Type",
      "Do-We-Care"
    ]
  },
  "responderapi_id": "7d946e42-6f46-11ef-ada2-1ec32bd4abd5",
  "called_at": "2024-09-10T07:30:01.704706Z",
  "execution_time": "109µs"
}
```

- `protocol` -- HTTP protocol version, set by the client automatically, unless you specifically override it
- `method` -- HTTP request method, set by the you, e.g. `curl -X POST`;
- `user_agent` -- user agent name and version, set by the client automatically, unless you override it;
- `client_address` -- the IP address or hostname and port number of the client sending the request;
- `host` -- the IP address or hostname and port number of **ResponderAPI** host;
- `url_path` -- the request URL path as sent by the client; if **ResponderAPI** doesn't work as you expected, comparing
this URL path with the values of `params` and `found_headers` may provide clues
- `content_type` -- the value of the request `Content-Type` header provided by the client; while you could achieve the 
same result using `expected_headers`, `Content-Type` is so common that it deserves it's own attribute;
- `content_length` -- the value of the request `Content-Length` header provided by the client; just like `Content-Type`
is used to often, it got its own attribute;
- `request_body` -- base64 encoded *request* body; this is the payload that was sent by the client, not the payload 
returned by **ResponderAPI**;
- `found_headers` -- request headers listed in `expected_headers` and their values;
- `params` -- request URL query params, see the list of param attributes below;
- `responderapi_id` -- the id of the **ResponderAPI** process, assigned on container startup;
- `called_at` -- date and time of the request;
- `execution_time` -- request processing time.

### `params` attributes

The `params` attribute returned by **ResponderAPI** contains request URL query params unpacked by **ResponderAPI**. 

- `delay` -- the value of the `delay` param;
- `random_delay` -- if present, will contain either `min` and `max` attributes; if only `max` attribute is used it 
means no `min` value was provided;
- `headers` -- base64 encoded *response* headers and their values, separated with commas (`,`);
- `no_headers` -- set to `true` if `no_headers` param was used;
- `expected_headers` -- a list of *request* headers you would like **ResponderAPI** to check for, results are listed in the `found_headers` attribute of the response body;
- `status_code` -- the HTTP status code to be returned by **ResponderAPI**;
- `body` -- base64 encoded *response* body;
- `no_body` -- set to `true` if `no_body` param was used.

> The response returned by **ResponderAPI** will also contain the raw URL path and the query string (i.e. anything that comes 
after `?`) params. If **ResponderAPI** does not do what you expect, verify that the URL query string is correct.

### Concatenating `params` attributes

It is possible to pass more than one param in the URL query string by joining them with an ampersand (`&`):

```bash
$ curl -vvv 'remotehost:8080?headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi93aGF0ZXZlcg==&status_code=500'
```

### Healthcheck entries in logs

When configured properly, **ResponderAPI** will record healthcheck requests in the CloudWatch logs. If you do not want
them filling up log groups, set log retention to a few days (3-5?) and set time between healthcheck requests to a
longer period.

## Writing Tests with ResponderAPI

**ResponderAPI**'s behaviour is controlled by request query params. If you want to understand how tests are written,
read the **Usage** section below and read and execute tests found in the [tests](../tests) folder. You will find there tests of
all params as well as basic implementations of tests for all HTTP methods. These will give you a starting point.

### Running Python tests

```bash
$ pytest
```

Copyright (c) 2024, Certograph Ltd