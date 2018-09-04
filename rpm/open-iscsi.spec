#
# spec file for package open-iscsi
#
# Copyright (c) 2018 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


%define iscsi_release 876-suse
Name:           open-iscsi
Version:        2.0.876
Release:        0
Summary:        Linux Open-iSCSI Software Initiator
License:        GPL-2.0-or-later
Group:          Productivity/Networking/Other
Url:            http://www.open-iscsi.com
Source:         %{name}-2.0.%{iscsi_release}.tar.bz2
Patch1:         %{name}-SUSE-latest.diff.bz2
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  bison
BuildRequires:  db-devel < 5
BuildRequires:  fdupes
BuildRequires:  flex
BuildRequires:  libkmod-devel
BuildRequires:  libmount-devel
BuildRequires:  libtool
BuildRequires:  make
BuildRequires:  open-isns-devel
BuildRequires:  openssl-devel
BuildRequires:  suse-module-tools
BuildRequires:  systemd
Requires(post): coreutils
Requires:       libopeniscsiusr0_1_0 = %{version}
%{?systemd_requires}

%description
Open-iSCSI is a transport independent implementation of RFC 3720
iSCSI. It is partitioned into user and kernel parts.

The kernel portion of Open-iSCSI implements the iSCSI data path (that
is, iSCSI Read and iSCSI Write), and consists of two loadable
modules: iscsi_if.ko and iscsi_tcp.ko.

The user space part contains the entire control plane: configuration
manager, iSCSI Discovery, Login and Logout processing,
connection-level error processing, Nop-In and Nop-Out handling. It
comes with a daemon process called iscsid, and a management utility,
iscsiadm.

%package -n libopeniscsiusr0_1_0
Version:        2.0.876
Release:        0
Summary:        Userspace iSCSI API
Group:          System/Libraries

%description -n libopeniscsiusr0_1_0
The iSCSI userspace API from the open-iscsi project.

%package -n iscsiuio
Version:        0.7.8.2
Release:        0
Summary:        Linux Broadcom NetXtremem II iscsi server
Group:          Productivity/Networking/Other
Requires:       logrotate

%description -n iscsiuio
This tool is to be used in conjunction with the Broadcom NetXtreme II Linux
driver (Kernel module name: "bnx2" and "bnx2x"), Broadcom CNIC driver,
and the Broadcom iSCSI driver (Kernel module name: "bnx2i").
This user space tool is used in conjunction with the following
Broadcom Network Controllers:

* bnx2:  BCM5706, BCM5708, BCM5709 devices
* bnx2x: BCM57710, BCM57711, BCM57711E, BCM57712, BCM57712E,
         BCM57800, BCM57810, BCM57840 devices

This utility will provide the ARP and DHCP functionality for the iSCSI offload.
The communication to the driver is done via Userspace I/O (Kernel module name
"uio").

%package devel
Version:        2.0.876
Release:        0
Summary:        Linux open-iscsi user-level library and include files
Group:          Development/Libraries/C and C++
Requires:       %{name}

%description devel
This development package contains the open-iscsi user-level library
include files and documentation. These are used to compile against
the libopeniscsiusr library.

%prep
%setup -q -n %{name}-2.0.%{iscsi_release}
%patch1 -p1

%build
make %{?_smp_mflags} OPTFLAGS="%{optflags} -fno-strict-aliasing -DOFFLOAD_BOOT_SUPPORTED -DUSE_KMOD -I/usr/include/kmod -DLOCK_DIR=\\\"%{_sysconfdir}/iscsi\\\"" LDFLAGS="-lkmod" user
cd iscsiuio
touch AUTHORS NEWS
autoreconf --install
%configure --sbindir=/sbin
make %{?_smp_mflags} CFLAGS="%{optflags}"

