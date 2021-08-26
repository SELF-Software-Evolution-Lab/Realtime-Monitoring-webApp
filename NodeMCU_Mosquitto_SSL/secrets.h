//enable only one of these below, disabling both is fine too.
#define CHECK_CA_ROOT
// #define CHECK_PUB_KEY
// #define CHECK_FINGERPRINT
////--------------------------////

#define SECRET

#ifdef CHECK_CA_ROOT
static const char digicert[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
MIIELTCCAxWgAwIBAgIUJ8xk/cM+iJs1Gj2vIv7y/o+XXWswDQYJKoZIhvcNAQEL
BQAwgaUxCzAJBgNVBAYTAkNPMQ8wDQYDVQQIDAZCb2dvdGExDzANBgNVBAcMBkJv
Z290YTERMA8GA1UECgwIVW5pYW5kZXMxDTALBgNVBAsMBERJU0MxJzAlBgNVBAMM
HmlvdGxhYi52aXJ0dWFsLnVuaWFuZGVzLmVkdS5jbzEpMCcGCSqGSIb3DQEJARYa
amEuYXZlbGlub0B1bmlhbmRlcy5lZHUuY28wHhcNMjEwODEzMTIyNzM1WhcNMjYw
ODEzMTIyNzM1WjCBpTELMAkGA1UEBhMCQ08xDzANBgNVBAgMBkJvZ290YTEPMA0G
A1UEBwwGQm9nb3RhMREwDwYDVQQKDAhVbmlhbmRlczENMAsGA1UECwwERElTQzEn
MCUGA1UEAwweaW90bGFiLnZpcnR1YWwudW5pYW5kZXMuZWR1LmNvMSkwJwYJKoZI
hvcNAQkBFhpqYS5hdmVsaW5vQHVuaWFuZGVzLmVkdS5jbzCCASIwDQYJKoZIhvcN
AQEBBQADggEPADCCAQoCggEBALpldL3rYIreRyElh74XURq5PyVHeZ8raK9l1Bh7
fdojzXMWZsXLT5AQyj7Xpyv/rQ5rmnxG/Yn5uqQuOGZy2e+YogWD/AiUC6Dt9BTM
35HZurGcC1RYVLbWzZsxoX53aj82PAkwKwAsc3WO61GiFjGMJqeEYdiq4UwsrHqs
JRKDt2HUsqMUwv/Av8QNWgqLZtvfHtRuE9Xzu8FyL2nukQGkXdHBMQQsLOo+h0Nk
iwcYPDMvOy+rf83frEj4h8mXrR3PMHgpIybn89LOv0VUAKrDeVQJJTJPWBObx3Yv
nd2SvzJ8Q++rYk+SpRXBVhcBNExpzx4NsqRqh6Nino1Co+MCAwEAAaNTMFEwHQYD
VR0OBBYEFLe0Qac+cffaxvYBdQWk2QH2v3cUMB8GA1UdIwQYMBaAFLe0Qac+cffa
xvYBdQWk2QH2v3cUMA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEB
AFIDE2Xfm0YC8edGvSqMYxTbNz/3fvmM2149lScKTHQrifN6kOOuGe26+tWgvjvx
KLAsox4GpTVokpyswt7Glr+l0l9UEC5BPqqr5pFEo8MWhAoH5y4NDFzVG6Jkf0i2
tYlQghdEslXV/r6FM4liAIc4CHdxUuvazAehT4JDcQkTmr3swNbF33L/JmTiZ5Ny
gymNUIVxbvQGUXOEwE4fId9e/Uoz7RcytOB9ZGvfb/FKZy69uHe1wavaZRA92W6d
FmcFfve/R1nmeJNDSIZBtXjDvnkuF5dygOBPHibvxIU49+iZD4YJvVrFV66L1xzW
1+SB2xn2cip+HG79iGsqrwc=
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
