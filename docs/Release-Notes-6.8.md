---
layout: default
title: Release Notes - Mock 6.8
---

## [Release 6.8](https://rpm-software-management.github.io/mock/Release-Notes-6.8) - 2026-08-11


### Breaking changes

- The `%{pkgid}` field has been removed from the `package_state` plugin output
  in both `available_pkgs.log` and `installed_pkgs.log`.

### New features

- New `separate_check` config option to run `%check` as a separate rpmbuild
  phase (`-bk --short-circuit`).  This prevents `%check` scripts from modifying
  already built RPM artifacts.  Supported values: `off` (default),
  `best_effort`, and `enforce`.

- New `system_monitor` plugin for collecting various statistics during the build
  phase.

- Build-time opt-in: Polkit support files can be included and installed with
  Mock when built `--with=polkit`.

- Bash completion for `--localrepo` now offers directory completions.

- For AlmaLinux targets, Podman container image pulls now pass `--platform`
  for x86_64 sub-architecture variants (x86_64_v2, x86_64_v3, x86_64_v4).
  This is a temporary workaround for Podman not being able to auto-detect
  sub-architecture variants in OCI images.  The `oci_platform_map` config
  option is set unconditionally in the AlmaLinux templates; this means
  that e.g. a v2 bootstrap image is unintuitively pulled even on a v4 host
  when the target architecture is x86_64_v2 (normally bootstrap should be
  host-native).

- New `pivot_root_chroot` configuration option uses `pivot_root(2)` inside a
  private mount namespace to atomically swap the mount-namespace root to the
  chroot path.  This satisfies the kernel check that blocks
  `unshare(CLONE_NEWUSER)` after plain `chroot()`, allowing tools like
  pasta/passt that require user namespaces to work inside Mock buildroots.
  This is the same approach used by bubblewrap and other container runtimes.
  Requires `CAP_SYS_ADMIN` (available in `--privileged` containers); falls back
  to plain `chroot()` on failure.
  Set `config_opts['pivot_root_chroot'] = True` to enable.

