#!/bin/bash
set -x

mkdir -p ~/rpmbuild/ ~/rpmbuild/BUILD ~/rpmbuild/SPECS ~/rpmbuild/SRPMS ~/rpmbuild/BUILDROOT ~/rpmbuild/SOURCES ~/rpmbuild/RPMS
readlink -f ./refactor-1.0.0.spec | xargs -I {} ln -sf {} ~/rpmbuild/SPECS/refactor-1.0.0.spec
$(cd ../ && tar -czf ~/rpmbuild/SOURCES/refactor.tar.gz ./bin)
rpmbuild -ba ~/rpmbuild/SPECS/refactor-1.0.0.spec
