#!/usr/bin/env python3
"""
Fetches available Android SDK cmdline-tools versions from Google's repository
and creates/updates sdk-* folders and the CI workflow matrix accordingly.
"""

import json
import os
import re
import shutil
import stat
import sys
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_XML_URL = "https://dl.google.com/android/repository/repository2-3.xml"
WORKFLOW_PATH = os.path.join(REPO_ROOT, ".github", "workflows", "build.yml")

# Template files come from the newest existing sdk-* folder
TEMPLATE_FILES = [
    "app/src/main/AndroidManifest.xml",
    "app/src/main/java/com/premexab/sample/MainActivity.java",
    "gradle/wrapper/gradle-wrapper.jar",
    "gradlew",
    "gradlew.bat",
]

# AGP / Gradle / Java / compileSdk mapping based on cmdline-tools major version
def get_build_config(major_version):
    if major_version <= 9:
        return {"agp": "7.4.2", "gradle": "7.6.4", "java": "11", "compile_sdk": "33"}
    elif major_version <= 11:
        return {"agp": "8.1.4", "gradle": "8.4", "java": "17", "compile_sdk": "34"}
    elif major_version <= 13:
        return {"agp": "8.5.2", "gradle": "8.7", "java": "17", "compile_sdk": "34"}
    else:
        return {"agp": "8.7.3", "gradle": "8.12", "java": "17", "compile_sdk": "35"}


def fetch_versions():
    """Fetch all stable cmdline-tools versions from Google's repository XML."""
    print(f"Fetching {REPO_XML_URL}")
    with urllib.request.urlopen(REPO_XML_URL) as resp:
        content = resp.read().decode("utf-8")

    pattern = (
        r'<remotePackage path="cmdline-tools;([^"]+)"'
        r".*?<url>(commandlinetools-linux-(\d+)_latest\.zip)</url>"
        r".*?<host-os>linux</host-os>"
    )
    versions = {}
    for m in re.finditer(pattern, content, re.DOTALL):
        ver = m.group(1)
        build = m.group(3)
        # Skip pre-release versions and "latest" alias
        if any(x in ver for x in ["alpha", "beta", "rc"]) or ver == "latest":
            continue
        major = int(ver.split(".")[0])
        versions[major] = {"version": ver, "build": build}

    return versions


def get_existing_sdk_dirs():
    """Return set of major versions that already have sdk-* folders."""
    existing = set()
    for entry in os.listdir(REPO_ROOT):
        m = re.match(r"^sdk-(\d+)$", entry)
        if m and os.path.isdir(os.path.join(REPO_ROOT, entry)):
            existing.add(int(m.group(1)))
    return existing


def find_template_dir():
    """Find the highest existing sdk-* folder to use as template."""
    existing = sorted(get_existing_sdk_dirs())
    if not existing:
        return None
    return os.path.join(REPO_ROOT, f"sdk-{existing[-1]}")


