# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

Summary: The Linux kernel

# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%global released_kernel 1

# Save original buildid for later if it's defined
%if 0%{?buildid:1}
%global orig_buildid %{buildid}
%undefine buildid
%endif

%define RPMBuilderVer rpm-generic
###################################################################
# SubPackage parameter(s) below is/are for Thecus package using.
# The format is:
# %define SubPackage[N] <git repository> <tag>
###################################################################
%define SubPackage0 driver/thecus_drv_board 1.3.3
%define SubPackage1 driver/thecus_drv_iscsi 1.1.2
%define SubPackage2 driver/etron_drv_etxhci 1.0.1
%define SubPackage3 driver/loop-AES v3.6i.2

###################################################################
# Polite request for people who spin their own kernel rpms:
# please modify the "buildid" define in a way that identifies
# that the kernel isn't the stock distribution kernel, for example,
# by setting the define to ".local" or ".bz123456". This will be
# appended to the full kernel version.
#
# (Uncomment the '#' and both spaces below to set the buildid.)
#
%define buildid .ce23
###################################################################

# The buildid can also be specified on the rpmbuild command line
# by adding --define="buildid .whatever". If both the specfile and
# the environment define a buildid they will be concatenated together.
%if 0%{?orig_buildid:1}
%if 0%{?buildid:1}
%global srpm_buildid %{buildid}
%define buildid %{srpm_buildid}%{orig_buildid}
%else
%define buildid %{orig_buildid}
%endif
%endif

# baserelease defines which build revision of this kernel version we're
# building.  We used to call this fedora_build, but the magical name
# baserelease is matched by the rpmdev-bumpspec tool, which you should use.
#
# We used to have some extra magic weirdness to bump this automatically,
# but now we don't.  Just use: rpmdev-bumpspec -c 'comment for changelog'
# When changing base_sublevel below or going from rc to a final kernel,
# reset this by hand to 1 (or to 0 and then use rpmdev-bumpspec).
# scripts/rebase.sh should be made to do that for you, actually.
#
# For non-released -rc kernels, this will be prepended with "0.", so
# for example a 3 here will become 0.3
#
%global baserelease 1
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 2.6.22-rc7-git1 starts with a 2.6.21 base,
# which yields a base_sublevel of 21.
%define base_sublevel 39

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 0
# Is it a -stable RC?
%define stable_rc 0
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev .%{stable_update}
%define stable_base %{stable_update}
%if 0%{?stable_rc}
# stable RCs are incremental patches, so we need the previous stable patch
%define stable_base %(echo $((%{stable_update} - 1)))
%endif
%endif
%define rpmversion 2.6.%{base_sublevel}%{?stablerev}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
# The rc snapshot level
%define rcrev 7
# The git snapshot level
%define gitrev 6
# Set rpm version accordingly
%define rpmversion 2.6.%{upstream_sublevel}
%endif
# Nb: The above rcrev and gitrev values automagically define Patch00 and Patch01 below.

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# standard kernel
%define with_up        %{?_without_up:        0} %{?!_without_up:        1}
# kernel-smp (only valid for ppc 32-bit)
%define with_smp       %{?_without_smp:       0} %{?!_without_smp:       0}
# kernel-PAE (only valid for i686)
%define with_pae       %{?_without_pae:       0} %{?!_without_pae:       0}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     0}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       0}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# kernel-firmware
%define with_firmware  %{?_with_firmware:     1} %{?!_with_firmware:     0}
# tools/perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      0}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 0}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 0}
# Want to build a the vsdo directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 0}

# Build the kernel-doc package, but don't fail the build if it botches.
# Here "true" means "continue" and "false" means "fail the build".
%if 0%{?released_kernel}
%define doc_build_fail false
%else
%define doc_build_fail true
%endif

%define rawhide_skip_docs 1
%if 0%{?rawhide_skip_docs}
%define with_doc 0
%define doc_build_fail true
%endif

# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the smp kernel (--with smponly):
%define with_smponly   %{?_with_smponly:      1} %{?!_with_smponly:      0}
# Only build the pae kernel (--with paeonly):
%define with_paeonly   %{?_with_paeonly:      1} %{?!_with_paeonly:      0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}

# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 1

# Want to build a vanilla kernel build without any non-upstream patches?
%define with_vanilla %{?_with_vanilla: 1} %{?!_with_vanilla: 0}

# pkg_release is what we'll fill in for the rpm Release: field
%if 0%{?released_kernel}

%if 0%{?stable_rc}
%define stable_rctag .rc%{stable_rc}
%endif
%define pkg_release %{fedora_build}%{?stable_rctag}%{?buildid}%{?dist}

%else

# non-released_kernel
%if 0%{?rcrev}
%define rctag .rc%rcrev
%else
%define rctag .rc0
%endif
%if 0%{?gitrev}
%define gittag .git%gitrev
%else
%define gittag .git0
%endif
%define pkg_release 0%{?rctag}%{?gittag}.%{fedora_build}%{?buildid}%{?dist}

%endif

# The kernel tarball/base version
%define kversion 2.6.%{base_sublevel}

%define make_target bzImage

%define KVERREL %{version}-%{release}.%{_target_cpu}
%define hdrarch %_target_cpu
%define asmarch %_target_cpu

%if 0%{!?nopatches:1}
%define nopatches 0
%endif

%if %{with_vanilla}
%define nopatches 1
%endif

%if %{nopatches}
%define with_bootwrapper 0
%define variant -vanilla
%else
%define variant_fedora -fedora
%endif

%define using_upstream_branch 0
%if 0%{?upstream_branch:1}
%define stable_update 0
%define using_upstream_branch 1
%define variant -%{upstream_branch}%{?variant_fedora}
%define pkg_release 0.%{fedora_build}%{upstream_branch_tag}%{?buildid}%{?dist}
%endif

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# kernel-PAE is only built on i686.
%ifnarch i686
%define with_pae 0
%endif

