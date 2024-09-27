import glob
import os
import platform
import re
import subprocess
import sys
from typing import Mapping, Self, TypedDict
import uuid


class NodeInfo(TypedDict):
    v: int
    report_uuid: str

    arch: str
    ci: str
    libc_name: str
    libc_ver: str
    os: str
    os_release_id: str
    os_release_version_id: str
    shell: str


def probe_for_ci(os_environ: Mapping[str, str]) -> str:
    # https://www.appveyor.com/docs/environment-variables/
    if os_environ.get("APPVEYOR", "").lower() == "true":
        return "appveyor"
    # https://learn.microsoft.com/en-us/azure/devops/pipelines/build/variables?view=azure-devops&tabs=yaml#system-variables-devops-services
    elif os_environ.get("TF_BUILD", "") == "True":
        return "azure"
    # https://circleci.com/docs/variables/#built-in-environment-variables
    elif os_environ.get("CIRCLECI", "") == "true":
        return "circleci"
    # https://cirrus-ci.org/guide/writing-tasks/#environment-variables
    elif os_environ.get("CIRRUS_CI", "") == "true":
        return "cirrus"
    # https://gitea.com/gitea/act_runner/pulls/113
    # this should be checked before GHA because upstream maintains compatibility
    # with GHA by also providing GHA-style preset variables
    # TODO: also detect Forgejo
    elif os_environ.get("GITEA_ACTIONS", "") == "true":
        return "gitea"
    # https://gitee.com/help/articles/4358#article-header8
    elif "GITEE_PIPELINE_NAME" in os_environ:
        return "gitee"
    # https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/store-information-in-variables#default-environment-variables
    elif os_environ.get("GITHUB_ACTIONS", "") == "true":
        return "github"
    # https://docs.gitlab.com/ee/ci/variables/predefined_variables.html#predefined-variables
    elif os_environ.get("GITLAB_CI", "") == "true":
        return "gitlab"
    # https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-environment-variables
    # may have false-negatives but likely no false-positives
    elif "JENKINS_URL" in os_environ:
        return "jenkins"
    # https://gitee.com/openeuler/mugen
    # seems nothing except $OET_PATH is guaranteed
    elif "OET_PATH" in os_environ:
        return "mugen"
    # there seems to be no designated marker for openQA, test a couple of
    # hopefully ubiquitous variables to avoid going through the entire key set
    elif "OPENQA_CONFIG" in os_environ or "OPENQA_URL" in os_environ:
        return "openqa"
    # https://docs.travis-ci.com/user/environment-variables/#default-environment-variables
    elif os_environ.get("TRAVIS", "") == "true":
        return "travis"
    # https://docs.koderover.com/zadig/Zadig%20v3.1/project/build/
    # https://github.com/koderover/zadig/blob/v3.1.0/pkg/microservice/jobexecutor/core/service/job.go#L117
    elif os_environ.get("ZADIG", "") == "true":
        return "zadig"
    elif os_environ.get("CI", "") == "true":
        return "unidentified"
    return "maybe-not"


def probe_for_libc() -> tuple[str, str]:
    r = platform.libc_ver()
    if r[0] and r[1]:
        return r

    # check for musl ld.so at the upstream standard paths, because
    # platform.libc_ver() as of Python 3.12 does not know how to handle musl
    #
    # see https://wiki.musl-libc.org/guidelines-for-distributions
    musl_lds = glob.glob("/lib/ld-musl-*.so.1")
    if musl_lds:
        # run it and check for "Version *.*.*"
        # in case of multiple hits (hybrid-architecture sysroot?), hope the
        # first one that successfully returns something is the native one
        for p in musl_lds:
            if ver := _try_get_musl_ver(p):
                return ("musl", ver)

    return ("unknown", "unknown")


_MUSL_VERSION_RE = re.compile(br"(?m)^Version ([0-9.]+)$")


def _try_get_musl_ver(ldso_path: str) -> str | None:
    res = subprocess.run([ldso_path], stderr=subprocess.PIPE)
    if m := _MUSL_VERSION_RE.search(res.stderr):
        return m.group(1).decode("ascii", "ignore")
    return None


def probe_for_shell(os_environ: Mapping[str, str]) -> str:
    if x := os_environ.get("SHELL"):
        return os.path.basename(x)
    return "unknown"


def gather_node_info(report_uuid: uuid.UUID | None = None) -> NodeInfo:
    libc = probe_for_libc()
    os_release = platform.freedesktop_os_release()

    return {
        "v": 1,
        "report_uuid": report_uuid.hex if report_uuid is not None else uuid.uuid4().hex,
        "arch": platform.machine(),
        "ci": probe_for_ci(os.environ),
        "libc_name": libc[0],
        "libc_ver": libc[1],
        "os": sys.platform,
        "os_release_id": os_release.get("ID", "unknown"),
        "os_release_version_id": os_release.get("VERSION_ID", "unknown"),
        "shell": probe_for_shell(os.environ),
    }
