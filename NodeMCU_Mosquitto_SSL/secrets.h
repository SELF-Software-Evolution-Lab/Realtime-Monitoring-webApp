//enable only one of these below, disabling both is fine too.
#define CHECK_CA_ROOT
// #define CHECK_PUB_KEY
// #define CHECK_FINGERPRINT
////--------------------------////

#define SECRET

#ifdef CHECK_CA_ROOT
static const char digicert[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
MIIEBTCCAu2gAwIBAgIUTRtBAJYUFcnUiCNXJDOny/6RmVkwDQYJKoZIhvcNAQEL
BQAwgZExCzAJBgNVBAYTAkNPMRUwEwYDVQQIDAxDdW5kaW5hbWFyY2ExDzANBgNV
BAcMBkJvZ290YTERMA8GA1UECgwIVW5pYW5kZXMxDTALBgNVBAsMBE1pc28xDzAN
BgNVBAMMBmJyb2tlcjEnMCUGCSqGSIb3DQEJARYYYWRtb25zaXNAdW5pYW5kZXMu
ZWR1LmNvMB4XDTI0MDgwNzE0MDIwMVoXDTI5MDgwNzE0MDIwMVowgZExCzAJBgNV
BAYTAkNPMRUwEwYDVQQIDAxDdW5kaW5hbWFyY2ExDzANBgNVBAcMBkJvZ290YTER
MA8GA1UECgwIVW5pYW5kZXMxDTALBgNVBAsMBE1pc28xDzANBgNVBAMMBmJyb2tl
cjEnMCUGCSqGSIb3DQEJARYYYWRtb25zaXNAdW5pYW5kZXMuZWR1LmNvMIIBIjAN
BgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAp8dgdoZLhQahtCCxuOcoVJUpg+Ko
EgSKy6kaF0+Sjay0bd7hZeCOPP1dZql1BhfUgl2qqCBGdnB41sQBxeTNk4L6ZVo/
eMI8wPuTYEkTwyyJU3pPy4upwX6BMBHkJfp19Hyca7G7RU+nVpgB921ulpHmatt2
j612yI9DTRke2G1pI75tpbi/DZIj5AshPRJEzvCbmzdRK/w0HR8DsGfkyrOLXs2J
O22oJpU5yeZnzUlVKMQRv3BLTMYxZ1S10EmLb9cJccQOU7ZX5WtauAarFkdL2S+r
Ivg5F736dl8nMjriwAB3skekRiNzVVh7VA/eCeIfYx5nGYuBf+RMZy1ItQIDAQAB
o1MwUTAdBgNVHQ4EFgQUfpWsX41A17h7U4DlEsA+3XnQOk0wHwYDVR0jBBgwFoAU
fpWsX41A17h7U4DlEsA+3XnQOk0wDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0B
AQsFAAOCAQEAg4OorSMFbqO7kJoutdmFIZkWMYTPFLXHlTGx33Y6FRL0qjB19Pf/
62tb1uKx3p/7uYfjMK0qbRR1Sngmz6y43N5KMogZbS2EfpuTh9V8jdUgphOMo6+1
EUqJzb9cU73VGayfd9UeRI0GRPtouCcvsEfx7CC9QcoP0lYzGCF8zI/S+jRUsNLg
jp/pn1TpOnED2z9jaMVhA0YOtSREMlrFxEUFdBXlB8VilKhJ06x5oX+xEWwSAQgj
vf1EOYTZpp4fYr5hC1dwyqVFDdRyL/SJuRywcl/KtVoWhtkdNzHXpqgsKtlqQhYH
LCxfJkfimLhbD1Pwq1VC0eW27K1PAXADYQ==
-----END CERTIFICATE-----
)EOF";
#endif

#ifdef CHECK_PUB_KEY
// Extracted by: openssl x509 -pubkey -noout -in ca.crt
static const char pubkey[] PROGMEM = R"KEY(
-----BEGIN PUBLIC KEY-----
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxx
-----END PUBLIC KEY-----
)KEY";
#endif

#ifdef CHECK_FINGERPRINT
// Extracted by: openssl x509 -fingerprint -in server.crt
static const char fp[] PROGMEM = "AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD";
#endif