# if requested, only build base kernel
%if %{with_baseonly}
%define with_smp 0
%define with_pae 0
%define with_debug 0
%endif

# if requested, only build smp kernel
%if %{with_smponly}
%define with_up 0
%define with_pae 0
%define with_debug 0
%endif

# if requested, only build pae kernel
%if %{with_paeonly}
%define with_up 0
%define with_smp 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%if %{debugbuildsenabled}
%define with_up 0
%define with_pae 0
%endif
%define with_smp 0
%define with_pae 0
%define with_perf 0
%endif

%define all_x86 i386 i686

%if %{with_vdso_install}
# These arches install vdso/ directories.
%define vdso_arches %{all_x86} x86_64 ppc ppc64
%endif

# Overrides for generic default options

# only ppc and alphav56 need separate smp kernels
%ifnarch ppc alphaev56
%define with_smp 0
%endif

# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64
%define with_debug 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_perf 0
%define all_arch_configs kernel-%{version}-*.config
%define with_firmware  %{?_with_firmware:     1} %{?!_with_firmware:     0}
%endif

# bootwrapper is only on ppc
%ifnarch ppc ppc64
%define with_bootwrapper 0
%endif

# sparse blows up on ppc64 alpha and sparc64
%ifarch ppc64 ppc alpha sparc64
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch %{all_x86}
%define asmarch x86
%define hdrarch i386
%define all_arch_configs kernel-%{version}-i?86*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc64
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc64*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x.config
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%define with_perf 0
%endif

%ifarch sparc64
%define asmarch sparc
%define all_arch_configs kernel-%{version}-sparc64*.config
%define make_target image
%define kernel_image arch/sparc/boot/image
%define image_install_path boot
%define with_perf 0
%endif

%ifarch sparcv9
%define hdrarch sparc
%endif

%ifarch ppc
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc{-,.}*config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%endif

%ifarch ia64
%define all_arch_configs kernel-%{version}-ia64*.config
%define image_install_path boot/efi/EFI/redhat
%define make_target compressed
%define kernel_image vmlinux.gz
%endif

%ifarch alpha alphaev56
%define all_arch_configs kernel-%{version}-alpha*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
%define image_install_path boot
%define hdrarch arm
%define make_target vmlinux
%define kernel_image vmlinux
%endif

%if %{nopatches}
# XXX temporary until last vdso patches are upstream
%define vdso_arches ppc ppc64
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%if %{nopatches}%{using_upstream_branch}
%define listnewconfig_fail 0
%else
%define listnewconfig_fail 1
%endif

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%define nobuildarches i386 s390 sparc sparcv9 %{arm}

%ifarch %nobuildarches
%define with_up 0
%define with_smp 0
%define with_pae 0
%define with_debuginfo 0
%define with_perf 0
%define _enable_debug_packages 0
%endif

%define with_pae_debug 0
%if %{with_pae}
%define with_pae_debug %{with_debug}
%endif

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3

# We moved the drm include files into kernel-headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools, initscripts >= 8.11.1-1, grubby >= 7.0.10-1
%define initrd_prereq  dracut >= 001-7

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:.%{1}}\
Provides: kernel-drm = 4.3.0\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-modeset = 1\
Provides: kernel-uname-r = %{KVERREL}%{?1:.%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
%if %{with_firmware}\
Requires(pre): kernel-firmware >= %{rpmversion}-%{pkg_release}\
%else\
Requires(pre): linux-firmware >= 20100806-2\
%endif\
Requires(post): /sbin/new-kernel-pkg\
Requires(preun): /sbin/new-kernel-pkg\
Conflicts: %{kernel_dot_org_conflicts}\
Conflicts: %{package_conflicts}\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}

Name: kernel%{?variant}
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
ExclusiveArch: noarch %{all_x86} x86_64 ppc ppc64 ia64 %{sparc} s390 s390x alpha alphaev56 %{arm}
ExclusiveOS: Linux

%kernel_reqprovconf

#
# List the packages used during the kernel build
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config
BuildRequires: net-tools
BuildRequires: xmlto, asciidoc
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel newt-devel python-devel perl(ExtUtils::Embed)
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb

%define fancy_debuginfo 0
%if %{with_debuginfo}
%if 0%{?fedora} >= 8 || 0%{?rhel} >= 6
%define fancy_debuginfo 1
%endif
%endif

%if %{fancy_debuginfo}
# Fancy new debuginfo generation introduced in Fedora 8.
BuildRequires: rpm-build >= 4.4.2.1-4
%define debuginfo_args --strict-build-id
%endif

Source0: linux-%{kversion}.tar.gz
Source1: kernel.config
Source2: thecus_drv_board.tar.gz
Source3: thecus_drv_iscsi.tar.gz
Source4: etron_drv_etxhci.tar.gz
Source5: loop-AES.tar.gz

BuildRoot: %{_tmppath}/kernel-%{KVERREL}-root

Requires: nas_img-tools >= 1.1.1-1

%description
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


%package doc
Summary: Various documentation bits found in the kernel source
Group: Documentation
%description doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.


%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package firmware
Summary: Firmware files used by the Linux kernel
Group: Development/System
# This is... complicated.
# Look at the WHENCE file.
License: GPL+ and GPLv2+ and MIT and Redistributable, no modification permitted
%if "x%{?variant}" != "x"
Provides: kernel-firmware = %{rpmversion}-%{pkg_release}
%endif
%description firmware
Kernel-firmware includes firmware files required for some devices to
operate.

%package bootwrapper
Summary: Boot wrapper files for generating combined kernel + initrd images
Group: Development/System
Requires: gzip
%description bootwrapper
Kernel-bootwrapper contains the wrapper code which makes bootable "zImage"
files combining both kernel and initial ramdisk.

%package debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
%description debuginfo-common-%{_target_cpu}
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf
This package provides the perf tool and the supporting documentation.

