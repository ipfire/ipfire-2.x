#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <fcntl.h>
#include "setuid.h"

int main(int argc, char *argv[]){
	if ( argc < 2 ){
		printf("invalid parameter(s)\n");
		return(1);
	}

	if (!(initsetuid()))
		exit(1);

	if (strcmp(argv[1], "start") == 0){
		safe_system("cp /var/ipfire/wlanap/hostapd.* /etc/");
		safe_system("/etc/init.d/hostapd start");
	}else if (strcmp(argv[1], "stop") == 0){
		safe_system("/etc/init.d/hostapd stop");
	}else if (strcmp(argv[1], "restart") == 0){
		safe_system("cp /var/ipfire/wlanap/hostapd.* /etc/");
		safe_system("/etc/init.d/hostapd restart");
	}else if (strcmp(argv[1], "status") == 0){
		safe_system("/etc/init.d/hostapd status");
	}else{
		printf("invalid parameter(s)\n");
		return(1);
	}

	return 0;
}
