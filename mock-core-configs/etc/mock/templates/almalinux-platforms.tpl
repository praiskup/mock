# Temporary workaround for Podman not resolving x86_64 sub-architecture
# variants in OCI images.  See the discussion in PR #1733 and PR #1783:
# https://github.com/rpm-software-management/mock/pull/1733
# https://github.com/rpm-software-management/mock/pull/1783
config_opts['oci_platform_map'] = {
    'x86_64_v2': 'linux/amd64/v2',
    'x86_64_v3': 'linux/amd64/v3',
    'x86_64_v4': 'linux/amd64/v4',
}
