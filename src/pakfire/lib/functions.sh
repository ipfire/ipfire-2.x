#!/bin/bash

extract_files() {
	echo "Extracting files..."
	tar xvf /opt/pakfire/tmp/files -C /
	echo "...Finished."
}
