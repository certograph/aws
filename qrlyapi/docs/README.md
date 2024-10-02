QRly API -- QR code generator API in your own AWS cloud
=======================================================

* **QRlyAPI** is a zero-configuration QR code generation API server designed to make it easy to generate QR codes at 
  scale and low cost.
* **QRlyAPI** is available as a Docker container and is meant to run in **AWS Elastic Container Service (ECS)**
  clusters using **AWS EC2** or **AWS Fargate** hosts. You can also deploy it in your **AWS Elastic Kubernetes Service
  (EKS)** clusters.

## Security and Data Safety

> **QRlyAPI** does not write to the local filesystem of the host. The only external calls made by **QRlyAPI**
> are to the AWS API to verify entitlement (presence of **AWS Marketplace** subscription) and register usage (time).
> **QRlyAPI** does not store or share with any third-party any part of the data received or returned. All
> **QRlyAPI** logs are sent to the **AWS CloudWatch** log groups in the same AWS account that **QRlyAPI** runs
> in. Payload strings are hashed out to protect sensitive information leaking though the logs.

## Usage

**QRlyAPI** expects POST requests that contain a JSON payload specifying QR code generation parameters.
All parameters except `payload` are optional,.

### `payload` -- text payload

QR code payload can be a link or some text. The length of text can be up to 4296 characters.

```bash
$ curl -vvv -X POST http://remotehost:8080 --data '{"payload":"https://www.certograph.com/"}' --output qrcode.png
```

### `size` -- width and height of the QR code image

The `size` parameter is a positive integer. It can be omitted, but generally varies from less than 30 pixels to several
thousands pixels.

> If you need to generate QR codes at print resolution, multiply the printed size of the QR code in inches by the
> printer resolution. e.g. 300 for 300dpi or 600 for 600dpi.

You can omit `size` and if you do, **QRlyAPI** will generate a tiny 29x29 pixel image.

```bash
$ curl -vvv -X POST http://remotehost:8080 --data '{"payload":"https://www.certograph.com/","size":100}' --output qrcode.png
```

* Minimum size: 29 pixels
* Maximum size: 2,147,483,647 pixels (32-bit) -- theoretical, if you use a host with a lot of memory
* Maximum size: 9,223,372,036,854,775,807 pixels (64-bit) -- theoretical, if you use a host with a lot of memory

### `trim_width`

**QRlyAPI** generates a standard border around the QR codes to help scanners recognize and separate the code from its
surroundings. If you want to make it smaller, use the `trim_width` parameter.

```bash
$ curl -vvv -X POST http://remotehost:8080 --data '{"payload":"https://www.certograph.com/","trim_width":3, "size":36}' --output qrcode.png
```

> If the results of using the `trim_width` parameter look wrong, adjust the size of the QR code using the `size` 
> parameter.

### `background_colour`

QR code background colour. If you omit this param, the QR code image will have white background (R: `255`, G: `255`, B: `255`).
If you want to change it, use the `background_colour=r,g,b` syntax, like this:

```bash
$ curl -vvv -X POST http://remotehost:8080 --data '{"payload":"https://www.certograph.com/","background_colour":{"r":0,"g":255,"b":0,"a":255}}' --output qrcode.png
```

Allowed range of values for each colour component (`R`, `G`, `B`) is 0 to 255.
'A' is alpha (transparency), 0 is fully transparent, 255 is fully opaque.

> NOTE: Do not make background and foreground colours too similar. QR code readers convert images captured by their
> cameras into a black and white image using a simple algorithm that will make non-contrasting colours blend into solid
> black or white. For example, a black foreground and a red background will blend into a solid black patch and the
> reader will be unable to recover information from the QR code.

### `foreground_colour`

QR code foreground colour. If you omit this parameter, the QR code image will have black foreground (R: `0`, G: `0`, B: `0`, A: `0`).
If you want to change it, use the `foreground_colour=r,g,b` syntax, like this:

```bash
$ curl -vvv -X POST http://remotehost:8080 --data '{"payload":"https://www.certograph.com/","foreground_colour":{"r":0,"g":255,"b":0,"a":255}}' --output qrcode.png
```

Allowed range of values for each colour component (`R`, `G`, `B`) is 0 to 255.
'A' is alpha (transparency), 0 is fully transparent, 255 is fully opaque.

> NOTE: Do not make background and foreground colours too similar. QR code readers convert images captured by their 
> cameras into a black and white image using a simple algorithm that will make non-contrasting colours blend into solid 
> black or white. For example, a black foreground and a red background will blend into a solid black patch and the 
> reader will be unable to recover information from the QR code.

### `recovery_level`

There are four levels of QR code recovery. Recovery level is another way of thinking of the amount of repeated
information encoded in the QR code that allows the reader to recover data when the code is partially damaged. 
There are four recovery levels available:

* `low`
* `medium`
* `high`
* `highest`

```bash
$ curl -vvv -X POST http://remotehost:8080 --data '{"payload":"https://www.certograph.com/","recovery_level":"low"}' --output qrcode.png
```

## Testing

The `tests` directory contains a Python test suite. Replace `remotehost` with the public IP of the instance of **QRlyAPI**.
Payload strings are hashed out to protect sensitive information leaking though the logs.

## Debugging

**QRLyAPI** logs requests to CloudWatch. 

* `Error: Invalid HTTP method: GET. Use POST` -- incorrect HTTP request method. Use `POST`
* `Error: Could not decode request payload`
* `Error: Invalid QR code image trim width: -5. Must be greater than 0`

## Performance

It takes around ~1ms (one millisecond) to generate a sub-100 pixel QR code on a host with the smallest
amount of memory and compute. You can check execution time in CloudWatch logs. Values of `execution_time` 
are reposted in microseconds.
