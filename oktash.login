OKTA_DOMAIN= # e.g. example.okta.com
curl -d '{ "username":"$USERNAME","password":"$PASSWORD" }' -c cookie_jar.txt \
    -H "Content-Type: application/json" -b cookie_jar.txt -c cookie_jar.txt \
     https://$OKTA_DOMAIN/api/v1/authn > auth.json

{
  "stateToken": "00oBpbTzKnRdKLYvc8yNBdFTusuoS4KUhdANgrMsOt",
  "expiresAt": "2019-07-08T22:54:32.000Z",
  "status": "MFA_REQUIRED",
  "_embedded": {
    "user": {
      "id": "00umczvjiljEfeDFx0x7",
      "profile": {
        "login": "gordon.weakliem@example.global",
        "firstName": "Gordon",
        "lastName": "Weakliem",
        "locale": "en",
        "timeZone": "America/Los_Angeles"
      }
    },
    "factors": [
      {
        "id": "opfmgmgkmnSSb3R1Q0x7",
        "factorType": "push",
        "provider": "OKTA",
        "vendorName": "OKTA",
        "profile": {
          "credentialId": "Gordon.Weakliem@example.global",
          "deviceType": "SmartPhone_Android",
          "keys": [
            {
              "kty": "PKIX",
              "use": "sig",
              "kid": "default",
              "x5c": [
                "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4zQ0id+9Tt01PWbI0DSf9RXPg5CrrbqX\n3gBu2oPfMj1vtei1oVMGN9YKV+fnCWfn2urVHTwJiBCEm7lNDwFFJjg6zYxaTPrGyHvPPL7Io6t2\ngJk5FA8H/nLEbBGpTylSOHYzWFWz0vTQf7FWdw+Rav8QPY8iqSaQ++VCo8OoshyIJMN6GCBPyWMi\nl1VvvgcTIi1m6+WwhS6wlFLz7VLnVnvFIuK4RSOVfpeHi+PXXYP6eQK6f9HF8MRtIOEKB4OX4BAu\nKStVnovLeBzu7H49v4n+WuqI+ANwRq5IcGGFbuRv7PRRcXT2y0Uymn7aaBWj7h63+a6RCWEP3Zy3\ntlIe7wIDAQAB\n"
              ]
            }
          ],
          "name": "BND-L34",
          "platform": "ANDROID",
          "version": "26"
        },
        "_links": {
          "verify": {
            "href": "https://example.okta.com/api/v1/authn/factors/opfmgmgkmnSSb3R1Q0x7/verify",
            "hints": {
              "allow": [
                "POST"
              ]
            }
          }
        }
      },
      {
        "id": "smsmgmhea6O2Ayr1t0x7",
        "factorType": "sms",
        "provider": "OKTA",
        "vendorName": "OKTA",
        "profile": {
          "phoneNumber": "+1 XXX-XXX-7234"
        },
        "_links": {
          "verify": {
            "href": "https://example.okta.com/api/v1/authn/factors/smsmgmhea6O2Ayr1t0x7/verify",
            "hints": {
              "allow": [
                "POST"
              ]
            }
          }
        }
      },
      {
        "id": "ostmgmifdbbSVUPkA0x7",
        "factorType": "token:software:totp",
        "provider": "OKTA",
        "vendorName": "OKTA",
        "profile": {
          "credentialId": "Gordon.Weakliem@example.global"
        },
        "_links": {
          "verify": {
            "href": "https://example.okta.com/api/v1/authn/factors/ostmgmifdbbSVUPkA0x7/verify",
            "hints": {
              "allow": [
                "POST"
              ]
            }
          }
        }
      }
    ],
    "policy": {
      "allowRememberDevice": true,
      "rememberDeviceLifetimeInMinutes": 20160,
      "rememberDeviceByDefault": false,
      "factorsPolicyInfo": {
        "opfmgmgkmnSSb3R1Q0x7": {
          "autoPushEnabled": false
        }
      }
    }
  },
  "_links": {
    "cancel": {
      "href": "https://example.okta.com/api/v1/authn/cancel",
      "hints": {
        "allow": [
          "POST"
        ]
      }
    }
  }
}


