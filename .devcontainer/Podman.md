# Podman

## VirtualBox

Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and then install [CentOS 7](http://isoredirect.centos.org/centos/7/isos/x86_64/) with a basic GUI server. This will work on newer versions, but 7 is what I've tested and documented.

[Install the VirtualBox Addons](https://slashterix.wordpress.com/2016/07/16/virtualbox-addon-installation-in-centos/) then set up a Shared Folder from your C: drive to the VM. Store your git checkout in that C drive folder so you can easily edit from VSCode in Windows.

Mount that shared folder with some extra options to make it play nice with podman. Here's my `/etc/fstab` entry where `local` is the name of the Shared Folder.

```fstab
local /home/sbarre/vb_local vboxsf defaults,uid=1000,gid=1000,umask=0022 0 0
```

## Setup CentOS

- [RHEL 7 Docs](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux_atomic_host/7/html-single/managing_containers/index#set_up_for_rootless_containers)
- [RHEL 8 Docs](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/building_running_and_managing_containers/assembly_starting-with-containers_building-running-and-managing-containers#proc_setting-up-rootless-containers_assembly_starting-with-containers)

Ensure [SELinux is disabled](https://access.redhat.com/solutions/3176) as it doesn't play nice with Virtual Box shared folders.

Ensure your user can open lots of files. Edit `/etc/security/limits.conf` to add a higher limit for your user.

```conf
sbarre - nofile 65536
```

Grant your user access to additional UID/GIDs

```bash
usermod --add-subuids 10000-75535 --add-subgids 10000-75535 sbarre
```

Install podman & git

```bash
yum install podman skopeo slirp4netns git
```

Ensure your user has sufficient disk space in `/home/sbarre/.local/share/containers/storage/`. In my VirtualBox I mounted an extra disk there.

```fstab
/dev/mapper/podman-podman /home/sbarre/.local/share/containers/ xfs defaults 0 0
```

## Run

You need to first clone the platform-gitops-repo into the `vb_local` directory you created earlier. Once you have cloned the repo, you need to cd into the directory and create an output directory via `mkdir output`. Run tests locally with podman. `make` will print out the help with options on which roles/cluster/files to generate for. If make works, you can then test this command by adding one of the environments after the final make (ei. make clab). Usually best to start with a `role/cluster` then expand up to the full suite before making your PR. Check the `/output` directory for the test files generated. You can then `oc create -f` those files to a test cluster to see if they would all work.

```bash
podman run --rm --ulimit nofile=65535:65535 \
  -v="$(pwd):/gen" \
  -v="$(pwd)/output:/tmp/platform-gitops-gen" \
  --env-file="$(pwd)/.devcontainer/devcontainer.env" \
  --workdir=/gen \
  ghcr.io/bcgov-platform-services/platform-gitops-container \
  make
```
