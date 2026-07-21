For AlmaLinux targets, podman container image pulls now pass `--platform`
for x86_64 sub-architecture variants (x86_64_v2, x86_64_v3, x86_64_v4).
This is a temporary workaround for Podman not being able to auto-detect
sub-architecture variants in OCI images.  The `oci_platform_map` config
option is set unconditionally in the AlmaLinux templates; this means
that e.g. a v2 bootstrap image is unintuitively pulled even on a v4 host
when the target architecture is x86_64_v2 (normally bootstrap should be
host-native).
