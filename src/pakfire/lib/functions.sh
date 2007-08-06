#!/bin/bash

extract_files() {
	echo "Extracting files..."
	tar xvf /opt/pakfire/tmp/files -C /
	echo "...Finished."
}

reload_all() {
	reload_modules
	reload_libs
}

reload_libs() {
	echo "(Re-)Initializing the lib-cache..."	
	ldconfig
	echo "...Finished."
}

reload_modules() {
	echo "(Re-)Initializing the module-dependencies..."	
	depmod -a
	echo "...Finished."
}

restart_service() {
	
	/etc/init.d/$1 restart

}
