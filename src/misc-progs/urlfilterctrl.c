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

	if (strcmp(argv[1], "cron") == 0){
		safe_system("rm /etc/fcron.*/urlfilter 2&>/dev/null");

		if (strcmp(argv[2], "daily") == 0){
			safe_system("ln -s /var/ipfire/urlfilter/bin/autoupdate.pl /etc/fcron.daily/urlfilter");
		} else if (strcmp(argv[2], "weekly") == 0){
			safe_system("ln -s /var/ipfire/urlfilter/bin/autoupdate.pl /etc/fcron.weekly/urlfilter");
		} else if (strcmp(argv[2], "monthly") == 0){
			safe_system("ln -s /var/ipfire/urlfilter/bin/autoupdate.pl /etc/fcron.monthly/urlfilter");
		}else{
			printf("invalid parameter(s)\n");
		return(1);
		}
	}
	return 0;
}