- On newer build hosts (Fedora 44+ and EL 11+), Mock uses the
  [`useradd --root` option][issue#1285] instead of `--prefix` to better isolate
  it from the host system.  Specifically, this correctly resolves
  [subuid/subgid issues][issue#1354] (previously, we had to work around this
  problem by using in-chroot shadow-utils).

- The `unbreq` plugin now detects if a `BuildRequires` field is not installed on
  the system and in that case does not report it as unused.  This can happen if
  the `BuildRequires` field is a more complex logic formula (e.g. `(foo if bar)`
  and `bar` is not installed on the system).  This scenario is no longer reported
  as a warning but as info.

- System architecture detection now prefers `python3-libdnf5` over the
  deprecated `python3-dnf`.  If `python3-libdnf5` is not available, Mock falls
  back to `python3-dnf`, preserving functionality on both modern and older
  systems.

### Bugfixes

- Fix bash completion `--chain` handling — it is an option with no argument, not
  a synonym for `--root` ([issue#1729][]).

- The `buildroot_lock` plugin no longer crashes when the bootstrap image is
  unavailable.  The lockfile is now only populated with bootstrap metadata when
  `use_bootstrap_image` is enabled.  Also, `--calculate-build-dependencies` no
  longer overrides an explicit `--disable-plugin buildroot_lock`
  ([issue#1758][]).

- Mock now decodes percent-escaped local `file://` repository paths before
  checking them for bootstrap bind mounts.  This fixes bootstrap package-manager
  access to host-local repositories whose paths contain characters such as `@`
  and therefore appear escaped in file URIs ([PR#1728][]).

- The existence of `repoquery` is now tested in the bootstrap image instead of
  on the host.

- The `--allowerasing` argument is no longer passed to the dnf5 `download`
  command, which does not accept it.  This invalid argument is now excluded
  when invoking dnf `download` operations using `--dnf-cmd` or `--pm-cmd`.

- Fix the `package_state` plugin so `available_pkgs.log` is generated when
  `package_manager` is set to `dnf5` or `dnf4`, not only `dnf` or `microdnf`
  ([#1190][]).

- Podman image pull now has a per-attempt timeout (configurable via
  `bootstrap_image_pull_timeout` and `buildroot_image_pull_timeout`, default
  120 seconds) to prevent indefinite hangs and allow the retry logic to work.

- Mock now preserves the timestamp of `dnf.conf` and `yum.conf` inside the
  chroot when their content has not changed.  Previously, every Mock invocation
  rewrote these files unconditionally, which — combined with DNF's default
  `check_config_file_age=True` — caused repository metadata to be re-downloaded
  even when it was still valid ([issue#216][]).

- The `uidManager` is now reloaded with `chrootuid`/`chrootgid` from
  config after the configuration is loaded.  Previously, privilege
  dropping always used the calling user's identity, ignoring the
  configured chroot user ([#1731][]).

- Consolidate NS resolver munging logic, which was previously scattered across
  multiple locations.  This duplication made the logic difficult to follow and
  led to bugs, such as the one addressed in [PR#1697][].

- The `--spec` option now works with spec files that have restrictive
  permissions (e.g. `0600`).  Previously, `shutil.copy2()` preserved the
  source permissions inside the chroot, making the file unreadable by the
  `mockbuild` user ([#1300][]).

- The `unbreq` plugin no longer caches the mapping of a source RPM file to its
  `BuildRequires` fields, fixing a logic error where it would ignore later
  automatically generated `BuildRequires` fields when `BuildRequires`
  autogeneration is used.  Source RPMs are now scanned after each installation
  of `BuildRequires` fields.

- The `--verbose` option no longer duplicates the build log output into the root
  log.

- Mock defaults were changed to not pass `--allowerasing` option to the
  `dnf5 list` command.

- The `mock-hermetic-repo` tool now retries HTTP 503 (Service Unavailable)
  responses with exponential backoff, matching the existing retry handling for
  other transient HTTP errors.  Previously, a single 503 from an upstream
  repository (e.g. S3 throttling) would cause the entire RPM download to fail
  ([PR#1769][]).

### Mock Core Configs changes

- Add the Extensions repo to the Fedora ELN config (disabled by default).

- Use `cdn.opensuse.org` for baseurl repositories, matching the real
  distribution.

- Branch Fedora 45 configuration files from Rawhide, per the
  [Fedora 45 Schedule](https://fedorapeople.org/groups/schedule/f-45/f-45-all-tasks.html).

- Add configuration for Fedora 45 RISC-V.

- Add Mageia 10 (stable) and Mageia 11 (development) configs.  Move Mageia 8
  configs to EOL.

- Update openEuler 24.03 LTS chroot to SP4 and fix the source and
  update-source metalink repositories across all openEuler templates
  (20.03, 22.03, 24.03): the `path=` metalink form does not translate the
  `$releasever` dnf variable into the full mirror directory name, so it
  resolved to a non-existent path and silently broke `mock --sources`.

### Contributors

Following contributors contributed to this release:

 * Andrea Bolognani
 * Andrew Lukoshko
 * Chris Adams
 * Jani Välimaa
 * lichaoran
 * Lukáš Lipinský
 * Marian Koncek
 * Miroslav Suchý
 * Pavel Raiskup
 * Rahman Ajibade
 * Scott Hebert
 * Scott K Logan
 * Simone Caronni
 * Tomas Kopecek
 * Yaakov Selkowitz
 * Yanko Kaneti

Thank you!

[#1190]: https://github.com/rpm-software-management/mock/issues/1190
[#1300]: https://github.com/rpm-software-management/mock/issues/1300
[#1731]: https://github.com/rpm-software-management/mock/issues/1731
[issue#216]: https://github.com/rpm-software-management/mock/issues/216
[issue#1285]: https://github.com/rpm-software-management/mock/issues/1285
[issue#1354]: https://github.com/rpm-software-management/mock/issues/1354
[issue#1729]: https://github.com/rpm-software-management/mock/issues/1729
[issue#1758]: https://github.com/rpm-software-management/mock/issues/1758
[PR#1697]: https://github.com/rpm-software-management/mock/pull/1697
[PR#1728]: https://github.com/rpm-software-management/mock/pull/1728
[PR#1769]: https://github.com/rpm-software-management/mock/pull/1769
