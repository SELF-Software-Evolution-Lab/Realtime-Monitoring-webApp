//enable only one of these below, disabling both is fine too.
#define CHECK_CA_ROOT
// #define CHECK_PUB_KEY
// #define CHECK_FINGERPRINT
////--------------------------////

#define SECRET

#ifdef CHECK_CA_ROOT
static const char digicert[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
MIIEQzCCAyugAwIBAgIUVxULRUCblz76p0JQ02yqP+0oIT0wDQYJKoZIhvcNAQEL
BQAwgbAxCzAJBgNVBAYTAkNPMRMwEQYDVQQIDApDdW5kY2xpZW50MRUwEwYDVQQH
DAxCb2dvdGFDbGllbnQxFzAVBgNVBAoMDlVuaWFuZGVzQ2xpZW50MRcwFQYDVQQL
DA5TeXN0ZW1hc0NsaWVudDEnMCUGA1UEAwweaW90bGFiLnZpcnR1YWwudW5pYW5k
ZXMuZWR1LmNvMRowGAYJKoZIhvcNAQkBFgtpb3RAaW90LmNvbTAeFw0yMzA4MDkx
NTM3MzdaFw0yODA4MDgxNTM3MzdaMIGwMQswCQYDVQQGEwJDTzETMBEGA1UECAwK
Q3VuZGNsaWVudDEVMBMGA1UEBwwMQm9nb3RhQ2xpZW50MRcwFQYDVQQKDA5Vbmlh
bmRlc0NsaWVudDEXMBUGA1UECwwOU3lzdGVtYXNDbGllbnQxJzAlBgNVBAMMHmlv
dGxhYi52aXJ0dWFsLnVuaWFuZGVzLmVkdS5jbzEaMBgGCSqGSIb3DQEJARYLaW90
QGlvdC5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCxteflALjc
YIu2G4Dx1w3nNfmFuvQIJtU3zGcWD8yiWzVfmhGIHTR5AMHGq+5p3VxKmX8T0aPJ
fgSgrBWxQFog3PqKZMDGIukcLf9EEyFL2DGkkiTj/DaxB6aa8yI2gHn/oSRLjw3p
5fWlEerMxOm9Uspvrzz6xnOObCJD/c8HMfWgzQEWTm+y60irQxh1V9UmTSsiIpj3
9+nfdOQfenOq5R92vdjVCDm4jpeeDf8P10jEqqgvxk7qA03qf+UKAMDv4GudfQxM
kkd+7zk+jncgSTb8nfVjazCm6nYreQVhHRCI103pDQ7c4aR02moisBBon2iUOVtk
bovtf4zc/2cnAgMBAAGjUzBRMB0GA1UdDgQWBBRMdA7bUGAb3SSSZ9brzWmeVJvw
+jAfBgNVHSMEGDAWgBRMdA7bUGAb3SSSZ9brzWmeVJvw+jAPBgNVHRMBAf8EBTAD
AQH/MA0GCSqGSIb3DQEBCwUAA4IBAQB8/lGbAIGXygkUwBuqDM+Vdvlgag3k93Gd
eNHGsMf6lvXAulvqnSm3CNYmZFmOGawOS7QJNKis1tIl5DzLPDhbxQ/IqhyHgD68
8IDjg6GyfxoChNOCO0fROdzRnl7l4izQ5EtmXRFY7Y8105EOyw1IaRK+SG9CzmJw
n2H83Dv/dg4Dx66vkZRwdHWTRW1d7lx4+GKzlpuDlPmIiLqOJZ+U5rB2sOwFNGud
1isNZfVIwrcEEsk7gP5pj3Fn5S5q6OVFlA7wxuxBb+AuC6FAt/uur5jjMvTsV7oY
upeTOzZ5IdS7YKX3qeuRGqnGqwu7ifAklS8j1sl9eLCdFK74dKFD
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
