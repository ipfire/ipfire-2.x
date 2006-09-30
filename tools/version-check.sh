#!/bin/bash

# Einfaches Skript zum Auflisten der Versionsnummern wichtiger Werkzeuge

echo "BENOETIGT - VORHANDEN"
echo -n "Bash-2.05a - " 
bash --version | head -n1 | cut -d" " -f2-4

echo -n "Binutils-2.12 - "
echo -n "Binutils: "; ld --version | head -n1 | cut -d" " -f3-4

echo -n "Bzip2-1.0.2 - "
bzip2 --version 2>&1 < /dev/null | head -n1 | cut -d" " -f1,6-

echo -n "Coreutils-5.0 - "
echo -n "Coreutils: "; chown --version | head -n1 | cut -d")" -f2

echo -n "Diffutils-2.8 - "
diff --version | head -n1

echo -n "Findutils-4.1.20 - "
find --version | head -n1

echo -n "Gawk-3.0 - "
gawk --version | head -n1

echo -n "Gcc-2.95.3 - "
gcc --version | head -n1

echo -n "Glibc-2.2.5 - "
/lib/libc.so.6 | head -n1 | cut -d" " -f1-7

echo -n "Grep-2.5 - "
grep --version | head -n1

echo -n "Gzip-1.2.4 - "
gzip --version | head -n1

echo -n "Linux-Kernel-2.6 - "
cat /proc/version | head -n1 | cut -d" " -f1-3,5-7

echo -n "Make-3.79.1 - "
make --version | head -n1

echo -n "Patch-2.5.4 - "
patch --version | head -n1

echo -n "Sed-3.0.2 - "
sed --version | head -n1

echo -n "Tar-1.14 - "
tar --version | head -n1
