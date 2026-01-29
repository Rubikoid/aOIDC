# aOIDC

Suckless implementation of [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0-final.html) for python with asyncio support in mind.

🚧 Currently under development 🚧

Also implemented:

- [ ] [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749): The OAuth 2.0 Authorization Framework
- [ ] [RFC 7033](https://datatracker.ietf.org/doc/html/rfc7033): WebFinger
- [ ] [RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591): OAuth 2.0 Dynamic Client Registration Protocol - **partically**
- [ ] [RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636): Proof Key for Code Exchange by OAuth Public Clients
- [ ] [RFC 7662](https://datatracker.ietf.org/doc/html/rfc7662): OAuth 2.0 Token Introspection
- [ ] [RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414): OAuth 2.0 Authorization Server Metadata
  - [x] Metadata model
  - [ ] `/.well-known/oauth-authorization-server` request
- [ ] [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0-final.html)
- [ ] [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0-final.html)
  - [ ] WebFinger discovery
  - [x] Model
  - [x] `.well-known/openid-configuration` request

## Implementation status / Roadmap

Core functional that I need from such library is simple client authentication via authorization code flow, so this will be implemented first.

1. [ ] OIDC Client for `CODE` flow
2. [ ] OIDC Client for `PKCE` flow
3. [ ] OIDC Client for token verification
4. [ ] OIDC Client for `client_credentials` flow

## Motivation

All the existing python OIDC RP libs are the big balls of mud:

- [pyoidc](https://github.com/CZ-NIC/pyoidc) - synchronous, a little obscure, but the best of all existing.
- [idpy-oidc](https://github.com/IdentityPython/idpy-oidc) - older lib from the same dev as `pyoidc`.
- [authlib](https://github.com/lepture/authlib) - synchronous, no typing, giant pain to use, dual licensing, bad kwargs architecture, bad docs. Worst library.
- [oauthlib](https://github.com/oauthlib/oauthlib) - synchronous, no OIDC client, only provider.
- [oidc-client](https://gitlab.com/yzr-oss/oidc-client) - not really a library.

There are few libraries which supports OAuth 2.0 & OIDC as provider (server), but they are out-of-scope.
