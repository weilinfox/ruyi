<div align="center">
<img alt="RuyiSDK Logo" src="resources/ruyi-logo-256.png" height="128" />
<h3>Ruyi</h3>
<p>The package manager for <a href="https://github.com/ruyisdk">RuyiSDK</a>.</p>
</div>

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ruyisdk/ruyi/dist.yml)
![GitHub License](https://img.shields.io/github/license/ruyisdk/ruyi)
![Python Version](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![GitHub Tag](https://img.shields.io/github/v/tag/ruyisdk/ruyi?label=latest%20tag)

## Installation and usage

You can get pre-built binaries of `ruyi` from [GitHub Releases][ghr] or
[the RuyiSDK mirror][mirror-testing] for easier testing.
Rename the downloaded file to `ruyi`, make it executable,
put inside your `$PATH` and you're ready to go.

[ghr]: https://github.com/ruyisdk/ruyi/releases
[mirror-testing]: https://mirror.iscas.ac.cn/ruyisdk/ruyi/testing/

You can browse the documentation at [the dedicated RuyiSDK docs site][docs]
(only available in Chinese right now).

[docs]: https://ruyisdk.github.io/docs/zh/introduction/

## Configuration

Various aspects of `ruyi` can be configured with files or environment variables.

### Config search path

`ruyi` respects `$XDG_CONFIG_HOME` and `$XDG_CONFIG_DIRS` settings, and will
look up its config accordingly. If these are not explicitly set though, as in
typical use cases, the default config directory is most likely `~/.config/ruyi`.

### Config file

Currently `ruyi` will look for an optional `config.toml` in its XDG config
directory. The file, if present, looks like this, with all values being default:

```toml
[packages]
# Consider pre-release versions when matching packages in repositories.
prereleases = false

[repo]
# Path to the local RuyiSDK metadata repository. Must be absolute or the setting
# will be ignored.
# If unset or empty, $XDG_CACHE_HOME/ruyi/packages-index is used.
local = ""
# Remote location of RuyiSDK metadata repository.
# If unset or empty, this default value is used.
remote = "https://github.com/ruyisdk/packages-index.git"
# Name of the branch to use.
# If unset or empty, this default value is used.
branch = "main"

[telemetry]
# Whether to collect telemetry information for improving RuyiSDK's developer
# experience, and whether to send the data periodically to RuyiSDK team.
# Valid values are `local`, `off` and `on` -- see the documentation for
# details.
#
# If unset or empty, this default value is used: data will be collected but
# nothing will get uploaded without explicit action by the user.
mode = "local"
```

### Environment variables

Currently the following environment variables are supported by `ruyi`:

* `RUYI_TELEMETRY_OPTOUT` -- boolean, whether to opt-out of telemetry.
* `RUYI_VENV` -- string, explicitly specifies the Ruyi virtual environment to use.

For boolean variables, the values `1`, `true`, `x`, `y` or `yes` (all case-insensitive)
are all treated as "true".

### Telemetry

The Ruyi package manager collects usage data in order to help us improve your
experience. It is collected by the RuyiSDK team and shared with the community.
You can opt-out of telemetry by setting the `RUYI_TELEMETRY_OPTOUT`
environment variable to any of `1`, `true`, `x`, `y` or `yes` using your
favorite shell.

> **NOTE**: Currently only the `local` and `off` modes are implemented. The
> server-side components of RuyiSDK are still under development, and has not
> been deployed yet. Consequently, no data will be uploaded for now.
>
> You will be notified at your next `ruyi update` when we are ready to
> do so, and you will have enough time to revise your configuration so as to
> prevent unintentional data uploads.

There are 3 telemetry modes available:

* `local`: data will be collected but not uploaded without user action.
* `off`: data will not be collected nor uploaded.
* `on`: data will be collected and periodically uploaded.

By default the `local` mode is active, which means every `ruyi` invocation
will record some non-sensitive information locally alongside various other
states of `ruyi`, but nothing will be uploaded.

You can change the telemetry mode by editing `ruyi`'s config file, or simply
by setting the `RUYI_TELEMETRY_OPTOUT` environment variable to any of the
values accepted as truthy.

<!-- We collect the following information with `ruyi`: -->

<!-- TODO: table of metrics -->

## License

Copyright &copy; 2023-2024 Institute of Software, Chinese Academy of Sciences (ISCAS).
All rights reserved.

`ruyi` is licensed under the [Apache 2.0 license](./LICENSE-Apache.txt).

The one-file binary distribution of `ruyi` contains code licensed under the
[Mozilla Public License 2.0](https://mozilla.org/MPL/2.0/).
You can get the respective project's sources from the project's official
website:

* [`certifi`](https://github.com/certifi/python-certifi): used unmodified

All trademarks referenced herein are property of their respective holders.
