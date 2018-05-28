Name:          	refactor
Version:       	1.0.0
Release:        1%{?dist}
Summary:        refactor 1.0.0

License:        MIT
Source0:       	refactor.tar.gz

BuildRoot: %{_tmppath}/refactor.tar.gz

%description

%prep
%setup -n %{name}

%build
# None required

%install
install -m 755 -d %{buildroot}/usr/bin
cp -a refactor %{buildroot}/usr/bin

%clean

%files
%defattr(-,root,root)
/usr/bin/refactor
