# The data for this tests was collected from  
# https://git.pleroma.social/pleroma/pleroma/blob/develop/test/web/http_sigs/http_sig_test.exs

from activityPub.data_signature import SignatureVerification

def test_correct_sign_with_key():

    public_key = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnGb42rPZIapY4Hfhxrgn\nxKVJczBkfDviCrrYaYjfGxawSw93dWTUlenCVTymJo8meBlFgIQ70ar4rUbzl6GX\nMYvRdku072d1WpglNHXkjKPkXQgngFDrh2sGKtNB/cEtJcAPRO8OiCgPFqRtMiNM\nc8VdPfPdZuHEIZsJ/aUM38EnqHi9YnVDQik2xxDe3wPghOhqjxUM6eLC9jrjI+7i\naIaEygUdyst9qVg8e2FGQlwAeS2Eh8ygCxn+bBlT5OyV59jSzbYfbhtF2qnWHtZy\nkL7KOOwhIfGs7O9SoR2ZVpTEQ4HthNzainIe/6iCR5HGrao/T8dygweXFYRv+k5A\nPQIDAQAB\n-----END PUBLIC KEY-----\n"
    headers = {
        "host": "localtesting.pleroma.lol",
        "connection": "close",
        "content-length": "2316",
        "user-agent": "http.rb/2.2.2 (Mastodon/2.1.0.rc3; +http://mastodon.example.org/)",
        "date": "Sun, 10 Dec 2017 14:23:49 GMT",
        "digest": "SHA-256=x/bHADMW8qRrq2NdPb5P9fl0lYpKXXpe5h5maCIL0nM=",
        "content-type": "application/activity+json",
        "(request-target)": "post /users/demiurge/inbox",
        "signature": "keyId=\"http://mastodon.example.org/users/admin#main-key\",algorithm=\"rsa-sha256\",headers=\"(request-target) user-agent host date digest content-type\",signature=\"i0FQvr51sj9BoWAKydySUAO1RDxZmNY6g7M62IA7VesbRSdFZZj9/fZapLp6YSuvxUF0h80ZcBEq9GzUDY3Chi9lx6yjpUAS2eKb+Am/hY3aswhnAfYd6FmIdEHzsMrpdKIRqO+rpQ2tR05LwiGEHJPGS0p528NvyVxrxMT5H5yZS5RnxY5X2HmTKEgKYYcvujdv7JWvsfH88xeRS7Jlq5aDZkmXvqoR4wFyfgnwJMPLel8P/BUbn8BcXglH/cunR0LUP7sflTxEz+Rv5qg+9yB8zgBsB4C0233WpcJxjeD6Dkq0EcoJObBR56F8dcb7NQtUDu7x6xxzcgSd7dHm5w==\""
    }

    method = "POST"
    path = "/users/demiurge/inbox"

    signature = SignatureVerification(headers, method, path)
    assert signature.verify_public_key(public_key)

def test_correct_fetching_user():
    headers= {
        "x-forwarded-for": "149.202.73.191",
        "host": "testing.pleroma.lol",
        "x-cluster-client-ip": "149.202.73.191",
        "connection": "upgrade",
        "content-length": "2396",
        "user-agent": "http.rb/3.0.0 (Mastodon/2.2.0; +https://niu.moe/)",
        "date": "Sun, 18 Feb 2018 20:31:51 GMT",
        "digest": "SHA-256=dzH+vLyhxxALoe9RJdMl4hbEV9bGAZnSfddHQzeidTU=",
        "content-type": "application/activity+json",
        "signature":'keyId=\"https://niu.moe/users/rye#main-key\",algorithm=\"rsa-sha256\",headers=\"(request-target) user-agent host date digest content-type\",signature=\"wtxDg4kIpW7nsnUcVJhBk6SgJeDZOocr8yjsnpDRqE52lR47SH6X7G16r7L1AUJdlnbfx7oqcvomoIJoHB3ghP6kRnZW6MyTMZ2jPoi3g0iC5RDqv6oAmDSO14iw6U+cqZbb3P/odS5LkbThF0UNXcfenVNfsKosIJycFjhNQc54IPCDXYq/7SArEKJp8XwEgzmiC2MdxlkVIUSTQYfjM4EG533cwlZocw1mw72e5mm/owTa80BUZAr0OOuhoWARJV9btMb02ZyAF6SCSoGPTA37wHyfM1Dk88NHf7Z0Aov/Fl65dpRM+XyoxdkpkrhDfH9qAx4iuV2VEWddQDiXHA==\"',
        "(request-target)": "post /inbox"
    }

    method = "POST"
    path = "/inbox"
    signature = SignatureVerification(headers, method, path)
    assert signature.verify()

def test_another():
    headers = {
        "host": "soc.canned-death.us",
        "user-agent": "http.rb/3.0.0 (Mastodon/2.2.0; +https://mst3k.interlinked.me/)",
        "date": "Sun, 11 Mar 2018 12:19:36 GMT",
        "digest": "SHA-256=V7Hl6qDK2m8WzNsjzNYSBISi9VoIXLFlyjF/a5o1SOc=",
        "content-type": "application/activity+json",
        "signature":'keyId=\"https://mst3k.interlinked.me/users/luciferMysticus#main-key\",algorithm=\"rsa-sha256\",headers=\"(request-target) user-agent host date digest content-type\",signature=\"CTYdK5a6lYMxzmqjLOpvRRASoxo2Rqib2VrAvbR5HaTn80kiImj15pCpAyx8IZp53s0Fn/y8MjCTzp+absw8kxx0k2sQAXYs2iy6xhdDUe7iGzz+XLAEqLyZIZfecynaU2nb3Z2XnFDjhGjR1vj/JP7wiXpwp6o1dpDZj+KT2vxHtXuB9585V+sOHLwSB1cGDbAgTy0jx/2az2EGIKK2zkw1KJuAZm0DDMSZalp/30P8dl3qz7DV2EHdDNfaVtrs5BfbDOZ7t1hCcASllzAzgVGFl0BsrkzBfRMeUMRucr111ZG+c0BNOEtJYOHSyZsSSdNknElggCJekONYMYk5ZA==\"',
        "x-forwarded-for": "2607:5300:203:2899::31:1337",
        "x-forwarded-host": "soc.canned-death.us",
        "x-forwarded-server": "soc.canned-death.us",
        "connection": "Keep-Alive",
        "content-length": "2006",
        "(request-target)": "post /inbox",
    }
    method = "POST"
    path = "/inbox"
    signature = SignatureVerification(headers, method, path)
    assert signature.verify()