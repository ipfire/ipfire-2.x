#!/bin/bash

extract_files() {
	echo "Extracting files..."
	cd / && cpio -i < /opt/pakfire/tmp/files
	
}
