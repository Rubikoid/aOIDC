# aOIDC

Suckless implementation of [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html) for python with asyncio support in mind.

Also implemented:

- [ ] [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749): The OAuth 2.0 Authorization Framework
- [ ] [RFC 7662](https://datatracker.ietf.org/doc/html/rfc7662): OAuth 2.0 Token Introspection

## Implementation status / Roadmap

Core functional, that i need from such library is simple client authentication with authorization code flow, so this will be implemented first.

## Motivation

All the existing python OIDC clients are big balls of mud:

- [pyoidc](https://github.com/CZ-NIC/pyoidc) - synchronous, a little obscure, but the best of all existing.
- [idpy-oidc](https://github.com/IdentityPython/idpy-oidc) - older lib from the same dev as `pyoidc`.
- [authlib](https://github.com/lepture/authlib) - synchronous, no typing, giant pain to use, dual licensing, bad kwargs architecture, bad docs. Worst library.
- [oauthlib](https://github.com/oauthlib/oauthlib) - synchronous, no OIDC client, only provider.
- [oidc-client](https://gitlab.com/yzr-oss/oidc-client) - not really a library.

There are few libraries, which supports oauth2.0 & OIDC as provider (server), but they are out-of-scope for now.