%package -n perf-debuginfo
Summary: Debug information for package perf
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf-debuginfo
This package provides debug information for package perf.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|XXX' -o perf-debuginfo.list}
%endif


#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
%define kernel_debuginfo_package() \
%package %{?1:%{1}-}debuginfo\
Summary: Debug information for package %{name}%{?1:-%{1}}\
Group: Development/Debug\
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-debuginfo-%{_target_cpu} = %{version}-%{release}\
AutoReqProv: no\
%description -n %{name}%{?1:-%{1}}-debuginfo\
This package provides debug information for package %{name}%{?1:-%{1}}.\
This is required to use SystemTap with %{name}%{?1:-%{1}}-%{KVERREL}.\
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '/.*/%%{KVERREL}%{?1:\.%{1}}/.*|/.*%%{KVERREL}%{?1:\.%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?1:.%{1}}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
Requires: perl\
%description -n kernel%{?variant}%{?1:-%{1}}-devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package %1\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
%kernel_reqprovconf\
%{expand:%%kernel_devel_package %1 %{!?-n:%1}%{?-n:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %1}\
%{nil}


# First the auxiliary packages of the main kernel package.
%kernel_devel_package
%kernel_debuginfo_package


# Now, each variant package.

%define variant_summary The Linux kernel compiled for SMP machines
%kernel_variant_package -n SMP smp
%description smp
This package includes a SMP version of the Linux kernel. It is
required only on machines with two or more CPUs as well as machines with
hyperthreading technology.

Install the kernel-smp package if your machine uses two or more CPUs.


%define variant_summary The Linux kernel compiled for PAE capable machines
%kernel_variant_package PAE
%description PAE
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.


%define variant_summary The Linux kernel compiled with extra debugging enabled for PAE capable machines
%kernel_variant_package PAEdebug
Obsoletes: kernel-PAE-debug
%description PAEdebug
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.


%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description debug
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.


%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_up}%{with_pae}
echo "Cannot build --with baseonly, up build is disabled"
exit 1
%endif
%endif

%if %{with_smponly}
%if !%{with_smp}
echo "Cannot build --with smponly, smp build is disabled"
exit 1
%endif
%endif

# more sanity checking; do it quietly
if [ "%{patches}" != "%%{patches}" ] ; then
  for patch in %{patches} ; do
    if [ ! -f $patch ] ; then
      echo "ERROR: Patch  ${patch##/*/}  listed in specfile but is missing"
      exit 1
    fi
  done
fi 2>/dev/null

patch_command='patch -p1 -F1 -s'
ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
%if !%{using_upstream_branch}
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME%%%%%{?variant}}.spec ; then
    if [ "${patch:0:10}" != "patch-2.6." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
%endif
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz) gunzip < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# don't apply patch if it's empty
ApplyOptionalPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  local C=$(wc -l $RPM_SOURCE_DIR/$patch | awk '{print $1}')
  if [ "$C" -gt 9 ]; then
    ApplyPatch $patch ${1+"$@"}
  fi
}

# we don't want a .config file when building firmware: it just confuses the build system
%define build_firmware \
   mv .config .config.firmware_save \
   make INSTALL_FW_PATH=$RPM_BUILD_ROOT/lib/firmware firmware_install \
   mv .config.firmware_save .config

# First we unpack the kernel tarball.
# If this isn't the first make prep, we use links to the existing clean tarball
# which speeds things up quite a bit.

# Update to latest upstream.
%if 0%{?released_kernel}
%define vanillaversion 2.6.%{base_sublevel}
# non-released_kernel case
%else
%if 0%{?rcrev}
%define vanillaversion 2.6.%{upstream_sublevel}-rc%{rcrev}
%if 0%{?gitrev}
%define vanillaversion 2.6.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
%define vanillaversion 2.6.%{base_sublevel}-git%{gitrev}
%else
%define vanillaversion 2.6.%{base_sublevel}
%endif
%endif
%endif

# %%{vanillaversion} : the full version name, e.g. 2.6.35-rc6-git3
# %%{kversion}       : the base version, e.g. 2.6.34

# Use kernel-%%{kversion}%%{?dist} as the top-level directory name
# so we can prep different trees within a single git directory.

# Build a list of the other top-level kernel tree directories.
# This will be used to hardlink identical vanilla subdirs.
sharedirs=$(find "$PWD" -maxdepth 1 -type d -name 'kernel-2.6.*' \
            | grep -x -v "$PWD"/kernel-%{kversion}%{?dist}) ||:

if [ ! -d kernel-%{kversion}%{?dist}/vanilla-%{vanillaversion} ]; then

  if [ -d kernel-%{kversion}%{?dist}/vanilla-%{kversion} ]; then

    # The base vanilla version already exists.
    cd kernel-%{kversion}%{?dist}

    # Any vanilla-* directories other than the base one are stale.
    for dir in vanilla-*; do
      [ "$dir" = vanilla-%{kversion} ] || rm -rf $dir &
    done

  else

    rm -f pax_global_header
    # Look for an identical base vanilla dir that can be hardlinked.
    for sharedir in $sharedirs ; do
      if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{kversion} ]] ; then
        break
      fi
    done
    if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{kversion} ]] ; then
%setup -q -n kernel-%{kversion}%{?dist} -c -T
      cp -rl $sharedir/vanilla-%{kversion} .
    else
%setup -q -n kernel-%{kversion}%{?dist} -c
      mv linux-%{kversion} vanilla-%{kversion}
    fi

  fi

%if "%{kversion}" != "%{vanillaversion}"

  for sharedir in $sharedirs ; do
    if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{vanillaversion} ]] ; then
      break
    fi
  done
  if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{vanillaversion} ]] ; then

    cp -rl $sharedir/vanilla-%{vanillaversion} .

  else

    # Need to apply patches to the base vanilla version.
    cp -rl vanilla-%{kversion} vanilla-%{vanillaversion}
    cd vanilla-%{vanillaversion}

