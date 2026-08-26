# Security Policy

## Reporting a Vulnerability

If you find a security issue in COMET — for example a vulnerability in
the bundled FastAPI sidecar, a way to escape the Electron renderer, or a
secret leak in a packaged build — please **do not open a public issue**.

Instead, send a private report to the maintainer through GitHub's private
vulnerability disclosure flow:

**https://github.com/hyunjin-kor/COMET/security/advisories/new**

Please include:

- A short description of the issue.
- The version (or commit SHA) you tested against — see `package.json` /
  `pyproject.toml` for the active version.
- A reproduction path: minimum input, observed behaviour, expected
  behaviour.
- Any relevant logs from `%APPDATA%\COMET\comet-launcher.log`
  (Windows desktop) or your terminal (development build).

You should get an acknowledgement within a few working days. Confirmed
issues are fixed on `master` and shipped in the next patch release; the
release notes name the CVE / advisory once published.

## Supported Versions

Only the latest tagged release on GitHub is actively patched. Older
desktop installers stay available for download but do not receive
security updates — please update to the latest installer before
reporting.

| Version | Supported |
| --- | --- |
| Latest tag on `master` | Yes |
| Older patch releases   | No  |

## Out of Scope

COMET is a local desktop tool. The following are not in scope for
the security policy:

- Bugs in third-party APIs or feeds (Yahoo Finance chart endpoint,
  Metals.Dev, MetalpriceAPI, BLS, etc.). Please report those upstream.
- Issues that require an attacker to already have local user-level
  access to the machine running COMET.
- Cosmetic UI bugs that don't expose data — please file those as a
  normal GitHub issue.
