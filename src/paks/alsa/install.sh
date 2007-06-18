tar xvfj files.tbz2 -C /
touch /etc/asound.state
ln -sf  ../init.d/alsa /etc/rc.d/rc0.d/K35alsa
ln -sf  ../init.d/alsa /etc/rc.d/rc6.d/K35alsa