VERIFY_URL=$(jq -r '._embedded.factors[]|select(.factorType=="push")._links.verify.href' auth.json)

VERIFY_URL=$(jq -r '._embedded.factors[]|select(.factorType=="token:software:totp")._links.verify.href' auth.json)

# for push keep looping on this until .status == SUCCESS
curl -XPOST -d @auth.json -H "Content-Type: application/json;" -H "Accept: application/json;" \
 -b cookie_jar.txt -c cookie_jar.txt \
 $VERIFY_URL > session.json

# for totp
curl -XPOST -d @auth.json -H "Content-Type: application/json;" -H "Accept: application/json;" \
 -b cookie_jar.txt -c cookie_jar.txt \
 $VERIFY_URL > verify.json

{
  "stateToken": "00T_V6Py66WDkx5GwuWzI5Bc26Om6Av65hxrLob9tt",
  "expiresAt": "2019-07-13T19:46:02.000Z",
  "status": "MFA_CHALLENGE",
  "factorResult": "CHALLENGE",
  "_embedded": {
    "user": {
      "id": "00umczvjiljEfeDFx0x7",
      "profile": {
        "login": "Gordon.Weakliem@example.global",
        "firstName": "Gordon",
        "lastName": "Weakliem",
        "locale": "en",
        "timeZone": "America/Los_Angeles"
      }
    },
    "factor": {
      "id": "ostmgmifdbbSVUPkA0x7",
      "factorType": "token:software:totp",
      "provider": "OKTA",
      "vendorName": "OKTA",
      "profile": {
        "credentialId": "Gordon.Weakliem@example.global"
      }
    },
    "policy": {
      "allowRememberDevice": true,
      "rememberDeviceLifetimeInMinutes": 20160,
      "rememberDeviceByDefault": false,
      "factorsPolicyInfo": {}
    }
  },
  "_links": {
    "next": {
      "name": "verify",
      "href": "https://example.okta.com/api/v1/authn/factors/ostmgmifdbbSVUPkA0x7/verify",
      "hints": {
        "allow": [
          "POST"
        ]
      }
    },
    "prev": {
      "href": "https://example.okta.com/api/v1/authn/previous",
      "hints": {
        "allow": [
          "POST"
        ]
      }
    },
    "cancel": {
      "href": "https://example.okta.com/api/v1/authn/cancel",
      "hints": {
        "allow": [
          "POST"
        ]
      }
    }
  }
}

STATE_TOKEN=$(jq -r '.stateToken' verify.json )
curl -s -H "Content-Type: application/json" -d "{\"stateToken\": \"${STATE_TOKEN}\", \"passCode\":\"271575\" }" \
    -b cookie_jar.txt -c cookie_jar.txt \
    $VERIFY_URL > session.json

{
  "expiresAt": "2019-07-13T19:50:01.000Z",
  "status": "SUCCESS",
  "sessionToken": "20111Ne3YvcCGieNRjneHu3F6rxzc0r3w7La9nsz5iIz6EXupm-W0cq",
  "_embedded": {
    "user": {
      "id": "00umczvjiljEfeDFx0x7",
      "profile": {
        "login": "Gordon.Weakliem@example.global",
        "firstName": "Gordon",
        "lastName": "Weakliem",
        "locale": "en",
        "timeZone": "America/Los_Angeles"
      }
    }
  },
  "_links": {
    "cancel": {
      "href": "https://example.okta.com/api/v1/authn/cancel",
      "hints": {
        "allow": [
          "POST"
        ]
      }
    }
  }
}

SESSION_TOKEN=$(jq -r '.sessionToken' session.json)
# get ~/.aws/config [profile] for aws_saml_url
SAML_PATH=home/example_awsdevdevelopers_1/0oalvzon2nfi40DXN0x7/alnlvzsal4s1KSRZV0x7


# get the SAML token
curl -d -L -H "Accept-Encoding: identity;" -i -b cookie_jar.txt -c cookie_jar.txt \
  "https://$OKTA_DOMAIN/$SAML_PATH?onetimetoken=$SESSION_TOKEN"


aws sts assume-role-with-saml --role-arn arn:aws:iam::563116987804:role/oktaDevDevelopersRole \
    --principal-arn $PRINCIPAL_ARN  --saml-assertion $SAML
