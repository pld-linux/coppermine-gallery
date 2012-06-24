%define		_ver %(echo %{version} | tr -d .)
Summary:	Multi-purpose fully-featured and integrated web picture gallery script
Summary(pl.UTF-8):	W pełni funkcjonalny skrypt do galerii obrazków na WWW
Name:		coppermine-gallery
Version:	1.4.25
Release:	1
License:	GPL v2+
Group:		Applications/Publishing
Source0:	http://dl.sourceforge.net/coppermine/cpg%{version}.zip
# Source0-md5:	329eb9e2cb4a56a7f3674312d7031a21
Source1:	%{name}-apache.conf
Patch0:		%{name}-typo.patch
Patch1:		%{name}-pld.patch
URL:		http://coppermine-gallery.net/
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	unzip
Requires:	php(mysql)
Requires:	webapps
Requires:	webserver(php) >= 4.1.0
#Suggests:	Imagemagick
#Suggests:	php-gd
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir	%{_datadir}/%{_webapp}

%description
Coppermine Photo Gallery is an advanced, user-friendly, picture
gallery script with built-in support for other multi-media/data files.

The gallery can be private, accessible to registered users only,
and/or open to all visitors to your site. Users, if permitted, can
upload pictures with their web browser (thumbnail and intermediate
sized images are created on the fly), rate pictures, add comments and
even send e-cards.

The site administrator determines which of the features listed above
are accessible by registered and non-registered users. The site
administrator can also manage galleries and batch process large
numbers of pictures that have been uploaded onto the server by FTP.

%description -l pl.UTF-8
Coppermine Photo Gallery to zaawansowany, przyjazny dla użytkownika
skrypt do galerii obrazków z wbudowaną obsługą innych plików
multimedialnych lub z danymi.

Galerie mogą być prywatne, dostępne tylko dla zarejestrowanych
użytkowników i/lub otwarte dla wszystkich gości. Użytkownicy, jeśli
mają do tego uprawnienia, mogą umieszczać obrazki przy użyciu swojej
przeglądarki (miniaturki i obrazki o pośrednim rozmiarze są tworzone w
locie), oceniać obrazki, dodawać komentarze, a nawet wysyłać e-kartki.

Administrator serwisu określa, które z wyżej wymienionych opcji są
dostępne dla zarejestrowanych i niezarejestrowanych użytkowników. Może
także zarządzać galeriami i wsadowo przetwarzać dużą liczbę obrazków
umieszczonych na serwerze przez FTP.

%package setup
Summary:	Coppermine Gallery setup package
Summary(pl.UTF-8):	Pakiet do wstępnej konfiguracji Coppermine Gallery
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}

%description setup
Install this package to configure initial Coppermine Gallery
installation. You should uninstall this package when you're done, as
it considered insecure to keep the setup files in place.

%description setup -l pl.UTF-8
Ten pakiet należy zainstalować w celu wstępnej konfiguracji Coppermine
Gallery Eventum po pierwszej instalacji. Potem należy go odinstalować,
jako że pozostawienie plików instalacyjnych mogłoby być niebezpieczne.

%prep
%setup -q -n cpg14x
rm -f upgrade-1.0-to-1.2.php
# undos the source
find '(' -name '*.php' -o -name '*.css' -o -name '*.js' ')' -print0 | xargs -0 sed -i -e 's,\r$,,'
%patch0 -p1
%patch1 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_appdir},%{_sysconfdir}} \
	$RPM_BUILD_ROOT/var/lib/%{name}/albums/{edit,userpics}

cp -a *.{php,js,css} $RPM_BUILD_ROOT%{_appdir}
cp -a bridge docs images include lang logs plugins sql themes $RPM_BUILD_ROOT%{_appdir}
ln -s /var/lib/%{name}/albums $RPM_BUILD_ROOT%{_appdir}/albums

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
touch $RPM_BUILD_ROOT%{_sysconfdir}/config.inc.php
touch $RPM_BUILD_ROOT%{_sysconfdir}/install.lock

%clean
rm -rf $RPM_BUILD_ROOT

%post setup
chmod 770 %{_sysconfdir}
chmod 660 %{_sysconfdir}/config.inc.php
if [ "$1" = 1 ]; then
%banner -e %{name}-setup <<EOF
You will need to create MySQL database and grant access to it:
$ mysqladmin create cpq
mysql> GRANT SELECT,INSERT,UPDATE,DELETE,CREATE ON cpg.* TO cpg@localhost IDENTIFIED BY 'PASSWORD';

You should install ImageMagic or php-gd for image conversions.
EOF
fi

%postun setup
if [ "$1" = "0" ]; then
	chmod 750 %{_sysconfdir}
	chown root:http %{_sysconfdir}/config.inc.php
	chmod 640 %{_sysconfdir}/config.inc.php
fi

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc README.txt CHANGELOG
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/config.inc.php
%ghost %{_sysconfdir}/install.lock
%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/*.js
%exclude %{_appdir}/install.php
%{_appdir}/albums
%{_appdir}/bridge
%{_appdir}/docs
%{_appdir}/images
%{_appdir}/include
%{_appdir}/lang
%{_appdir}/logs
%{_appdir}/plugins
%{_appdir}/themes

%dir %attr(710,root,http) /var/lib/%{name}
%dir %attr(730,root,http) /var/lib/%{name}/albums
%dir %attr(730,root,http) /var/lib/%{name}/albums/edit
%dir %attr(730,root,http) /var/lib/%{name}/albums/userpics

%files setup
%defattr(644,root,root,755)
%{_appdir}/install.php
%{_appdir}/installer.css
%{_appdir}/sql
