# Hands-on Notes - Security  - 3760 - Cloud Technologies for Big Data, Machine Learning & Artificial Intelligence

AWS & GCP further Readings - IN Cloud Security with provider context:

- [AWS Well Architecture Framework - Security Pillar](https://d1.awsstatic.com/whitepapers/architecture/AWS-Security-Pillar.pdf)
- [Google Cloud Security Foundations](https://services.google.com/fh/files/misc/google-cloud-security-foundations-guide.pdf)

Security Hands-on Topics:

1. AWS: Creation of IAM, User, Groups and Policies Examples
2. AWS: Creating S3 Buckets with IAM Identity and Bucket resource based Policies, Example of applying the Least Privillege principle in both Policy types.
3. GCP: Implementing JWT/JWS RS256 - Securing Public API endpoints by restricting Service 2 Service access with Origin Athenticity verification - Python 3.7 (Secret Storage, Firestore, CloudFunctions)

# Hands-on Requirements!

  - AWS Account Admin Access
  - GCP Project Owner Access
  - aws and gcloud cli on your machine's command line(Optional)


Cloud Data Privacy & Security Highlights:

> Security OF the Cloud does not equal Security IN the Cloud.
> Need to manage & maintain Data Lifecycle with Security in Mind.
> Leverage Cryptography, Service Configurations and access to Control to secure data in Transit, at Rest, in Use. 
> Think Defence in Depth with Controls in Layers (not in Parallel).
> Stick to the Least Privillege Principle when thinking IAM and Networking in both design and operations.
> Think Identity, Authentication, Authorization, Audit for ANY thing in the Cloud or out of the Cloud.

### Installation

First Tab:
```sh
$ aws
```

Second Tab:
```sh
$ gcloud
```

(optional) Third:
```sh
$ command line test
```

### CLI

```sh
docker build -t zoobin/zoobin:${package.json.version} .
```
 `${package.json.version}`

```sh
docker run -d -p 8000:8080 --restart="always" <youruser>/zoobin:${package.json.version}
```

```sh
127.0.0.1:8000
```

### Todos

 - 
