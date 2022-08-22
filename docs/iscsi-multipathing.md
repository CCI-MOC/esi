# ESI iSCSI multipathing

ESI supports the use of iSCSI multipathing when booting from volume. This document describes how to configure multipathing.

## Configuring multipathing

When a node is booted from volume, ESI will provide 2 paths for the volume.

```
[root@host-10-21-0-155 ~]# lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda      8:0    0 372G  0 disk
sdb      8:0    0 25G  0 disk
└─sdb1   8:2    0 25G  0 part /
sdc      8:16   0 25G  0 disk
└─sdc2   8:18   0 25G  0 part
```

Note that the rootfs `/` is only on `sdb` and not on `sdc`, while `sda` is the local drive.

At this stage

1. Install `device-mapper-multipath`,
2. Create a multipath config file with `mpathconf --enable --with_multipathd y`
3. Enable and start multipathd `systemctl enable --now multipathd`
4. Add the device wwid of the device with rootfs `/` to wwid file with `multipath -a /dev/sdb`. This will print the wwid that is added. In this case it'll be of `sdb` or `sdc` (it'll be the same for both of these).
4. Ensure that the only wwid listed in `/etc/multipath/wwid` and in `/etc/multipath/bindings` is of the device with the rootfs `/`. If there's some other unwanted wwid then delete those.
5. Generate initramfs with multipath. `dracut --force -H --add multipath --include /etc/multipath`.
6. Reboot your system.

This is how a correctly configured system will look like:

```
[root@host-10-21-0-155 ~]# lsblk
NAME        MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINT
sda           8:0    0  372G  0 disk
sdb           8:16   0   25G  0 disk
└─mpatha    253:0    0   25G  0 mpath
  └─mpatha1 253:1    0   25G  0 part  /
sdc           8:32   0   25G  0 disk
└─mpatha    253:0    0   25G  0 mpath
  └─mpatha1 253:1    0   25G  0 part  /
```

## Booting a node from a volume copy

It is trivial to boot a node from a copy of a volume.

1. Create a deep copy of a volume you want to boot another node from:

`openstack volume create --volume <volume-to-be-copied> --bootable --size <size> <name-of-volume-copy>`

2. Boot the new node from this copy.

3. If multipathing was configured on the volume being copied, then you'll need to reconfigure multipathing once the new node boots from the copied volume.


