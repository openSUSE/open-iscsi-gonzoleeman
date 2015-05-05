#
# Makefile for the Open-iSCSI Initiator
#

# if you are packaging open-iscsi, set this variable to the location
# that you want everything installed into.
DESTDIR ?= 

prefix = /usr
exec_prefix = /
sbindir = $(exec_prefix)/sbin
bindir = $(exec_prefix)/bin
mandir = $(prefix)/share/man
etcdir = /etc
initddir = $(etcdir)/init.d
mkinitrd = $(exec_prefix)/lib/mkinitrd/scripts
rulesdir = $(etcdir)/udev/rules.d

MANPAGES = doc/iscsid.8 doc/iscsiadm.8 doc/iscsi_discovery.8 \
	doc/iscsi_fw_login.8
PROGRAMS = usr/iscsid usr/iscsiadm utils/iscsi_discovery utils/iscsi-iname
SCRIPTS = utils/iscsi_discovery utils/iscsi_offload utils/iscsi-gen-initiatorname \
	utils/iscsi_fw_login
INSTALL = install
ETCFILES = etc/iscsid.conf
IFACEFILES = etc/iface.example
OPTFLAGS ?= -O2 -g
RULESFILES =  utils/50-iscsi-firmware-login.rules 

# Random comments:
# using '$(MAKE)' instead of just 'make' allows make to run in parallel
# over multiple makefile.

all: user

user: utils/open-isns/Makefile
	$(MAKE) -C utils/open-isns
	$(MAKE) -C utils/sysdeps
	$(MAKE) -C utils/fwparam_ibft
	$(MAKE) -C usr
	$(MAKE) -C utils
	@echo
	@echo "Compilation complete                 Output file"
	@echo "-----------------------------------  ----------------"
	@echo "Built iSCSI daemon:                  usr/iscsid"
	@echo "Built management application:        usr/iscsiadm"
	@echo "Built boot tool:                     usr/iscsistart"
	@echo
	@echo "Read README file for detailed information."

utils/open-isns/Makefile: utils/open-isns/configure utils/open-isns/Makefile.in
	cd utils/open-isns; ./configure CFLAGS="$(OPTFLAGS)" --with-security=no

kernel: force
	$(MAKE) -C kernel
	@echo "Kernel Compilation complete          Output file"
	@echo "-----------------------------------  ----------------"
	@echo "Built iSCSI Open Interface module:   kernel/scsi_transport_iscsi.ko"
	@echo "Built iSCSI library module:          kernel/libiscsi.ko"
	@echo "Built iSCSI over TCP library module: kernel/libiscsi_tcp.ko"
	@echo "Built iSCSI over TCP kernel module:  kernel/iscsi_tcp.ko"

force: ;

clean:
	$(MAKE) -C utils/sysdeps clean
	$(MAKE) -C utils/fwparam_ibft clean
	$(MAKE) -C utils clean
	$(MAKE) -C usr clean
	$(MAKE) -C kernel clean
	$(MAKE) -C utils/open-isns clean
	$(MAKE) -C utils/open-isns distclean

# this is for safety
# now -jXXX will still be safe
# note that make may still execute the blocks in parallel
.NOTPARALLEL: install_user install_programs install_initd \
	install_initd_suse install_initd_redhat install_initd_debian \
	install_etc install_iface install_doc install_kernel install_iname

install: install_programs install_doc install_etc \
	install_initd install_iname install_iface

install_user: install_programs install_doc install_etc \
	install_initd install_iface install_udev_rules

install_udev_rules:
	$(INSTALL) -d $(DESTDIR)$(rulesdir)
	$(INSTALL) -m 644 $(RULESFILES) $(DESTDIR)/$(rulesdir)

install_programs:  $(PROGRAMS) $(SCRIPTS)
	$(INSTALL) -d $(DESTDIR)$(sbindir)
	$(INSTALL) -m 755 $^ $(DESTDIR)$(sbindir)

# ugh, auto-detection is evil
# Gentoo maintains their own init.d stuff
install_initd:
	if [ -f /etc/debian_version ]; then \
		$(MAKE) install_initd_debian ; \
	elif [ -f /etc/redhat-release ]; then \
		$(MAKE) install_initd_redhat ; \
	elif [ -f /etc/SuSE-release ]; then \
		$(MAKE) install_initd_suse ; \
	fi

# these are external targets to allow bypassing distribution detection
install_initd_suse:
	$(INSTALL) -d $(DESTDIR)$(initddir)
	$(INSTALL) -m 755 etc/initd/initd.suse \
		$(DESTDIR)$(initddir)/open-iscsi
	$(INSTALL) -m 755 etc/initd/boot.suse \
		$(DESTDIR)$(initddir)/boot.open-iscsi
	$(INSTALL) -d $(DESTDIR)$(mkinitrd)
	$(INSTALL) -m 755 etc/mkinitrd/mkinitrd-boot.sh \
		$(DESTDIR)$(mkinitrd)/boot-iscsi.sh
	$(INSTALL) -m 755 etc/mkinitrd/mkinitrd-setup.sh \
		$(DESTDIR)$(mkinitrd)/setup-iscsi.sh
	$(INSTALL) -m 755 etc/mkinitrd/mkinitrd-stop.sh \
		$(DESTDIR)$(mkinitrd)/boot-killiscsi.sh

install_initd_redhat:
	$(INSTALL) -d $(DESTDIR)$(initddir)
	$(INSTALL) -m 755 etc/initd/initd.redhat \
		$(DESTDIR)$(initddir)/open-iscsi

install_initd_debian:
	$(INSTALL) -d $(DESTDIR)$(initddir)
	$(INSTALL) -m 755 etc/initd/initd.debian \
		$(DESTDIR)$(initddir)/open-iscsi

install_iface: $(IFACEFILES)
	$(INSTALL) -d $(DESTDIR)$(etcdir)/iscsi/ifaces
	$(INSTALL) -m 644 $^ $(DESTDIR)$(etcdir)/iscsi/ifaces

install_etc: $(ETCFILES)
	if [ ! -f $(DESTDIR)/etc/iscsi/iscsid.conf ]; then \
		$(INSTALL) -d $(DESTDIR)$(etcdir)/iscsi ; \
		$(INSTALL) -m 644 $^ $(DESTDIR)$(etcdir)/iscsi ; \
	fi

install_doc: $(MANPAGES)
	$(INSTALL) -d $(DESTDIR)$(mandir)/man8
	$(INSTALL) -m 644 $^ $(DESTDIR)$(mandir)/man8

install_kernel:
	$(MAKE) -C kernel install_kernel

install_iname:
	if [ ! -f $(DESTDIR)/etc/iscsi/initiatorname.iscsi ]; then \
		echo "InitiatorName=`$(DESTDIR)/sbin/iscsi-iname`" > $(DESTDIR)/etc/iscsi/initiatorname.iscsi ; \
		echo "***************************************************" ; \
		echo "Setting InitiatorName to `cat $(DESTDIR)/etc/iscsi/initiatorname.iscsi`" ; \
		echo "To override edit $(DESTDIR)/etc/iscsi/initiatorname.iscsi" ; \
		echo "***************************************************" ; \
	fi

depend:
	for dir in usr utils utils/fwparam_ibft; do \
		$(MAKE) -C $$dir $@; \
	done

# vim: ft=make tw=72 sw=4 ts=4:
