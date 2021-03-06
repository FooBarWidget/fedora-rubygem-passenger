%global package_name passenger
%global namespace passenger
%global nginx_version 1.4.4
%global bundled_boost_version 1.54.0

%if 0%{?fc18}
%global rubyabi 1.9.1
%endif

%if 0%{?el6}
%global rubyabi 1.8
%endif

%if 0%{?fedora} >= 19
%global gem_extdir %{gem_extdir_mri}
%endif
%{!?gem_extdir: %global gem_extdir %{gem_instdir}/extdir}

%{!?_httpd_mmn: %{expand: %%global _httpd_mmn %%(cat %{_includedir}/httpd/.mmn 2>/dev/null || echo missing-httpd-devel)}}
%{!?_httpd_confdir:    %{expand: %%global _httpd_confdir    %%{_sysconfdir}/httpd/conf.d}}
# /etc/httpd/conf.d with httpd < 2.4 and defined as /etc/httpd/conf.modules.d with httpd >= 2.4
%{!?_httpd_modconfdir: %{expand: %%global _httpd_modconfdir %%{_sysconfdir}/httpd/conf.d}}
%{!?_httpd_moddir:    %{expand: %%global _httpd_moddir    %%{_libdir}/httpd/modules}}

%global ruby_dir_version %(ruby -rrbconfig -e 'puts RbConfig::CONFIG["ruby_version"]')
%global ruby_arch_name %(ruby -rrbconfig -e 'puts RbConfig::CONFIG["arch"]')
%{!?ruby_sitelibdir: %global ruby_sitelibdir %(ruby -rrbconfig -e 'puts RbConfig::CONFIG["sitelibdir"]')}
%{!?ruby_sitearchdir: %global ruby_sitearchdir %(ruby -rrbconfig -e 'puts RbConfig::CONFIG["sitearchdir"]')}
%global passenger_ruby_libdir %{ruby_sitelibdir}
%global locations_ini %{passenger_ruby_libdir}/phusion_passenger/locations.ini


Summary: Phusion Passenger application server
Name: %{package_name}
Version: 4.0.33
Release: 1%{?dist}
Group: System Environment/Daemons
# Passenger code uses MIT license.
# Bundled(Boost) uses Boost Software License
# BCrypt and Blowfish files use BSD license.
# Documentation is CC-BY-SA
# See: https://bugzilla.redhat.com/show_bug.cgi?id=470696#c146
License: Boost and BSD and BSD with advertising and MIT and zlib
URL: https://www.phusionpassenger.com
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source: http://s3.amazonaws.com/phusion-passenger/releases/passenger-%{version}.tar.gz
Source1: http://nginx.org/download/nginx-%{nginx_version}.tar.gz
Source10: passenger.logrotate
Source11: apache-passenger.conf.in
Source12: config.json

# Include sys/types.h for GCC 4.7
Patch2:         rubygem-passenger-4.0.18-gcc47-include-sys_types.patch

# Make example config for tests ready for linux by default
Patch4:         passenger_tests_default_config_example.patch

# Test tries to spawn 1000 threads with 256kb stacks. Default Linux settings
# deny allocating so much, causing test to fail. Let's use 8kb stacks instead.
Patch102:       passenger_dynamic_thread_group.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=985634
Patch107:       rubygem-passenger-4.0.18-GLIBC_HAVE_LONG_LONG.patch

Requires: rubygems
# XXX: Needed to run passenger standalone
Requires: rubygem(daemon_controller) >= 1.1.0
Requires: rubygem(rack)
Requires: rubygem(rake)
%if 0%{?fedora} >= 19
Requires: ruby(release)
%else
Requires: ruby(abi) = %{rubyabi}
%endif

%if 0%{?rhel} >= 6 || 0%{?fedora} >= 15
BuildRequires:  libcurl-devel
%else
BuildRequires:  curl-devel
%endif

%if 0%{?rhel} < 6 && 0%{?fedora} <= 16
Requires: rubygem(fastthread) >= 1.0.1
BuildRequires:  rubygem(fastthread) >= 1.0.1
%endif

BuildRequires: httpd-devel
BuildRequires: libev-devel >= 4.0.0
BuildRequires: ruby
BuildRequires: ruby-devel
BuildRequires: rubygems
BuildRequires: rubygems-devel
BuildRequires: rubygem(rake) >= 0.8.1
BuildRequires: rubygem(rack)
BuildRequires: zlib-devel
BuildRequires: pcre-devel
BuildRequires: openssl-devel

Provides: %{package_name} = %{version}-%{release}
Provides: bundled(boost)  = %{bundled_boost_version}
Obsoletes: rubygem(passenger) < 4.0.33
Obsoletes: rubygem-passenger < 4.0.33
Obsoletes: rubygem-passenger%{_isa} < 4.0.33
Obsoletes: rubygem-passenger-native < 4.0.33
Obsoletes: rubygem-passenger-native%{?_isa} < 4.0.33

%description
Phusion Passenger® is a web server and application server, designed to be fast, robust
and lightweight. It takes a lot of complexity out of deploying web apps, adds powerful
enterprise-grade features that are useful in production, and makes administration much
easier and less complex. It supports Ruby, Python, Node.js and Meteor.

%package -n mod_passenger
Summary: Apache Module for Phusion Passenger
Group: System Environment/Daemons
BuildRequires:  httpd-devel
Requires: httpd-mmn = %{_httpd_mmn}
Requires: %{package_name} = %{version}-%{release}
License: Boost and BSD and BSD with advertising and MIT and zlib

%description -n mod_passenger
This package contains the pluggable Apache server module for Phusion Passenger®.

%package devel
Summary: Phusion Passenger development files
Group: System Environment/Daemons
Requires: %{package_name}%{?_isa} = %{version}-%{release}
Provides: bundled(boost-devel) = %{bundled_boost_version}
Obsoletes: rubygem-passenger-devel < 4.0.33
Obsoletes: rubygem-passenger-devel%{?_isa} < 4.0.33
License: Boost and BSD and BSD with advertising and GPL+ and MIT and zlib

%description devel
This package contains development files for Phusion Passenger®. Installing this
package allows it to compile native extensions for non-standard Ruby interpreters,
and allows Passenger Standalone to use a different Nginx core version.

%package doc
Summary: Phusion Passenger documentation
Group: System Environment/Daemons
Requires: %{package_name} = %{version}-%{release}
Obsoletes: rubygem-passenger-doc < 4.0.33
BuildArch: noarch
License: CC-BY-SA and MIT and (MIT or GPL+)

%description doc
This package contains documentation files for Phusion Passenger®.

%package native-libs
Summary: Phusion Passenger native extensions
Group: System Environment/Daemons
Requires: %{package_name}%{?_isa} = %{version}-%{release}
Requires: ruby
Obsoletes: rubygem-passenger-native-libs < 4.0.33
Obsoletes: rubygem-passenger-native-libs%{?_isa} < 4.0.33
License: Boost and BSD and BSD with advertising and MIT and zlib
%description native-libs
This package contains Phusion Passenger® native extensions for Ruby.
It has been separated so that installing a new Ruby interpreter only
necessitates rebuilding this package.


%prep
%setup -q -n %{package_name}-%{version}
tar xzf %{SOURCE1}

%patch2   -p1 -b .include-sys-types
%patch4   -p1 -b .lindefault
%patch102 -p1 -b .threadtest

# fix passenger boost for glibc >= 2.18
%if 0%{?fedora} >= 20
    %patch107 -p1 -b .glibc-long
%endif

# Don't use bundled libev
%{__rm} -rf ext/libev

%build
export EXTRA_CFLAGS="${CFLAGS:-%optflags} -Wno-deprecated"
export EXTRA_CXXFLAGS="${CXXFLAGS:-%optflags} -Wno-deprecated"

# Reduce optimization level. Passenger has not been tested with -O2.
export EXTRA_CFLAGS=`echo "$EXTRA_CFLAGS" | sed 's|-O2|-O|g'`
export EXTRA_CXXFLAGS=`echo "$EXTRA_CXXFLAGS" | sed 's|-O2|-O|g'`

export USE_VENDORED_LIBEV=false

# Speed up ccache (reduce I/O) by lightly compressing things.
# Always set these variables because pbuilder uses ccache transparently.
export CCACHE_COMPRESS=1
export CCACHE_COMPRESS_LEVEL=3

# Build Passenger.
rake fakeroot \
    NATIVE_PACKAGING_METHOD=rpm \
    FS_PREFIX=%{_prefix} \
    FS_BINDIR=%{_bindir} \
    FS_SBINDIR=%{_sbindir} \
    FS_DATADIR=%{_datadir} \
    FS_DOCDIR=%{_docdir} \
    FS_LIBDIR=%{_libdir} \
    RUBYLIBDIR=%{ruby_sitelibdir} \
    RUBYARCHDIR=%{ruby_sitearchdir} \
    APACHE2_MODULE_PATH=%{_httpd_moddir}/mod_passenger.so

# Build Nginx core for Passenger Standalone.
nginx_config_opts=`ruby -Ilib -rphusion_passenger -e 'PhusionPassenger.locate_directories; PhusionPassenger.require_passenger_lib "constants"; puts PhusionPassenger::STANDALONE_NGINX_CONFIGURE_OPTIONS'`
pushd nginx-%{nginx_version}
./configure --prefix=/tmp $nginx_config_opts --add-module=`pwd`/../ext/nginx
make
popd