# Update vanilla to the latest upstream.
# (non-released_kernel case only)
%if 0%{?rcrev}
    ApplyPatch patch-2.6.%{upstream_sublevel}-rc%{rcrev}.bz2
%if 0%{?gitrev}
    ApplyPatch patch-2.6.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.bz2
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
    ApplyPatch patch-2.6.%{base_sublevel}-git%{gitrev}.bz2
%endif
%endif

    cd ..

  fi

%endif

else

  # We already have all vanilla dirs, just change to the top-level directory.
  cd kernel-%{kversion}%{?dist}

fi

# Now build the fedora kernel tree.
if [ -d linux-%{kversion}.%{_target_cpu} ]; then
  # Just in case we ctrl-c'd a prep already
  rm -rf deleteme.%{_target_cpu}
  # Move away the stale away, and delete in background.
  mv linux-%{kversion}.%{_target_cpu} deleteme.%{_target_cpu}
  rm -rf deleteme.%{_target_cpu} &
fi

cp -rl vanilla-%{vanillaversion} linux-%{kversion}.%{_target_cpu}

# patch Thecus drivers to kernel source
tar xfz %{SOURCE2}
sh thecus_drv_board/setup.sh linux-%{kversion}.%{_target_cpu}
tar xfz %{SOURCE3}
sh thecus_drv_iscsi/setup.sh linux-%{kversion}.%{_target_cpu}
tar xfz %{SOURCE4}
sh etron_drv_etxhci/setup.sh linux-%{kversion}.%{_target_cpu}
tar xfz %{SOURCE5}
sh loop-AES/setup.sh linux-%{kversion}.%{_target_cpu}

cd linux-%{kversion}.%{_target_cpu}


# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

touch .scmversion


# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -exec rm -f {} \; >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{fancy_debuginfo}
# This override tweaks the kernel makefiles so that we run debugedit on an
# object before embedding it.  When we later run find-debuginfo.sh, it will
# run debugedit again.  The edits it does change the build ID bits embedded
# in the stripped object, but repeating debugedit is a no-op.  We do it
# beforehand to get the proper final build ID bits into the embedded image.
# This affects the vDSO images in vmlinux, and the vmlinux image in bzImage.
export AFTER_LINK=\
'sh -xc "/usr/lib/rpm/debugedit -b $$RPM_BUILD_DIR -d /usr/src/debug \
    				-i $@ > $@.id"'
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3
    InstallName=${4:-vmlinuz}

    # Pick the right config file for the kernel we're building
    Config=kernel-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
    DevelDir=/usr/src/kernels/%{KVERREL}${Flavour:+.${Flavour}}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{version}-%{release}.%{_target_cpu}${Flavour:+.${Flavour}}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = %{?stablerev}-%{release}.%{_target_cpu}${Flavour:+.${Flavour}}/" Makefile

    # if pre-rc1 devel kernel, must fix up SUBLEVEL for our versioning scheme
    %if !0%{?rcrev}
    %if 0%{?gitrev}
    perl -p -i -e 's/^SUBLEVEL.*/SUBLEVEL = %{upstream_sublevel}/' Makefile
    %endif
    %endif

    # and now to start the build process

    make -s mrproper
    cp %{SOURCE1} .config

    Arch=x86
    echo USING ARCH=$Arch

    make -s ARCH=$Arch oldnoconfig >/dev/null
    make -s ARCH=$Arch V=1 %{?_smp_mflags} $MakeTarget %{?sparse_mflags}
    make -s ARCH=$Arch V=1 %{?_smp_mflags} modules %{?sparse_mflags} || exit 1

    # Start installing the results
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi
    $CopyKernel $KernelImage \
    		$RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    # Override $(mod-fw) because we don't want it to install any firmware
    # We'll do that ourselves with 'make firmware_install'
    make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=
%ifarch %{vdso_arches}
    make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf \
        $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-$KernelVer.conf
%endif

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi
    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
%ifarch ppc
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/autoconf.h
    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{fancy_debuginfo}
    if test -s vmlinux.id; then
      cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id
    else
      echo >&2 "*** ERROR *** no vmlinux build ID! ***"
      exit 1
    fi
%endif

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
      LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
    }

    collect_modules_list networking \
    			 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register'
    collect_modules_list block \
    			 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler'
    collect_modules_list drm \
    			 'drm_open|drm_init'
    collect_modules_list modesetting \
    			 'drm_crtc_init'

    # detect missing or incorrect license tags
    rm -f modinfo
    while read i
    do
      echo -n "${i#$RPM_BUILD_ROOT/lib/modules/$KernelVer/} " >> modinfo
      /sbin/modinfo -l $i >> modinfo
    done < modnames

    grep -E -v \
    	  'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' \
	  modinfo && exit 1

    rm -f modinfo modnames

    # remove files that will be auto generated by depmod at rpm -i time
    for i in alias alias.bin builtin.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap
    do
      rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
    done

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
    ln -sf ../../..$DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -exec rm -f {} \;
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd linux-%{kversion}.%{_target_cpu}

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_pae_debug}
BuildKernel %make_target %kernel_image PAEdebug
%endif

%if %{with_pae}
BuildKernel %make_target %kernel_image PAE
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image
%endif

%if %{with_smp}
BuildKernel %make_target %kernel_image smp
%endif

%global perf_make \
  make %{?_smp_mflags} -C tools/perf -s V=1 HAVE_CPLUS_DEMANGLE=1 prefix=%{_prefix}
%if %{with_perf}
%{perf_make} all
%{perf_make} man || %{doc_build_fail}
%endif

%if %{with_doc}
# Make the HTML and man pages.
make htmldocs mandocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{fancy_debuginfo}
%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
%{nil}
%endif