def create_sdk_folder(major, build_num):
    """Create a new sdk-* folder with all necessary build files."""
    sdk_dir = os.path.join(REPO_ROOT, f"sdk-{major}")
    config = get_build_config(major)
    template_dir = find_template_dir()

    print(f"Creating sdk-{major} (build {build_num}, AGP {config['agp']}, Java {config['java']})")

    # Create directory structure
    os.makedirs(os.path.join(sdk_dir, "app", "src", "main", "java", "com", "premexab", "sample"), exist_ok=True)
    os.makedirs(os.path.join(sdk_dir, "gradle", "wrapper"), exist_ok=True)

    # Copy template files
    if template_dir:
        for f in TEMPLATE_FILES:
            src = os.path.join(template_dir, f)
            dst = os.path.join(sdk_dir, f)
            if os.path.exists(src):
                shutil.copy2(src, dst)

    # Make gradlew executable
    gradlew = os.path.join(sdk_dir, "gradlew")
    if os.path.exists(gradlew):
        os.chmod(gradlew, os.stat(gradlew).st_mode | stat.S_IEXEC)

    # Write settings.gradle.kts
    with open(os.path.join(sdk_dir, "settings.gradle.kts"), "w") as f:
        f.write(f"""pluginManagement {{
    repositories {{
        google()
        mavenCentral()
        gradlePluginPortal()
    }}
}}

dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{
        google()
        mavenCentral()
    }}
}}

rootProject.name = "sample-sdk-{major}"
include(":app")
""")

    # Write build.gradle.kts
    with open(os.path.join(sdk_dir, "build.gradle.kts"), "w") as f:
        f.write(f"""plugins {{
    id("com.android.application") version "{config['agp']}" apply false
}}
""")

    # Write app/build.gradle.kts
    with open(os.path.join(sdk_dir, "app", "build.gradle.kts"), "w") as f:
        f.write(f"""plugins {{
    id("com.android.application")
}}

android {{
    namespace = "com.premexab.sample"
    compileSdk = {config['compile_sdk']}

    defaultConfig {{
        applicationId = "com.premexab.sample"
        minSdk = 21
        targetSdk = {config['compile_sdk']}
        versionCode = 1
        versionName = "1.0"
    }}

    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_{config['java']}
        targetCompatibility = JavaVersion.VERSION_{config['java']}
    }}
}}
""")

    # Write gradle-wrapper.properties
    with open(os.path.join(sdk_dir, "gradle", "wrapper", "gradle-wrapper.properties"), "w") as f:
        f.write(f"""distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-{config['gradle']}-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")


def update_workflow(versions):
    """Regenerate the CI workflow with the current set of sdk-* folders."""
    existing = sorted(get_existing_sdk_dirs())

    # Build matrix entries
    matrix_entries = []
    for major in existing:
        if major in versions:
            build = versions[major]["build"]
            config = get_build_config(major)
            matrix_entries.append(
                f"          - {{ dir: sdk-{major}, build: '{build}', java: {config['java']} }}"
            )

    matrix_block = "\n".join(matrix_entries)

    workflow = f"""name: CI

on:
  push:
    branches: [main]
    tags: ['*']
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ${{{{ matrix.os }}}}
    strategy:
      matrix:
        os:
          - ubuntu-latest
          - windows-latest
          - macos-latest
        sdk:
{matrix_block}
    name: ${{{{ matrix.sdk.dir }}}} / ${{{{ matrix.os }}}}

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK ${{{{ matrix.sdk.java }}}}
        uses: actions/setup-java@v4
        with:
          java-version: ${{{{ matrix.sdk.java }}}}
          distribution: 'temurin'

      - name: Setup Android SDK
        uses: premex-ab/setup-android@main
        with:
          cmdline-tools-version: ${{{{ matrix.sdk.build }}}}

      - name: Build
        if: runner.os != 'windows'
        working-directory: ${{{{ matrix.sdk.dir }}}}
        run: ./gradlew --no-daemon assembleDebug

      - name: Build (Windows)
        if: runner.os == 'windows'
        working-directory: ${{{{ matrix.sdk.dir }}}}
        run: .\\gradlew.bat --no-daemon assembleDebug

  CI:
    needs: build
    if: always()
    runs-on: ubuntu-latest
    steps:
      - run: |
          if [[ "${{{{ needs.build.result }}}}" != "success" ]]; then
            exit 1
          fi
"""

    with open(WORKFLOW_PATH, "w") as f:
        f.write(workflow)

    print(f"Updated {WORKFLOW_PATH} with {len(matrix_entries)} SDK versions")


def main():
    versions = fetch_versions()
    print(f"Found {len(versions)} stable cmdline-tools versions: {sorted(versions.keys())}")

    existing = get_existing_sdk_dirs()
    print(f"Existing sdk-* folders: {sorted(existing)}")

    # Only add versions >= 7 (older ones are too ancient)
    new_versions = {k: v for k, v in versions.items() if k >= 7 and k not in existing}

    if not new_versions:
        print("No new versions to add")
    else:
        print(f"New versions to add: {sorted(new_versions.keys())}")
        for major in sorted(new_versions.keys()):
            create_sdk_folder(major, new_versions[major]["build"])

    # Always regenerate workflow to keep it in sync
    update_workflow(versions)

    if new_versions:
        # Output for GitHub Actions
        added = ",".join(str(v) for v in sorted(new_versions.keys()))
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"new_versions={added}\n")
                f.write("has_new=true\n")
        print(f"Added SDK versions: {added}")
    else:
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write("has_new=false\n")


if __name__ == "__main__":
    main()
