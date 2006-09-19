#
# spec file for package grub (Version 0.97)
#
# Copyright (c) 2006 SUSE LINUX Products GmbH, Nuernberg, Germany.
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#
# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild
# usedforbuild    aaa_base acl attr audit-libs autoconf automake bash bind-libs bind-utils binutils bison bzip2 coreutils cpio cpp cpp41 cracklib cvs cyrus-sasl db diffutils e2fsprogs file filesystem fillup findutils flex gawk gcc gcc41 gdbm gdbm-devel gettext gettext-devel glibc glibc-devel glibc-locale gpm grep groff gzip info insserv klogd less libacl libattr libcom_err libgcc41 libltdl libmudflap41 libnscd libstdc++41 libtool libvolume_id libxcrypt libzio m4 make man mktemp module-init-tools ncurses ncurses-devel net-tools netcfg openldap2-client openssl pam pam-modules patch perl permissions popt procinfo procps psmisc pwdutils rcs readline rpm sed strace sysvinit tar tcpd texinfo timezone unzip util-linux vim zlib zlib-devel

# Commandline: 
Name:           grub
%ifarch x86_64
BuildRequires:  gcc41-32bit glibc-devel-32bit ncurses-32bit ncurses-devel-32bit
%endif
License:        GPL
Group:          System/Boot
Version:        0.97
Release:        22
Source0:        %{name}-%{version}.tar.gz
Source1:        installgrub
Source2:        grubonce
Patch0:         %{name}-%{version}-path-patch
Patch1:         use_ferror.diff
Patch2:         grub-R
Patch3:         bad-assert-sideeffect
Patch4:         %{name}-gfxmenu-v8.diff
Patch5:         reiser-unpack
Patch6:         chainloader-devicefix
Patch7:         %{name}-%{version}-devicemap.diff
Patch8:         grub-linux-setup-fix
Patch9:         fix-uninitialized
Patch10:        force-LBA-off.diff
Patch11:        gcc4-diff
Patch12:        %{name}-%{version}-initrdaddr.diff
Patch20:        stage2-dir-callback.diff
Patch21:        stage2-wildcard.diff
Patch22:        stage2-wildcard-zerowidth.diff
Patch23:        stage2-wildcard-doc.diff
Patch24:        grub-%{version}-protexec.patch
URL:            http://www.gnu.org/software/grub/grub.en.html
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Summary:        Grand Unified Boot Loader
PreReq:         fileutils sh-utils

%description
GNU GRUB is a multiboot boot loader. It was derived from GRUB. It is an
attempt to produce a boot loader for IBM PC-compatible machines that
has both the ability to be friendly to beginning or otherwise
nontechnically interested users and the flexibility to help experts in
diverse environments. It is compatible with Free/Net/OpenBSD and Linux.
It supports Win 9x/NT and OS/2 via chainloaders. It has a menu
interface and a command line interface.



Authors:
--------
    Alessandro Rubini <rubini@gnu.org>
    Chip Salzenberg <chip@valinux.com>
    Edmund GRIMLEY EVANS <edmundo@rano.demon.co.uk>
    Edward Killips <ekillips@triton.net>
    Gordon Matzigkeit <gord@fig.org>
    Jochen Hoenicke <jochen@gnu.org>
    Khimenko Victor <grub@khim.sch57.msk.ru>
    Klaus Reichl <Klaus.Reichl@alcatel.at>
    Michael Hohmuth <hohmuth@innocent.com>
    OKUJI Yoshinori <okuji@gnu.org>
    Pavel Roskin <proski@gnu.org>

%debug_package
%prep
%setup
rm -f acconfig.h || true
%patch -p1 -E
%patch1
%patch2 -p1
%patch3 -p1
%patch4
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
# Disable the wildcard feature
#%patch20 -p1
#%patch21 -p1
#%patch22 -p1
#%patch23 -p1
%patch24 -p1

%build
perl -pi -e 's,/usr/share/grub/i386-pc,/usr/lib/grub,' docs/grub.texi
%{?suse_update_config:%{suse_update_config -l -f . }}
autoreconf --force --install
%ifarch x86_64
  EXTRACFLAGS=' -fno-strict-aliasing -minline-all-stringops -m32 -fno-asynchronous-unwind-tables '
%else
  EXTRACFLAGS=' -fno-strict-aliasing -minline-all-stringops'
