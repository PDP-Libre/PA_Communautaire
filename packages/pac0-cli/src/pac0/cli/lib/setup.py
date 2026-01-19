# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
import subprocess
from packaging.version import Version
from packaging.specifiers import SpecifierSet
import re

# cf https://peps.python.org/pep-0440/#version-specifiers
SPEC_SPECIAL_CHARS = "~=!<>"

# ~=: Compatible release clause
# ==: Version matching clause
# !=: Version exclusion clause
# <=, >=: Inclusive ordered comparison clause
# <, >: Exclusive ordered comparison clause
# ===: Arbitrary equality clause
def _version_strip(version: str | None) -> str:
    if version:
        for char in SPEC_SPECIAL_CHARS:
            version = version.replace(char, "")
    return version or ""


@dataclass
class SetupTool:
    name: str
    version: str | None = None
    checked_version: str | None = None
    version_get: str | None = None
    install: str | None = None

    def _current_version_extract(
        self,
    ) -> str:
        if self.version_get is None:
            return "0.0.0"
        try:
            query = subprocess.run(
                self.version_get.strip(),
                shell=True,
                stdout=subprocess.PIPE,
                # cwd=cwd,
                executable="/bin/bash",
                check=True,
                #on_error="print_ignore",
                #extra_envvars=extra_envvars,
            )
            version_current = query.stdout.decode().strip()
        except subprocess.CalledProcessError:
            return "0.0.0"
        # print('version_current====', version_current)
        match = re.search(r"(\d+\.\d+\.\d+)", version_current)
        self.checked_version = match.group(0) if match else "0.0.0"
        return self.checked_version

    # see https://packaging.pypa.io/en/stable/specifiers.html#usage
    def _version_valid(
        self,
        version: str | None,
    ) -> bool:
        if self.version:
            version = version or "0.0.0"
            if self.version[0] in SPEC_SPECIAL_CHARS:
                v = Version(version)
                v_spec = SpecifierSet(self.version or "0.0.0")
                return v in v_spec
            else:
                return self.version in version
        else:
            return True

    def setup(
        self,
    ):
        version_current = self._current_version_extract()
        # if version_current is None:
        if not self._version_valid(version_current) and self.install:
            print(f"Installing {self.name}{self.version} ...")

            cmd = f"""
                    pushd /tmp
                    {self.install.format(version=_version_strip(self.version))}
                    popd
                """.strip()
            #print(cmd)
            subprocess.run(
                cmd,
                shell=True,
                executable="/bin/bash",
            )
            version_current = self._current_version_extract()

    def check(
        self,
    ) -> bool:
        version_current = self._current_version_extract()
        valid = self._version_valid(version_current)
        if valid:
            print(f"{self.name}{self.version} ok (found {version_current})")
        else:
            print(
                f"{self.name}{self.version} not found ! (found {version_current})"
                )
        return valid


tools: list[SetupTool] = [
    SetupTool(
        name="build-essential",
        version=">=12.10",
        install="""
            apt update
            apt install --yes build-essential
        """,
        version_get="""apt show build-essential | grep Version | cut -d: -f2 | xargs""",
    ),
    SetupTool(
        name="git",
        version=">=2.39.5",
        install="""
            apt update
            apt install --yes git unzip wget  
        """,
        version_get="""git -v""",
    ),
    SetupTool(
        name="nats-cli",
        version=">=0.3.0",
        install="""
            wget https://github.com/nats-io/natscli/releases/download/v{version}/nats-{version}-linux-amd64.zip
            unzip nats-*-linux-amd64.zip
            mv nats-*-linux-amd64/nats /usr/local/bin/
            rm -Rf nats-*-linux-amd64*
        """,
        version_get="nats --version",
    ),
    SetupTool(
        name="nats-server",
        version=">=2.12.3",
        install="""
            wget https://github.com/nats-io/nats-server/releases/download/v{version}/nats-server-v{version}-linux-amd64.tar.gz
            tar xvf nats-server-v*-linux-amd64.tar.gz
            mv nats-server-v*-linux-amd64/nats-server /usr/local/bin/
            rm -Rf nats-server-v*-linux-amd64*
        """,
        version_get="nats-server -v",
    ),
    SetupTool(
        name="hx",
        version=">=25.07.1",
        install="""
            curl -sLO "https://github.com/helix-editor/helix/releases/download/{version}/helix-{version}-x86_64-linux.tar.xz"
            tar xf helix-{version}-x86_64-linux.tar.xz
            rm helix-{version}-x86_64-linux.tar.xz
            sudo mv helix-{version}-x86_64-linux/hx /usr/local/bin/
            mkdir -p ~/.config/helix/runtime
            mv helix-{version}-x86_64-linux/runtime ~/.config/helix/runtime
            rm -Rf helix-{version}-x86_64-linux
        """,
        version_get="hx --version",
    ),
    SetupTool(
        name="k9s",
        version=">=0.50.4",
        install="""
            curl -sLO "https://github.com/derailed/k9s/releases/download/v{version}/k9s_Linux_amd64.tar.gz"
            tar xf k9s_Linux_amd64.tar.gz
            sudo mv k9s /usr/local/bin/
        """,
        version_get="k9s version",
    ),
    SetupTool(
        name="kubectl",
        # curl -L -s https://dl.k8s.io/release/stable.txt
        version=">=1.35.0",
        install="""
            curl -LO "https://dl.k8s.io/release/v{version}/bin/linux/amd64/kubectl"
            chmod a+x kubectl
            sudo mv kubectl /usr/local/bin/
        """,
        version_get="""kubectl version --client""",
    ),
    SetupTool(
        name="rclone",
        version=">=1.69.2",
        install="""
            curl -sLO "https://github.com/rclone/rclone/releases/download/v1.69.2/rclone-v1.69.2-linux-amd64.zip"
            unzip rclone-v1.69.2-linux-amd64.zip
            sudo mv rclone-v1.69.2-linux-amd64/rclone  /usr/local/bin/
        """,
        version_get="""rclone version""",
    ),
    SetupTool(
        name="typst",
        version=">=0.13.1",
        install="""
            curl -LO "https://github.com/typst/typst/releases/download/v{version}/typst-x86_64-unknown-linux-musl.tar.xz"
            tar xvf typst-x86_64-unknown-linux-musl.tar.xz
            sudo mv typst-x86_64-unknown-linux-musl/typst /usr/local/bin/
            rm -Rf typst-x86_64-unknown-linux-musl
        """,
        version_get="""typst --version""",
    ),
]
