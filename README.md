# Joplin Software Test Artifacts

This repository collects a software testing study of [Joplin](https://github.com/laurent22/joplin), with requirements and test reports, Python API test scripts, and a JavaScript test excerpt. It does not contain the Joplin application or a standalone implementation of its desktop, mobile, sync, or encryption features.

## Contents

| Path | Purpose |
| --- | --- |
| [SRS.pdf](SRS.pdf) | Software requirements document |
| [TestPlan.pdf](TestPlan.pdf) | Test plan |
| [TestEndReport.pdf](TestEndReport.pdf) | Historical test report |
| [codes/joplin_functional_tests.py](codes/joplin_functional_tests.py) | Sample API operations for notes and tags |
| [codes/joplin_performance_tests.py](codes/joplin_performance_tests.py) | Sample API timing checks and local process measurements |
| [codes/joplin_security_tests.py](codes/joplin_security_tests.py) | Historical security scenarios with unverified API assumptions |
| [codes/CustomTest.test.js](codes/CustomTest.test.js) | Model tests that depend on Joplin source modules and fixtures absent from this repository |
| [codes/joplin_api.py](codes/joplin_api.py) | Shared local API configuration and request boundary |
| [codes/test_joplin_api.py](codes/test_joplin_api.py) | Offline configuration and mocked request regression tests |

The existing scenario descriptions and reports include Turkish text. The PDFs are historical artifacts, not evidence that the current Joplin release passes every scenario.

## Offline checks

Use Python 3.10 or newer. From the repository root, create a virtual environment and install the two packages imported by the scripts:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install requests psutil
.venv\Scripts\python -m unittest discover -s codes -p "test_*.py" -v
```

The regression tests mock the HTTP session and process module imports. They check missing configuration, local origin restrictions, token encoding, redacted connection errors, and the request boundary used by each legacy script. They do not contact Joplin or validate application behavior. There is no application build or configured CI workflow in this repository. `CustomTest.test.js` cannot run on its own because its relative imports require a compatible Joplin source checkout.

## Configuring the legacy API scripts

The scripts create, update, and delete data, may leave test notes behind, and include sync requests. Use a disposable local profile with sync disconnected. Review the individual scenarios before running them; the full security script also sleeps for 15 minutes.

All three scripts require these environment variables before their first request:

| Variable | Required value |
| --- | --- |
| `JOPLIN_API_URL` | Explicit HTTP or HTTPS loopback server origin, for example `http://127.0.0.1:41184` |
| `JOPLIN_API_TOKEN` | API token supplied privately through the process environment |
| `JOPLIN_TEST_PROFILE_ACKNOWLEDGED` | `1`, acknowledging that the target is a disposable local test profile |

The [official Joplin Data API reference](https://joplinapp.org/help/api/references/rest_api/) describes the clipper service, its port, and API token configuration. It uses token query parameters. The shared client encodes those parameters, sets a 10 second request timeout, disables environment proxy configuration, refuses remote origins, and does not follow redirects. Configuration errors stop execution before an HTTP session is created; connection error messages omit credentials and request URLs.

Once the token has been supplied privately to the current process environment, a PowerShell session can set the remaining configuration and invoke one script:

```powershell
$env:JOPLIN_API_URL = "http://127.0.0.1:41184"
$env:JOPLIN_TEST_PROFILE_ACKNOWLEDGED = "1"
.venv\Scripts\python codes/joplin_functional_tests.py
```

The performance and security entry points are `codes/joplin_performance_tests.py` and `codes/joplin_security_tests.py`. Do not commit tokens or use a personal profile. A token previously embedded in the scripts has been removed from the current source; its owner should revoke or replace it because earlier Git history may retain it.

## Interpretation limits

These scripts are examples that need review against the API version being studied. Several scenarios assume endpoints such as `/auth`, `/logs`, `/sync`, note export, or note restore, and fields such as `is_favorite`. The repository supplies no server implementation for those assumptions and does not establish their compatibility with Joplin.

An API response containing an `encrypted` string does not establish encryption at rest or secure sync. Posting an XSS string and inspecting the response does not test how a client renders it. A `/ping` request measures an already running service's response, not application startup, and the mobile performance scenario sends a desktop API request without exercising a mobile device. Some scenarios use weak assertions and can report success for reasons unrelated to the stated requirement. Their printed pass/fail results should not be treated as a security audit or release acceptance result.

No current application performance figures, device results, complete requirements coverage, or resolved-defect claims are established by the files in this repository. Use the PDF reports as historical context and record the actual environment, API compatibility, and observed results for any new study.

## License

See [LICENSE](LICENSE). Joplin is an independent upstream project; its source and tests are subject to their upstream attribution and licensing requirements.