%endif  
CFLAGS="$RPM_OPT_FLAGS -Os -DNDEBUG -W -Wall -Wpointer-arith $EXTRACFLAGS" ./configure \
  --prefix=/usr --infodir=%{_infodir} --mandir=%{_mandir} --datadir=/usr/lib \
  --disable-auto-linux-mem-opt --enable-diskless \
  --enable-{3c50{3,7},3c5{0,2}9,3c595,3c90x,cs89x0,davicom,depca,eepro{,100},epic100} \
  --enable-{exos205,lance,ne,ne2100,ni{50,52,65}00,ns8390} \
  --enable-{rtl8139,sk-g16,smc9000,tiara,tulip,via-rhine,w89c840,wd} 
make
(cd stage2; mv nbgrub pxegrub ..)
mv stage2/stage2{,.netboot}
make clean
CFLAGS="$RPM_OPT_FLAGS -Os -DNDEBUG -W -Wall -Wpointer-arith $EXTRACFLAGS" ./configure \
  --prefix=/usr --infodir=%{_infodir} --mandir=%{_mandir} --datadir=/usr/lib \
  --disable-auto-linux-mem-opt 
make

%install
[ "$RPM_BUILD_ROOT" != "" -a -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT;
make -k DESTDIR=$RPM_BUILD_ROOT install 
mkdir -p $RPM_BUILD_ROOT/boot/grub
ln -sfn . $RPM_BUILD_ROOT/boot/boot
(cd $RPM_BUILD_ROOT/usr/lib/grub && mv *-suse/* . && rmdir *-suse) >/dev/null 2>&1 || true
cp -p {nb,pxe}grub stage2/stage2{,.netboot} $RPM_BUILD_ROOT/usr/lib/grub
cp -p %{SOURCE2} $RPM_BUILD_ROOT/usr/sbin/.
# This fine script used to do everything at once, which
# isn't necessary any more with Yast2 support.
# Kept only for reference and historical reasons.
# install -o root -g root -m 744 %{SOURCE1} /usr/sbin
# grub-terminfo is irrelevant to us
rm -f $RPM_BUILD_ROOT/usr/sbin/grub-terminfo
rm -f $RPM_BUILD_ROOT/usr/share/man/man8/grub-terminfo*

%clean
[ "$RPM_BUILD_ROOT" != "" -a -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT;

%preun
%install_info --delete --info-dir=%{_infodir} %{_infodir}/%{name}.info.gz
%install_info --delete --info-dir=%{_infodir} %{_infodir}/multiboot.info.gz

%files
%defattr(-,root,root)
%doc BUGS NEWS TODO README THANKS AUTHORS INSTALL ChangeLog COPYING 
%docdir %{_infodir}
%docdir %{_mandir}
%docdir /usr/share/doc/packages/grub
%dir /boot/grub
/usr/bin/mbchk
%{_infodir}/grub*.gz
%{_infodir}/multiboot.info.gz
%{_mandir}/man1/mbchk.1.gz
%{_mandir}/man8/grub-install.8.gz
%{_mandir}/man8/grub.8.gz
%{_mandir}/man8/grub-md5-crypt.8.gz
/usr/sbin/grub
/usr/sbin/grubonce
/usr/sbin/grub-set-default
/usr/sbin/grub-install
/usr/sbin/grub-md5-crypt
#/usr/sbin/installgrub
%dir /boot/boot
/usr/lib/grub

%post
# should anything go wrong the system will remain bootable :
[ -e /boot/grub/stage2 ] && mv /boot/grub/stage2{,.old}
# copy especially stage2 over, because it will be modified in-place !
cp -p /usr/lib/grub/*stage1*   /boot/grub 2>/dev/null || true
cp -p /usr/lib/grub/*/*stage1* /boot/grub 2>/dev/null || true
#special hack for #46843
dd if=/usr/lib/grub/stage2 of=/boot/grub/stage2 bs=256k 
sync
# command sequence to update-install stage1/stage2.
# leave everything else alone !
[ -e /etc/grub.conf ] && /usr/sbin/grub --batch < /etc/grub.conf >/dev/null 2>&1
%install_info --info-dir=%{_infodir} %{_infodir}/%{name}.info.gz
%install_info --info-dir=%{_infodir} %{_infodir}/multiboot.info.gz
exit 0

%changelog -n grub
* Fri Aug 25 2006 - snwint@suse.de
- needs gcc41-32bit
* Thu Aug 24 2006 - snwint@suse.de
- support latest gfxmenu
* Mon Jul 17 2006 - snwint@suse.de
- extended gfxmenu interface to pass options for 'module' lines (#160066)
- merged various gfxmenu patch fragments into one patch
* Thu Apr 20 2006 - duwe@suse.de
- fix incorrect DL contents e.g. on chainloader (fd0)+1
  (Bug #158072)
- initialize array in intel netcard probe (Bug #144171)
* Wed Jan 25 2006 - mls@suse.de
- converted neededforbuild to BuildRequires
* Thu Nov 24 2005 - snwint@suse.de
- support latest gfxboot
* Thu Nov 10 2005 - duwe@suse.de
-  update to 0.97
* Fri Sep 09 2005 - coolo@suse.de
- make grubonce shutup
* Fri Sep 02 2005 - duwe@suse.de
- Make grubonce work with the new 0.96 savedefault,
  (fixing bug #95082, and by coincidence 99185 along the way, too)
* Fri Jun 10 2005 - ro@suse.de
- fix variable type in last change
* Thu Jun 09 2005 - ro@suse.de
- fix gfx display (stackptr diff) (thanks to Steffen)
* Fri Apr 29 2005 - duwe@suse.de
- update to 0.96
- "grubonce" no handled differently
- re-do gcc4 fix (cleaner now)
- dropped rare NICs sis900 and natsemi in the process,
  update from etherboot pending anyways.
* Sat Apr 09 2005 - aj@suse.de
- Compile with GCC4.
* Wed Mar 02 2005 - duwe@suse.de
- force cache reloading after "embed", for
  the "setup" shortcut. This fixes Bug #66454
* Fri Feb 18 2005 - agruen@suse.de
- Disable the wildcard feature.
* Sun Feb 06 2005 - ro@suse.de
- fix build on i386
- use RPM_OPT_FLAGS
* Sat Feb 05 2005 - ro@suse.de
- use PROT_EXEC (from grub bug-tracking system)
* Fri Jan 28 2005 - snwint@suse.de
- updated gfxboot patch
* Wed Oct 06 2004 - sf@suse.de
- dd stage2 instead of copying it (#46843)
* Fri Oct 01 2004 - max@suse.de
- Added ncurses-devel-32bit and ncurses-devel-32bit to
  neededforbuild to make history and command completion work
  on x86_64 [Bug #46577].
* Thu Sep 30 2004 - duwe@suse.de
- try to defragment stage2 if it resides on reiserfs.
  This should fix sporadic failures we see.
* Thu Sep 30 2004 - agruen@suse.de
- Wildcard feature:
  + stage2-wildcard-zerowidth.diff: Allow zero-width matches (so
  that the asterisk in wildcard matches has the usual file glob
  sematics).
  + stage2-wildcard-doc.diff: Document the wildcard feature.
* Tue Sep 21 2004 - duwe@suse.de
- removed one ill side effect of assert(), most likely
  fixing blocker #44520
* Tue Sep 07 2004 - duwe@suse.de
- added "grubonce" script to demonstrate & ease "savedefault --once"
* Mon Sep 06 2004 - agruen@suse.de
- Fix usage of wrong variable in wildcard code.
* Sun Aug 22 2004 - agruen@suse.de
- stage2-dir-callback.diff: Make the dir command more flexible,
  and clean up a bit.
- stage2-wildcard.diff: Implement wildcard menu entries.
* Mon Jul 26 2004 - duwe@suse.de
- update to the latest version, 0.95
* Thu May 13 2004 - duwe@suse.de
- added -fno-strict-aliasing to CFLAGS, as suggested
  per autobuild.
* Thu May 13 2004 - duwe@suse.de
-  fix at least Bugs #32351,#36460,#34576,#38774 and #27486,
  maybe also #35262
* Fri Mar 05 2004 - duwe@suse.de
- fix bug #35352, the initrd patch only seemed to have gone into
  0.94, the semantics differ slightly :-(
* Mon Mar 01 2004 - duwe@suse.de
- quick fix for changed --datadir in 0.94,
  detected by automated build checks.
* Mon Mar 01 2004 - duwe@suse.de
- upgrade to 0.94
- integrate iso9660 FS
- network booting temporarily disabled
* Wed Jan 14 2004 - snwint@suse.de
- understand new gfxboot file format
* Sat Jan 10 2004 - adrian@suse.de
- add %%defattr
* Thu Aug 28 2003 - snwint@suse.de
- graphics patch had been accidentally disabled
* Thu Aug 14 2003 - duwe@suse.de
- another graphics consolidation, to allow
  modular maintenance
* Thu Jul 31 2003 - duwe@suse.de
- reconsolidated graphics patches
- fix for machines with > 1GB of mem
  (thanks to Karsten Keil for reporting/finding this)
- fix for hardware RAID device naming scheme
* Tue May 27 2003 - snwint@suse.de
- no graphics menu if 'savedefault --once' is used (#25356)
* Wed May 21 2003 - mmj@suse.de
- Don't package grub-terminfo
* Sat Mar 08 2003 - snwint@suse.de
- no graphics menu if 'hiddenmenu' is used (#23538)
* Thu Mar 06 2003 - kukuk@suse.de
- Remove not used cyrus-sasl from neededforbuild
* Wed Feb 19 2003 - duwe@suse.de
- use -minline-all-stringops to work around broken gcc
* Tue Feb 11 2003 - ro@suse.de
- combine the two postinstalls
* Mon Feb 10 2003 - mmj@suse.de
- Use %%install_info macros [#23420]
* Mon Feb 10 2003 - snwint@suse.de
- fixed evil bug in graphics patch
* Mon Feb 10 2003 - duwe@suse.de
- Now build network and non-network stage2 (Blocker #23502 )
- #19984 considered fixed now, too
* Sun Feb 09 2003 - snwint@suse.de
- updated graphics patch
* Thu Feb 06 2003 - duwe@suse.de
- update to 0.93 version
- patches rediffed accordingly
- gfx patches consolidated
- made patch to force LBA off (untested)
* Thu Jan 16 2003 - nadvornik@suse.cz
- fixed the 'valid preprocessing token' error
* Thu Nov 28 2002 - duwe@suse.de
- added an "important" security fix ;-)
  passwd not working along with gfxmenu is now
  made obvious and warned about.
- made grub compile with gcc-3.3 and hopefully up.
* Thu Nov 14 2002 - duwe@suse.de
  (candidate to PUTONFTP -- please test)
- imported totally rewritten memory layout
  handling from CVS. This should work around the
  broken nforce chipsets.
- made device.map more robust:
  * use /boot/grub/device.map by default if it exists
  * erroneous lines are now skipped, and don't lead to
  no device.map at all any more.
* Thu Oct 10 2002 - kukuk@suse.de
- remove requires from bootsplash
* Wed Sep 11 2002 - adrian@suse.de
- remove PreReq to itself
* Tue Sep 10 2002 - duwe@suse.de
- added --disable-auto-linux-mem-opt to ./configure options.
  This prevents grub from arbitrarily adding "mem=" to kernel opts.
  This anachronism was necessary for some 2.2 Linux kernels, and
  breaks on MXT machines (#19288).
* Fri Sep 06 2002 - duwe@suse.de
- added "lilo -R" feature on strong popular demand (#18538)
* Tue Sep 03 2002 - snwint@suse.de
- fixed Requires
* Tue Aug 27 2002 - snwint@suse.de
- graphics: free some memory before loading kernel (#18291)
* Mon Aug 26 2002 - sf@suse.de
- add glibc-devel-32bit to compile on x86_64
* Thu Aug 22 2002 - sf@suse.de
- added x86_64
- compile with -m32 -fno-unwind-asynchronous-tables on x86_64
* Tue Aug 20 2002 - mmj@suse.de
- Correct PreReq
* Wed Jul 24 2002 - duwe@suse.de
- converted to safe update scheme using /etc/grub.conf
  *stage* are now copied from /usr/lib/grub [FHS compliant]
  to /boot/grub and remain functioning after uninstall.
  Now configurable with next Yast2; remove previous versions
  with "rpm -e", from here on "rpm -U" simply works.
- grub shell & friends moved to /usr/sbin
  (you already have that functionality w/ GRUB even before
  the kernel is booted, save for a mounted root FS)
* Thu Jul 18 2002 - snwint@suse.de
- basic graphics patch
* Thu Jun 20 2002 - stepan@suse.de
- update to 0.92 (bugfix release)
* Thu Apr 04 2002 - pthomas@suse.de
- Fixed to build with new autoconf/automake.
* Fri Feb 01 2002 - pthomas@suse.de
- Update to 0.91
- Clean up spec file.
- Handle the chase of /boot not being on its own partition correctly.
* Mon Mar 19 2001 - tw@suse.de
- switched to grub 0.5.96.1 so the patch of device.c is no longer needed
- build --recheck into the installgrub-script
* Mon Jan 15 2001 - tw@suse.de
- Don't install the stage bootloaders in /usr/share as FHS
  prohibits doing so.
- Because the stage-bootloaders are not in /usr/share, they have
  to be copied by "grub-install".
- Added a new script to ./util "installgrub", which automatically
  searches the most common partition-types, the kernels and the initrds
  and installs the bootmanager without action by the user.
- There was a bug in ./lib/device.c, that causes a DISK WRITE ERROR.
  It is fixed now. (Only a O_RDONLY needed to be changed to O_RDRW)
