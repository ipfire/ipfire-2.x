# Make sure the basic paths are always available.

pathmunge /bin
pathmunge /usr/bin
pathmunge /usr/local/bin

for directory in $(find /opt/*/bin -maxdepth 1 -type d 2>/dev/null); do
        pathmunge ${directory} after
done

unset directory