%if %{with_debuginfo}
%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo-common-%{_target_cpu}
%defattr(-,root,root)
%endif
%endif

###
### pre-install
###
%pre
# If XBMC is installed and the version is older(< 12.2.2.1-1) when updating
# the kernel, we will preserve the kernel modules which is
# current version(< 2.6.39-1.ce19).
KERNEL_VERSION="`uname -r`"
KERNEL_MOD_BAK="/var/tmp/kernel_modules_bak"
if [ "$1" -gt "1" ];then
	XBMC_VERSION="`rpm -q XBMC --queryformat=%{VERSION}-%{RELEASE}`"
	if [ "$?" == "0" ] && [[ "$XBMC_VERSION" < "12.2.2.1-1.fc16" ]];then
		if [[ "$KERNEL_VERSION" < "2.6.39-1.ce19.fc16.i686" ]];then
			rm -rf ${KERNEL_MOD_BAK} > /dev/null 2>&1
			mkdir -p ${KERNEL_MOD_BAK}
			cp -aur /lib/modules/${KERNEL_VERSION} ${KERNEL_MOD_BAK}
		fi
	fi
fi

###
### install
###

%install

cd linux-%{kversion}.%{_target_cpu}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}
man9dir=$RPM_BUILD_ROOT%{_datadir}/man/man9

# copy the source over
mkdir -p $docdir
tar -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

# Install man pages for the kernel API.
mkdir -p $man9dir
find Documentation/DocBook/man -name '*.9.gz' -print0 |
xargs -0 --no-run-if-empty %{__install} -m 444 -t $man9dir $m
ls $man9dir | grep -q '' || > $man9dir/BROKEN
%endif # with_doc

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install

# perf man pages (note: implicit rpm magic compresses them later)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-man || %{doc_build_fail}
%endif

%if %{with_headers}
# Install kernel headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Do headers_check but don't die if it fails.
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_check \
     > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
     	-name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

# glibc provides scsi headers for itself, for now
rm -rf $RPM_BUILD_ROOT/usr/include/scsi
rm -f $RPM_BUILD_ROOT/usr/include/asm*/atomic.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/io.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/irq.h
%endif

%if %{with_firmware}
%{build_firmware}
%endif

%if %{with_bootwrapper}
make DESTDIR=$RPM_BUILD_ROOT bootwrapper_install WRAPPER_OBJDIR=%{_libdir}/kernel-wrapper WRAPPER_DTSDIR=%{_libdir}/kernel-wrapper/dts
%endif


###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]\
then\
    (cd /usr/src/kernels/%{KVERREL}%{?1:.%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*.fc*.*/$f $f\
     done)\
fi\
%{nil}

# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1}}\
/sbin/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --mkinitrd --dracut --depmod --update %{KVERREL}%{?-v:.%{-v*}} || exit $?\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --rpmposttrans %{KVERREL}%{?1:.%{1}} || exit $?\
%{expand:
# If XBMC is installed and the verison is older(< 12.2.2.1-1) when updating
# the kernel, we will import the preserved current kernel modules to
# /lib/modules .
KERNEL_VERSION="`uname -r`"
KERNEL_MOD_BAK="/var/tmp/kernel_modules_bak"
# If there is no kernel module which is current verison in /lib/modules,
# that means it is RPM updateing time.
if [ ! -d "/lib/modules/${KERNEL_VERSION}" ];then
	XBMC_VER="`rpm -q XBMC --queryformat=%{VERSION}-%{RELEASE}`"
	if [ "$?" == "0" ] && [[ "$XBMC_VER" < "12.2.2.1-1.fc16" ]];then
		if [[ "$KERNEL_VERSION" < "2.6.39-1.ce19.fc16.i686" ]];then
			[ -e "${KERNEL_MOD_BAK}/${KERNEL_VERSION}" ] && mv ${KERNEL_MOD_BAK}/${KERNEL_VERSION} /lib/modules/
		fi
	fi
fi
}
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*}}\
%{-r:\
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{expand:\
/sbin/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --install %{KVERREL}%{?-v:.%{-v*}} || exit $?\
}\
%{expand:\
if [ -e /proc/thecus_io ];then\
  # Intel SDK SW1.2 had modified kernel.
  # If NAS hasn't no XBMC or has new XBMC(>= 12.2.2.1-1), thecus's kernel can upgrade emmc.
  Ver="`rpm -q XBMC`"\
  if [ "$?" == "1" ] || ! [[ "$Ver" < "XBMC-12.2.2.1-1[.]" ]]; then\
    if [ "`/sbin/blockdev --getsize64 /dev/mmcblk0`" -lt 2000000000 ]; then\
      /usr/local/sbin/imgtool emmc "/dev/mmcblk0" -k /%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?-v:.%{-v*}} || exit $?\
    else\
      /usr/local/sbin/imgtool emmc4 "/dev/mmcblk0" -k /%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?-v:.%{-v*}} || exit $?\
    fi\
  fi\
fi}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1}}\
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}%{?1:.%{1}} || exit $?\
%{nil}

%kernel_variant_preun
%kernel_variant_post -r kernel-smp

%kernel_variant_preun smp
%kernel_variant_post -v smp

%kernel_variant_preun PAE
%kernel_variant_post -v PAE -r (kernel|kernel-smp)

%kernel_variant_preun debug
%kernel_variant_post -v debug

%kernel_variant_post -v PAEdebug -r (kernel|kernel-smp)
%kernel_variant_preun PAEdebug

if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi

