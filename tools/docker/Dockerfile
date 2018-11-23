# This image is based on the latest stable version of Debian
FROM debian:stable

# Install all updates
RUN apt-get update && apt-get dist-upgrade

# Install all packages needed for the build
RUN apt-get install -y \
	build-essential \
	autoconf \
	automake \
	bison \
	flex \
	gawk \
	git \
	libz-dev

# Enable colors in git
RUN git config --global color.ui auto

WORKDIR ~