%install
%{__rm} -rf %{buildroot}
%{__mkdir} %{buildroot}
%{__cp} -a pkg/fakeroot/* %{buildroot}/
%{__cp} nginx-%{nginx_version}/objs/nginx %{buildroot}%{_libdir}/%{namespace}/PassengerWebHelper

# Install bootstrapping code into the executables and the Nginx config script.
./dev/install_scripts_bootstrap_code.rb --ruby %{passenger_ruby_libdir} %{buildroot}%{_bindir}/* %{buildroot}%{_sbindir}/*
./dev/install_scripts_bootstrap_code.rb --nginx-module-config %{_bindir} %{buildroot}%{_datadir}/%{namespace}/ngx_http_passenger_module/config

# Install Apache config.
%{__mkdir_p} %{buildroot}%{_httpd_confdir} %{buildroot}%{_httpd_modconfdir}
%{__sed} -e 's|@PASSENGERROOT@|%{passenger_ruby_libdir}/phusion_passenger/locations.ini|g' %{SOURCE11} > passenger.conf

%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
    %{__sed} -n /^LoadModule/p passenger.conf > 10-passenger.conf
    %{__sed} -i /^LoadModule/d passenger.conf
    touch -r %{SOURCE11} 10-passenger.conf
    install -pm 0644 10-passenger.conf %{buildroot}%{_httpd_modconfdir}/passenger.conf
%endif
touch -r %{SOURCE11} passenger.conf
install -pm 0644 passenger.conf %{buildroot}%{_httpd_confdir}/passenger.conf

# Install man pages into the proper location.
%{__mkdir_p} %{buildroot}%{_mandir}/man1
%{__mkdir_p} %{buildroot}%{_mandir}/man8
%{__cp} man/*.1 %{buildroot}%{_mandir}/man1
%{__cp} man/*.8 %{buildroot}%{_mandir}/man8

# Make our ghost log and run directories...
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/passenger-analytics

# logrotate
%{__mkdir_p} %{buildroot}%{_sysconfdir}/logrotate.d
install -pm 0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/logrotate.d/passenger


%check
export EXTRA_CFLAGS="${CFLAGS:-%optflags} -Wno-deprecated"
export EXTRA_CXXFLAGS="${CXXFLAGS:-%optflags} -Wno-deprecated"
export EXTRA_CFLAGS=`echo "$EXTRA_CFLAGS" | sed 's|-O2||g'`
export EXTRA_CXXFLAGS=`echo "$EXTRA_CXXFLAGS" | sed 's|-O2||g'`
export USE_VENDORED_LIBEV=false
export CCACHE_COMPRESS=1
export CCACHE_COMPRESS_LEVEL=3

# Running the full test suite is not only slow, but also impossible
# because not all requirements are packaged by Fedora. It's also not
# too useful because Phusion Passenger is automatically tested by a CI
# server on every commit. The C++ tests are the most likely to catch
# any platform-specific bugs (e.g. bugs caused by wrong compiler options)
# so we only run those. Note that the C++ tests are highly timing
# sensitive, so sometimes they may fail even though nothing is really
# wrong. We therefore do not make failures fatal, although the result
# should still be checked.
%{__cp} %{SOURCE12} test/config.json
rake test:cxx || true

%files
%doc "%{_docdir}/%{namespace}/Users guide.html"
%doc "%{_docdir}/%{namespace}/Users guide Nginx.html"
%doc "%{_docdir}/%{namespace}/Users guide Apache.html"
%doc "%{_docdir}/%{namespace}/Users guide Standalone.html"
%{_bindir}
%{_sbindir}
%{_libdir}/%{namespace}/PassengerWebHelper
%{_libdir}/%{namespace}/agents
%{_datadir}/%{namespace}/helper-scripts
%{_datadir}/%{namespace}/templates
%{_datadir}/%{namespace}/standalone_default_root
%{_datadir}/%{namespace}/node
%{_datadir}/%{namespace}/*.types
%{_datadir}/%{namespace}/*.crt
%{_datadir}/%{namespace}/*.txt
%dir %{_localstatedir}/log/passenger-analytics
%{_sysconfdir}/logrotate.d/passenger
%{_mandir}
%{passenger_ruby_libdir}

%files doc
%doc %{_docdir}/%{namespace}

%files devel
%{_datadir}/%{namespace}/ngx_http_passenger_module
%{_datadir}/%{namespace}/ruby_extension_source
%{_datadir}/%{namespace}/include
%{_libdir}/%{namespace}/common

%files -n mod_passenger
%config(noreplace) %{_httpd_modconfdir}/*.conf
%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
    %config(noreplace) %{_httpd_confdir}/*.conf
%endif
%doc "%{_docdir}/%{namespace}/Users guide Apache.html"
%{_httpd_moddir}/mod_passenger.so

%files native-libs
%{ruby_sitearchdir}/passenger_native_support.so

%changelog
* Thu Nov 14 2013 Jan Kaluza <jkaluza@redhat.com> - 4.0.18-4
- load native library from proper path

* Thu Oct 31 2013 Jan Kaluza <jkaluza@redhat.com> - 4.0.18-3
- fix #1021940 - add locations.ini with proper Fedora locations

* Wed Sep 25 2013 Troy Dawson <tdawson@redhat.com> - 4.0.18-2
- Cleanup spec file
- Fix for bz#987879

* Tue Sep 24 2013 Troy Dawson <tdawson@redhat.com> - 4.0.18-1
- Update to 4.0.18
- Remove patches no longer needed
- Update patches that need updating

* Mon Sep 23 2013 Brett Lentz <blentz@redhat.com> - 3.0.21-9
- finish fixing bz#999384

* Fri Sep 20 2013 Joe Orton <jorton@redhat.com> - 3.0.21-8
- update packaging for httpd 2.4.x

* Thu Sep 19 2013 Troy Dawson <tdawson@redhat.com> - 3.0.21-7
- Fix for F20 FTBFS (#993310)

* Thu Aug 22 2013 Brett Lentz <blentz@redhat.com> - 3.0.21-6
- bz#999384

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.21-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Jul 18 2013 Troy Dawson <tdawson@redhat.com> - 3.0.21-4
- Fix for CVE-2013-4136 (#985634)

* Fri Jun 21 2013 Troy Dawson <tdawson@redhat.com> - 3.0.21-3
- Putting the agents back to where they originally were

* Fri Jun 21 2013 Troy Dawson <tdawson@redhat.com> - 3.0.21-2
- Remove Rakefile (only used for building) (#976843)

* Thu May 30 2013 Troy Dawson <tdawson@redhat.com> - 3.0.21-1
- Update to version 3.0.21
- Fix for CVE-2013-2119

* Thu May 16 2013 Troy Dawson <tdawson@redhat.com> - 3.0.19-4
- Fix to make agents work on F19+

* Wed Mar 13 2013 Troy Dawson <tdawson@redhat.com> - 3.0.19-3
- Fix to make it build/install on F19+
- Added patch105

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.19-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jan 20 2013 Orion Poplawski <orion@cora.nwra.com> - 3.0.19-1
- Update to 3.0.19

* Wed Sep 19 2012 Orion Poplawski <orion@cora.nwra.com> - 3.0.17-3
- Drop dependency on rubygem(file-tail), no longer needed

* Fri Sep 7 2012 Brett Lentz <blentz@redhat.com> - 3.0.17-2
- Fix License

* Thu Sep 6 2012 Brett Lentz <blentz@redhat.com> - 3.0.17-1
- update to 3.0.17

* Wed Sep 5 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-15
- add support for tmpfiles.d

* Tue Sep 4 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-14
- Fix License tag
- Fix gem_extdir ownership issue

* Wed Aug 29 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-13
- fix pathing issues
- fix ruby abi requires

* Wed Aug 29 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-12
- remove capability for running passenger standalone until daemon_controller is updated

* Tue Aug 28 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-11
- fix issues with fastthread

* Mon Aug 27 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-10
- get test suite sort of working
- move agents to gem_extdir

* Fri Aug 24 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-9
- stop using _bindir
- fix native libs path
- fix ownership on extdir
- improve test output

* Wed Aug 22 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-8
- removed policycoreutils requirement
- moved native libs to gem_extdir

* Wed Aug 22 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-7
- remove selinux policy module. it's in the base policy now.

* Fri Aug 17 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-6
- put native-libs into ruby_vendorarchdir.

* Thu Aug 16 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-5
- clean up packaging and file placement.
- add logrotate file for /var/log/passenger-analytics

* Wed Aug 15 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-4
- backported fix only needed on f18+

* Wed Aug 15 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-3
- backport fix from https://svn.boost.org/trac/boost/ticket/6940

* Mon Aug 13 2012 Brett Lentz <blentz@redhat.com> - 3.0.14-2
- remove F15 conditional. F15 is EOL.

* Fri Jul 27 2012 Troy Dawson <tdawson@redhat.com> - 3.0.14-1
- Updated to version 3.0.14

* Fri Jul 27 2012 Troy Dawson <tdawson@redhat.com> - 3.0.12-6
- Added patch20, spawn-ip
- Changed selinux files to be more dynamic

* Tue Jun 05 2012 Troy Dawson <tdawson@redhat.com> - 3.0.12-5
- Add all the selinux files

* Tue Jun 05 2012 Troy Dawson <tdawson@redhat.com> - 3.0.12-4
- Added selinux configurations

* Tue Jun 05 2012 Troy Dawson <tdawson@redhat.com> - 3.0.12-3
- Added native and native-libs rpms.

* Mon Apr 16 2012 Brett Lentz <blentz@redhat.com> - 3.0.12-2
- Add dist to release.
- Shuffle around deprecated buildrequires and requires.

* Mon Apr 16 2012 Brett Lentz <blentz@redhat.com> - 3.0.12-1
- Update to 3.0.12
- Incorporate specfile changes from kanarip's version

* Wed Apr 11 2012 Brett Lentz <blentz@redhat.com> - 3.0.11-1
- Initial spec file