%install
make DESTDIR=%{buildroot} install_user
# install service files
make DESTDIR=%{buildroot} install_service_suse
# create rc symlinks
[ -d %{buildroot}%{_sbindir} ] || mkdir -p %{buildroot}%{_sbindir}
ln -s %{_sbindir}/service %{buildroot}%{_sbindir}/rciscsi
ln -s %{_sbindir}/service %{buildroot}%{_sbindir}/rciscsid
ln -s %{_sbindir}/service %{buildroot}%{_sbindir}/rciscsiuio
(cd %{buildroot}/etc; ln -sf iscsi/iscsid.conf iscsid.conf)
touch %{buildroot}%{_sysconfdir}/iscsi/initiatorname.iscsi
install -m 0755 usr/iscsistart %{buildroot}/sbin
%make_install -C iscsiuio
%fdupes %{buildroot}/%{_prefix}

%post
%{?regenerate_initrd_post}
if [ ! -f %{_sysconfdir}/iscsi/initiatorname.iscsi ] ; then
    /sbin/iscsi-gen-initiatorname
fi
%{service_add_post iscsid.socket iscsid.service iscsi.service}

%posttrans
%{?regenerate_initrd_posttrans}

%postun
%{service_del_postun iscsid.socket iscsid.service iscsi.service}

%pre
%{service_add_pre iscsid.socket iscsid.service iscsi.service}

%preun
%{service_del_preun iscsid.socket iscsid.service iscsi.service}

%post   -n libopeniscsiusr0_1_0 -p /sbin/ldconfig
%postun -n libopeniscsiusr0_1_0 -p /sbin/ldconfig

%post -n iscsiuio
%{service_add_post iscsiuio.socket iscsiuio.service}

%postun -n iscsiuio
%{service_del_postun iscsiuio.socket iscsiuio.service}

%pre -n iscsiuio
%{service_add_pre iscsiuio.socket iscsiuio.service}

%preun -n iscsiuio
%{service_del_preun iscsiuio.socket iscsiuio.service}

%files
%dir %{_sysconfdir}/iscsi
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/iscsi/iscsid.conf
%ghost %{_sysconfdir}/iscsi/initiatorname.iscsi
%dir %{_sysconfdir}/iscsi/ifaces
%config %{_sysconfdir}/iscsi/ifaces/iface.example
%{_sysconfdir}/iscsid.conf
%{_unitdir}/iscsid.service
%{_unitdir}/iscsid.socket
%{_unitdir}/iscsi.service
%{_libexecdir}/systemd/system-generators/ibft-rule-generator
%{_sbindir}/rciscsi
%{_sbindir}/rciscsid
/sbin/iscsid
/sbin/iscsiadm
/sbin/iscsi-iname
/sbin/iscsistart
/sbin/iscsi-gen-initiatorname
/sbin/iscsi_offload
/sbin/iscsi_discovery
/sbin/iscsi_fw_login
%doc COPYING README
%{_mandir}/man8/iscsiadm.8%{ext_man}
%{_mandir}/man8/iscsid.8%{ext_man}
%{_mandir}/man8/iscsi_discovery.8%{ext_man}
%{_mandir}/man8/iscsistart.8%{ext_man}
%{_mandir}/man8/iscsi-iname.8%{ext_man}
%{_mandir}/man8/iscsi_fw_login.8%{ext_man}
%{_udevrulesdir}/50-iscsi-firmware-login.rules

%files -n libopeniscsiusr0_1_0
%{_libdir}/libopeniscsiusr.so*

%files -n iscsiuio
/sbin/iscsiuio
/sbin/brcm_iscsiuio
%{_mandir}/man8/iscsiuio.8%{ext_man}
%config %{_sysconfdir}/logrotate.d/iscsiuiolog
%{_unitdir}/iscsiuio.service
%{_unitdir}/iscsiuio.socket
%{_sbindir}/rciscsiuio

%files devel
%{_includedir}/libopeniscsiusr*.h
%{_mandir}/man3/*.3%{ext_man}

%changelog
