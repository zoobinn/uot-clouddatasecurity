import os
import flask
import json
jwcrypto.jwk as jwk, time
from google.cloud import firestore
from google.cloud import secretmanager
from jose import jwt

project_id = os.environ["GCP_PROJECT"]
function_name = os.environ["FUNCTION_NAME"]
function_region = os.environ["FUNCTION_REGION"]
publicpemurl = f'https://{function_region}-{project_id}.cloudfunctions.net/{function_name}/.well-known/public.pem'
publicjwksurl = f'https://{function_region}-{project_id}.cloudfunctions.net/{function_name}/.well-known/public.jwks'
keygenurl = f'https://{function_region}-{project_id}.cloudfunctions.net/{function_name}/keygen/'
tokegenurl = f'https://{function_region}-{project_id}.cloudfunctions.net/{function_name}/tokengen/'

def dispatch(request):

    request_args = request.args
    ######
    ####  PATH KEYGEN /keygen/
    ######
    if request.method == 'GET' and request.path == '/keygen/':
        ## Generate RSA 2048 KeyPair
        key = jwk.JWK.generate(kty='RSA', size=2048)
       
        ## Export Private Key to PEM forkmat
        priv_pem = key.export_to_pem(private_key=True, password=None)
        textualprivpem = priv_pem.decode('utf-8')
        
        ## Export Public Key to PEM format
        pub_pem = key.export_to_pem(private_key=False)
        textualpubpem = pub_pem.decode('utf-8')
        
        ## Get JSON Format of the KeyPair friendly for JWK/JWT presentation
        priv_key = jwk.JWK.from_pem(priv_pem)
        pub_key = jwk.JWK.from_pem(pub_pem)
        json_pub = jwk.JWK.export_public(key)
        json_priv = jwk.JWK.export_private(key)

        ## Storing Private/Secret PEM and JSONs in GCP Secret Storage
        add_secret_version("priv-pem",f'{textualprivpem}')
        add_secret_version("jwk-secret",f'{json_priv}')

        ## Storing Public PEM and JSON in GCP FireStore
        db = firestore.Client()
        doc_ref = db.collection(u'jwtpublic').document(u'keys')
        doc_ref.set({
            u'textual-public-pem' : f'{textualpubpem}',
            u'public-jwk': f'{json_pub}',
        })
        try:
            return "Key Pair Generated: publicPEM: <br>" + textualpubpem  + f'<br> Access Token: use this URL to generate -> {keygenurl}<br>' + '<br> publicJSON: <br>' + str(json_pub) # SECRET: priv_pem SHALL NOT BE SHARED or Printed
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
                return str(e.message)
            else:
                print(e)
                return str(e)
    ######
    ####  PATH TOKENGEN /tokengen/
    ######
    elif request.method == 'GET' and request.path == '/tokengen/':
        try:
            ## Get Secret Key from GCP Secret Storage
            secretjson = access_secret_version("jwk-secret");
            secretprivpem = access_secret_version("priv-pem");

            ## Add JWT timings IAT, EXP, NBF
            issue = int(time.time())
            notbefore = int(time.time())
            expiery = int(time.time()) + 3600

            ## Generate JWS by feeding Secret Key with Algorithm RS256
            token = jwt.encode({'iat' : issue, 'exp' : expiery, 'nbf' : notbefore, 'public_pem' : f'{publicpemurl}'}, secretprivpem, algorithm='RS256')

            ## Getting the Public Key to Verify the Signature generated in Token Value
            db = firestore.Client()
            doc_ref = db.collection(u'jwtpublic').document(u'keys')
            doc = doc_ref.get()
            if doc.exists:
                # Signature Failed
                wrongtoken = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1OTczMjY3MDMsImlhdCI6MTU5NzMyNjQwMywiaWRlbnRpdHkiOiJmdW5jdGlvbi0xIiwianRpIjoiYk43aUszV2Z1RjJLWVdkNG1ScHR2ZyIsIm1lc3NhZ2UiOiJUaGlzIG1lc3NhZ2UgaXMgYSBzaWduZWQgbWVzc2FnZSBlbnN1cmluZyBpbnRlZ2lydHkgYW5kIGF1dGhlbnRpY2l0eSBvZiBpdHMgb3JpZ2luYXRvciIsIm5iZiI6MTU5NzMyNjQwM30.Zrrvh-s4fsHDddTOc3TXZqi4EMq2TpoKpPFRqKV7mcCmI_CQLszMMpxpjxPQGdh6MqsdzAQnsi9J9mpREAqHwSDhw15-4AIGnKtqRMNlxAqfplIPFxqwbGAA2P8kSc7qWe7HUnZq-6t7pqcSWkJxyilfQbT8byGl5nu5PySclzJTkdbyVpGnq50L1j09Wq8k2X1Nvv5JHCdjJHVC9RJCM5RmH721cPRwcB640FbVhXDTADlaxkYqQI29sfpSsvMrn8s76hOGv-iZ-dQyRaDM27HGELpwlN0HPQ3RXRDhX06osr2PTNM-DFPinAS8uuonuf8tFZzELEY-CMEasl7cNw'
                # NBF Failed
                wrongtoken2 = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjEwOTc0MTM1NTUsImV4cCI6MTA5NzQxNzE1NSwibmJmIjoyNTk3NDEzNTU1LCJwdWJsaWNfcGVtIjoiaHR0cHM6Ly9jbG91ZC1zZWN1cml0eS04NjhjOTg3Ny5jbG91ZGZ1bmN0aW9ucy5uZXQvZnVuY3Rpb24tMS8ud2VsbC1rbm93bi9wdWJsaWMucGVtIn0.es9_5T2J_5HkFRbIKgapsw0rAmIq2WKZ5BaCVsyPBtwA7xNAiP370pWcFt85Oi0yr5H5YgoyT4UlXYcNqM1sk64Oc5KXJ3-Dga39sClu6pgG82a5-G9MMFnYcR86ETEFAyh692qvxffOMjGmr1qqiwgGsVH3TwqSv6kOFksBFNasZW7XG4pv-svwZ7MbDNM4wmqYCcn_G5Ek7AZy8n9LkCyOZNzIDGxtWzvCJLcTw7jzCl2uqHzpFHgP1JXAwiIsEXvUWjzB-GcdU17G9P3wlV_p0siCLnKhJDnYA7QpgawKOJYx-sUKzW86bmBXnA-gYfn-Z4lH752Gpgpw8tYFdg'
                # Expiery Time Failed
                wrongtoken3 = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjEwOTc0MTM1NTUsImV4cCI6MTA5NzQxNzE1NSwibmJmIjoxNTk3NDE1NTAwLCJwdWJsaWNfcGVtIjoiaHR0cHM6Ly9jbG91ZC1zZWN1cml0eS04NjhjOTg3Ny5jbG91ZGZ1bmN0aW9ucy5uZXQvZnVuY3Rpb24tMS8ud2VsbC1rbm93bi9wdWJsaWMucGVtIn0.p3OvKplkk2adlOuE_Rg2x3WJKnAQsfqnafUviBv_LT0iy3rHpbtlnRReS5RfVuipS_xdpK8Z9KZOWHBKbxv8S9PVysxsRpPt-EB-5bAA-kNA7GI6BHs-AKUqYNxLBbjsapxIH87jbSHNc_D5aoY3V9EGHLG2cbFLxLZ5lUPxPgtLHWEqlwDHoc9hVeHJ7W0H5_v1APUSZ2hw7EtfhQNVgcaY78YE_930SMmWmUgKC6gDzU1lS8Pl0Nv55A7yo77qGPYMrHKpNq56h-gfRAUEE-lxSBoaKwZ904aKKtLmSk7HQkoRIsRnPE5GalNo3eWJr0RhXK8lxriOr3OTOxxKZQ'
                dictresult = doc.to_dict()
                jsonresult = json.dumps(dictresult)
                show_pem = dictresult["textual-public-pem"]
                ## Verify Signature
                verify = jwt.decode(token, show_pem, algorithms='RS256')
                return f'AccessToken: {token} <br> Public: {show_pem} <br> Verification Result: {verify}'
            else:
                return "public pem doesn't exists"
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
                return str(e.message)
            else:
                print(e)
                return str(e)
    ######
    #### PATH public.jwks /.well-known/public.jwks
    ######
    elif request.method == 'GET' and request.path == '/.well-known/public.jwks':
        try:
            db = firestore.Client()
            doc_ref = db.collection(u'jwtpublic').document(u'keys')
            doc = doc_ref.get()
            if doc.exists:
                dictresult = doc.to_dict()
                jsonresult = json.dumps(dictresult)
                show_jwk = dictresult["public-jwk"]
                return f'{show_jwk}'
            else:
                return "public jwks doesn't exists"
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
                return str(e.message)
            else:
                print(e)
                return str(e)
    ######
    #### PATH public.pem /.well-known/public.pem
    ######
    elif request.method == 'GET' and request.path == '/.well-known/public.pem':
        try:
            db = firestore.Client()
            doc_ref = db.collection(u'jwtpublic').document(u'keys')
            doc = doc_ref.get()
            if doc.exists:
                dictresult = doc.to_dict()
                jsonresult = json.dumps(dictresult)
                show_pem = dictresult["textual-public-pem"]
                return f'{show_pem}'
            else:
                return "public pem doesn't exists"
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
                return str(e.message)
            else:
                print(e)
                return str(e)
    ######
    #### PATH DEBUG
    ######
    elif request.method == 'GET' and request.path == '/debug/':
        return "debug" + str(request.base_url) + "-" + str(request.method) + "-" + str(request.headers) + str(request.path)
    ######
    #### PATH DEFAULT
    ######
    else:
        return f'URL to GenerateaNewKeypair: {keygenurl} <br>' +  f'URL to GenerateNewToken: {tokegenurl}'

def add_secret_version(secret_id, payload):
    client = secretmanager.SecretManagerServiceClient()
    parent = client.secret_path(project_id, secret_id)
    payload = payload.encode('UTF-8')
    response = client.add_secret_version(parent, {'data': payload})
    print(f'Added secret version: {response.name}')
def access_secret_version(secret_id, version_id="latest"):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = client.secret_version_path(project_id, secret_id, version_id)

    # Access the secret version.
    response = client.access_secret_version(name)

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')