###
### file lists
###

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_firmware}
%files firmware
%defattr(-,root,root)
/lib/firmware/*
%doc linux-%{kversion}.%{_target_cpu}/firmware/WHENCE
%endif

%if %{with_bootwrapper}
%files bootwrapper
%defattr(-,root,root)
/usr/sbin/*
%{_libdir}/kernel-wrapper
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%{_datadir}/man/man9/*
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_mandir}/man[1-8]/*

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf-debuginfo
%defattr(-,root,root)
%endif
%endif

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{1}\
%{expand:%%files %{?2}}\
%defattr(-,root,root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?2:.%{2}}\
%attr(600,root,root) /boot/System.map-%{KVERREL}%{?2:.%{2}}\
/boot/config-%{KVERREL}%{?2:.%{2}}\
%dir /lib/modules/%{KVERREL}%{?2:.%{2}}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/kernel\
/lib/modules/%{KVERREL}%{?2:.%{2}}/build\
/lib/modules/%{KVERREL}%{?2:.%{2}}/source\
/lib/modules/%{KVERREL}%{?2:.%{2}}/extra\
/lib/modules/%{KVERREL}%{?2:.%{2}}/updates\
%ifarch %{vdso_arches}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/vdso\
/etc/ld.so.conf.d/kernel-%{KVERREL}%{?2:.%{2}}.conf\
%endif\
/lib/modules/%{KVERREL}%{?2:.%{2}}/modules.*\
%ghost /boot/initramfs-%{KVERREL}%{?2:.%{2}}.img\
%{expand:%%files %{?2:%{2}-}devel}\
%defattr(-,root,root)\
/usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
%if %{with_debuginfo}\
%ifnarch noarch\
%if %{fancy_debuginfo}\
%{expand:%%files -f debuginfo%{?2}.list %{?2:%{2}-}debuginfo}\
%else\
%{expand:%%files %{?2:%{2}-}debuginfo}\
%endif\
%defattr(-,root,root)\
%if !%{fancy_debuginfo}\
%if "%{elf_image_install_path}" != ""\
%{debuginfodir}/%{elf_image_install_path}/*-%{KVERREL}%{?2:.%{2}}.debug\
%endif\
%{debuginfodir}/lib/modules/%{KVERREL}%{?2:.%{2}}\
%{debuginfodir}/usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
%endif\
%endif\
%endif\
%endif\
%{nil}


%kernel_variant_files %{with_up}
%kernel_variant_files %{with_smp} smp
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_pae} PAE
%kernel_variant_files %{with_pae_debug} PAEdebug

# plz don't put in a version string unless you're going to tag
# and build.

%changelog
* Fri May 20 2011 Dave Jones <davej@redhat.com>
- Rebuild to fix versioning.

* Thu May 19 2011 Dave Jones <davej@redhat.com>
- Update to 2.6.39 final.

* Sat May 14 2011 Kyle McMartin <kmcmartin@redhat.com>
- Update to v2 of Mel Gorman's SLUB patchset

* Sat May 14 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc7.git6.1
- tmpfs: implement generic xattr support
  Merge Eric Paris' patch to add xattr support to tmpfs, so that it can be
  used to host mockroots for mass rebuilds.
- Drop IMA disabling patch, which is no longer necessary since it's run time
  (but unused) cost is now minimized.
- Switch NF_CONNTRACK to modular, it'll get autoloaded where necessary.

* Sat May 14 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc7.git6.0
- Update to 2.6.39-rc7-git6

* Thu May 12 2011 Chuck Ebbert <cebbert@redhat.com>
- Fix yet another bug in AMD erratum checking (#704059)

* Thu May 12 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc7.git3.0
- Switch on release builds until 2.6.39 releases and we branch off 2.6.40-git.

* Wed May 11 2011 Kyle McMartin <kmcmartin@redhat.com>
- Linux 2.6.39-rc7-git3
- Pull in some SLUB fixes from Mel Gorman for testing.

* Tue May 09 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc7.git0.0
- Linux 2.6.39-rc7

* Mon May 09 2011 Dave Jones <davej@redhat.com>
- Remove remnants of non-upstreamed utrace bits.

* Mon May 08 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.39-0.rc6.git6.0
- Enable CONFIG_FB_UDL (#634636)

* Sat May 07 2011 Kyle McMartin <kmcmartin@redhat.com>
- Update to snapshot 2.6.39-rc6-git5

* Wed May 04 2011 Kyle McMartin <kmcmartin@redhat.com>
- Update to snapshot 2.6.39-rc6-git2

* Tue May 03 2011 Kyle McMartin <kmcmartin@redhat.com>
- Linux 2.6.39-rc6

* Sun May 01 2011 Kyle McMartin <kmcmartin@redhat.com>
- Update to snapshot 2.6.39-rc5-git5

* Thu Apr 28 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc5.git1.0
- Update to snapshot 2.6.39-rc5-git1
- Edit scripts/rebase.sh to not keep appending to .gitignore when the new
  .bz2 files are covered by wildcards.

* Wed Apr 27 2011 Kyle McMartin <kmcmartin@redhat.com>
- Linux 2.6.39-rc5

* Tue Apr 26 2011 Kyle McMartin <kmcmartin@redhat.com>
- Update to 2.6.39-rc4-git8

* Sun Apr 24 2011 Kyle McMartin <kmcmartin@redhat.com>
- ppc64: disable TUNE_CELL, which causes problems with illegal instuctions
  being generated on non-Cell PPC machines. (#698256)

* Wed Apr 20 2011 Dave Jones <davej@redhat.com> 2.6.39-0.rc4.git2.0
- Update to 2.6.39-rc4-git2

* Tue Apr 19 2011 Dave Jones <davej@redhat.com>
- Build USB_SERIAL in instead of modular.
  Enable USB_SERIAL_CONSOLE.

* Wed Apr 13 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc3.git2.0
- Update to snapshot 2.6.39-rc3-git2

* Mon Apr 11 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc2.git3.0
- Update to git snapshot 2.6.39-rc2-git3
- efifb_update.patch: drop, upstream.

* Thu Apr 07 2011 Hans de Goede <hdegoede@redhat.com>
- Add a no lvds quirk for the Asus EB1007 to the i915 drm driver,
  this fixes gnome-shell not working on it

* Wed Apr 06 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc2.git0.0
- Update to 2.6.39-rc2

* Tue Apr 05 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc1.git5.0
- Update to git snapshot 2.6.39-rc1-git5
- (Not test-built before commit since my rawr box is down atm.)

* Sat Apr 02 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc1.git3.0
- Update to snapshot 2.6.39-rc1-git3
- generic: CONFIG_USB_VL600=m

* Thu Mar 31 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc1.git1.0
- Update to snapshot 2.6.39-rc1-git1

* Tue Mar 29 2011 Kyle McMartin <kmcmartin@redhat.com>
- Disable CONFIG_IMA, CONFIG_TCG_TPM on powerpc (#689468)

* Tue Mar 29 2011 Kyle McMartin <kmcmartin@redhat.com>
- Disable qla4xxx (CONFIG_SCSI_QLA_ISCSI) driver on powerpc32 (#686199)

* Tue Mar 29 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc1.git0.0
- ... and then 2.6.39-rc1

* Tue Mar 29 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc0.git21.0
- Update to snapshot 2.6.38-git21
- Enable some new x86{_64} platform drivers.

* Mon Mar 28 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc0.git19.0
- Update to snapshot 2.6.38-git19
- Drop upstream patches:
  - acpi_battery-fribble-sysfs-files-from-a-resume-notifier.patch
  - apple_backlight.patch
- Rebased:
  - acpi_reboot.patch
  - linux-2.6-acpi-debug-infinite-loop.patch
  - linux-2.6-debug-sizeof-structs.patch
  - linux-2.6-i386-nx-emulation.patch
- Disabled:
  - utrace.

* Fri Mar 25 2011 Chuck Ebbert <cebbert@redhat.com>
- Drop unused patches already applied upstream:
  hdpvr-ir-enable.patch
  thinkpad-acpi-fix-backlight.patch

* Wed Mar 23 2011 Kyle McMartin <kmcmartin@redhat.com>
- Re-create ACPI battery sysfs files on resume from suspend, fixes the
  upstream changes to the dropped
  acpi-update-battery-information-on-notification-0x81.patch.

* Wed Mar 23 2011 Kyle McMartin <kmcmartin@redhat.com>
- Update to 2.6.38-git12
- Enable I2C_DIOLAN_U2C USB i2c adapter [all], I2C_PXA [i686].

* Tue Mar 22 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc0.git11.0
- Update to 2.6.38-git11
- Drop merged fs-call-security_d_instantiate-in-d_obtain_alias.patch
- Fix context in add-appleir-usb-driver.patch
- Enable firewire ALSA modules, HP accelerometer driver.
- Re-enable PSTORE, seems to be fixed.
- Fix utrace-ptrace for upstream smp_lock removal.

* Fri Mar 18 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc0.git6.0
- Update to 2.6.38-git6
- CONFIG_IP_SET modules and associated netfilter goo.
- New network packet scheduler modules (sch, choke, mqprio.)
- Enable DMI sysfs interface (built-in) on ia64, x86_64, i386.
- Explicitly set USB storage goo as modular.
- Drop merged patches, nil-ify drm-nouveau-updates, fix context in crash.ko
  Kconfig diff.

* Thu Mar 17 2011 Matthew Garrett <mjg@redhat.com>
- drop efi_default_physical.patch - it's actually setting up something that's
  neither physical nor virtual, and it's probably breaking EFI boots

* Wed Mar 16 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.39-0.rc0.git1.1
- Test out scripts/rebase.sh on 2.6.38-git1.
- Enable fhandle syscalls (ugh. conditional syscalls... update
  CONFIG_EXPORTFS to =y, since it's now a bool.)
- CONFIG_XEN_DEBUG [i386,x86_64] =n, but possibly should be -debug
  conditional. Needs a xen user to benchmark and see how bad the overhead
  is.

* Tue Mar 15 2011 Adam Jackson <ajax@redhat.com>
- drm-intel-big-hammer.patch: Drop.

* Tue Mar 15 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-1
- Linux 2.6.38

* Mon Mar 14 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc8.git4.1
- Linux 2.6.38-rc8-git4

* Thu Mar 10 2011 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.38-rc8-git3

* Thu Mar 10 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc8.git2.1
- Linux 2.6.38-rc8-git2

* Wed Mar 09 2011 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.38-rc8-git1

* Wed Mar 09 2011 Dennis Gilmore <dennis@ausil.us>
- apply sparc64 gcc-4.6.0 buildfix patch

* Wed Mar 09 2011 Ben Skeggs <bskeggs@redhat.com> 2.6.38-0.rc8.git0.2
- nouveau: allow max clients on nv4x (679629), better error reporting

* Tue Mar 08 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc8.git0.1
- Linux 2.6.38-rc8

* Sat Mar 05 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc7.git4.1
- Linux 2.6.38-rc7-git4
- Revert upstream commit e3e89cc535223433a619d0969db3fa05cdd946b8
  for now to fix utrace build.

* Fri Mar 04 2011 Roland McGrath <roland@redhat.com> - 2.6.38-0.rc7.git2.3
- Split out perf-debuginfo subpackage.

* Fri Mar 04 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc7.git2.2
- Disable drm-i915-gen4-has-non-power-of-two-strides.patch for now, breaks
  my mutter.

* Fri Mar 04 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc7.git2.1
- Linux 2.6.38-rc7-git2
- drm-i915-gen4-has-non-power-of-two-strides.patch (#681285)

* Thu Mar 03 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc7.git1.1
- Linux 2.6.38-rc7-git1

* Tue Mar 01 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc7.git0.1
- Linux 2.6.38-rc7

* Fri Feb 25 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc6.git6.1
- Linux 2.6.38-rc6-git6
- Build in virtio_pci driver so virtio_console will be built-in (#677713)

* Thu Feb 24 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc6.git4.1
- Linux 2.6.38-rc6-git4

* Thu Feb 24 2011 Matthew Garrett <mjg@redhat.com> 2.6.38-0.rc6.git2.2
- linux-2.6-acpi-fix-implicit-notify.patch: Fix implicit notify when there's
  more than one device per GPE

* Wed Feb 23 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc6.git2.1
- Linux 2.6.38-rc6-git2

* Wed Feb 23 2011 Ben Skeggs <bskeggs@redhat.com> 2.6.38-0.rc6.git0.2
- nouveau: nv4x pciegart fixes, nvc0 accel improvements

* Tue Feb 22 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc6.git0.1
- Linux 2.6.38-rc6

* Tue Feb 22 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc5.git7.1
- Linux 2.6.38-rc5-git7

* Mon Feb 21 2011 Dave Jones <davej@redhat.com> 2.6.38-0.rc5.git6.1
- Linux 2.6.38-rc5-git6

* Sat Feb 19 2011 Chuck Ebbert <cebbert@redhat.com>  2.6.38-0.rc5.git5.1
- Linux 2.6.38-rc5-git5

* Wed Feb 16 2011 Chuck Ebbert <cebbert@redhat.com>  2.6.38-0.rc5.git1.1
- Linux 2.6.38-rc5-git1
- Add support for Airprime/Sierra USB IP modem (#676860)
- Make virtio_console built-in on x86_64 (#677713)
- Revert check for read-only block device added in .38 (#672265)

* Tue Feb 15 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc5.git0.1
- Linux 2.6.38-rc5 (81 minutes later...)

* Sun Feb 13 2011 Chuck Ebbert <cebbert@redhat.com>  2.6.38-0.rc4.git7.1
- Linux 2.6.38-rc4-git7

* Sat Feb 12 2011 Chuck Ebbert <cebbert@redhat.com>  2.6.38-0.rc4.git6.1
- Linux 2.6.38-rc4-git6
- Fix memory corruption caused by bug in bridge code.

* Thu Feb 10 2011 Chuck Ebbert <cebbert@redhat.com>  2.6.38-0.rc4.git3.1
- Linux 2.6.38-rc4-git3

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.38-0.rc4.git0.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Feb 07 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc4.git0.1
- Linux 2.6.38-rc4

* Fri Feb 04 2011 Chuck Ebbert <cebbert@redhat.com>  2.6.38-0.rc3.git4.1
- Linux 2.6.38-rc3-git4

* Thu Feb 03 2011 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.38-rc3-git3
- Enable Advansys SCSI driver on x86_64 (#589115)

* Thu Feb 03 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc3.git2.1
- Linux 2.6.38-rc3-git2 snapshot
- [sgruszka] ath5k: fix fast channel change (#672778)

* Wed Feb 02 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc3.git1.1
- Linux 2.6.38-rc3-git1 snapshot.

* Wed Feb 02 2011 Chuck Ebbert <cebbert@redhat.com>
- Fix autoload of atl1c driver for latest hardware (#607499)

* Tue Feb 01 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc3.git0.1
- Linux 2.6.38-rc3
- Try to fix some obvious bugs in hfsplus mount failure handling (#673857)

* Mon Jan 31 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc2.git9.1
- Linux 2.6.38-rc2-git9

* Mon Jan 31 2011 Kyle McMartin <kmcmartin@redhat.com>
- disable CONFIG_SERIAL_8250_DETECT_IRQ (from mschmidt@redhat.com)

* Mon Jan 31 2011 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.38-rc2-git8
- Add Trond's NFS bugfixes branch from git.linux-nfs.org

* Mon Jan 31 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc2.git7.2
- Fix build failure on s390.

* Fri Jan 28 2011 Chuck Ebbert <cebbert@redhat.com> 2.6.38-0.rc2.git7.1
- Linux 2.6.38-rc2-git7

* Wed Jan 26 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc2.git5.1
- Linux 2.6.38-rc2-git5
- [x86] Re-enable TRANSPARENT_HUGEPAGE, should be fixed by cacf061c.

* Tue Jan 25 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc2.git3.2
- [x86] Disable TRANSPARENT_HUGEPAGE for now, there be dragons there.

* Tue Jan 25 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc2.git3.1
- Linux 2.6.38-rc2-git3
- perf-gcc460-build-fixes.patch: fix context from [9486aa38]

* Mon Jan 24 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc2.git1.3
- Disable usb/pci/acpi autosuspend goo until it can be checked.

* Mon Jan 24 2011 Kyle McMartin <kmcmartin@redhat.com>
- debug-tty-print-dev-name.patch: drop, haven't seen any warnings recently.
- runtime_pm_fixups.patch: rebase and re-enable, make acpi_power_transition
   in pci_bind actually do the right thing instead of (likely) always
   trying to transition to D0.

* Mon Jan 24 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc2.git1.1
- Linux 2.6.38-rc2-git1
- [e5cce6c1] tpm: fix panic caused by "tpm: Autodetect itpm devices"
  may fix some boot issues people were having.
- tpm-fix-stall-on-boot.patch: upstream.
- perf-gcc460-build-fixes.patch: fix build issues with warn-unused-but-set
  in gcc 4.6.0

* Sat Jan 22 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc2.git0.1
- Linux 2.6.38-rc2
- linux-2.6-serial-460800.patch, drivers/serial => drivers/tty/serial

* Thu Jan 20 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc1.git1.1
- Linux 2.6.38-rc1-git1, should fix boot failure in -rc1.

* Wed Jan 19 2011 Roland McGrath <roland@redhat.com>
- utrace update

* Wed Jan 19 2011 Kyle McMartin <kmcmartin@redhat.com> 2.6.38-0.rc1.git0.1
- Linux 2.6.38-rc1

* Wed Jan 19 2011 Kyle McMartin <kyle@redhat.com>
- Trimmed changelog, see fedpkg git for earlier history.

###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
