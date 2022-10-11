/* This file is part of the IPFire Firewall.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <dirent.h>
#include <fnmatch.h>
#include <errno.h>
#include "setuid.h"

#define BUFFER_SIZE 1024

const char *initd_path = "/etc/rc.d/init.d";
const char *enabled_path = "/etc/rc.d/rc3.d";
const char *disabled_path = "/etc/rc.d/rc3.d/off";

const char *usage = 
    "Usage\n"
    "  addonctrl <addon> (start|stop|restart|reload|enable|disable|status|boot-status|list-services) [<service>]\n"
    "\n"
    "Options:\n"
    "  <addon>\t\tName of the addon to control\n"
    "  <service>\t\tSpecific service of the addon to control (optional)\n"
    "  \t\t\tBy default the requested action is performed on all related services. See also 'list-services'.\n"
    "  start\t\t\tStart service(s) of the addon\n"
    "  stop\t\t\tStop service(s) of the addon\n"
    "  restart\t\tRestart service(s) of the addon\n"
    "  enable\t\tEnable service(s) of the addon to start at boot\n"
    "  disable\t\tDisable service(s) of the addon to start at boot\n"
    "  status\t\tDisplay current state of addon service(s)\n"
    "  boot-status\t\tDisplay wether service(s) is enabled on boot or not\n"
    "  list-services\t\tDisplay a list of services related to the addon";

// Find a file <path> using <filepattern> as glob pattern. 
// Returns the found filename or NULL if not found
char *find_file_in_dir(const char *path, const char *filepattern) 
{
    struct dirent *entry;
    DIR *dp;
    char *found = NULL;

    dp = opendir(path);
    if (dp) {
        entry = readdir(dp);
        while(!found && entry) {
            if (fnmatch(filepattern, entry->d_name, FNM_PATHNAME) == 0)
                found = strdup(entry->d_name);
            else
                entry = readdir(dp);
        }

        closedir(dp);
    }

    return found;
}

// Reads Services metadata for <addon>.
// Returns pointer to array of strings containing the services for <addon>,
// sets <servicescnt> to the number of found services and 
// sets <returncode> to 
// -1 - system error occured, check errno
// 0 - success - if returned array is NULL, there are no services for <addon>
// 1 - addon was not found
char **get_addon_services(const char *addon, int *servicescnt, const char *filter, int *returncode) {
    const char *metafile_prefix = "/opt/pakfire/db/installed/meta-";
    const char *metadata_key = "Services";
    const char *keyvalue_delim = ":";
    const char *service_delim = " ";
    char *token;
    char **services = NULL;
    char *service;
    char *line = NULL;
    size_t line_len = 0;
    int i = 0;
    char *metafile = NULL;

    *returncode = 0;
 
    if (!addon) {
        errno = EINVAL;
        *returncode = 1;
        return NULL;
    }

    *returncode = asprintf(&metafile, "%s%s", metafile_prefix, addon);
    if (*returncode == -1)
        return NULL;

    FILE *fp = fopen(metafile,"r");
    if (!fp) {
        if (errno == ENOENT) {
            *returncode = 1;
        } else {
            *returncode = -1;
        }
        return NULL;
    }

    // Get initscript(s) for addon from meta-file
    while (getline(&line, &line_len, fp) != -1 && !services) {
        // Strip newline
        char *newline = strchr(line, '\n');
        if (newline) *newline = 0;

        // Split line in key and values; Check for required key.
        token = strtok(line, keyvalue_delim);
        if (!token || strcmp(token, metadata_key) != 0) 
            continue;

        // Get values for matched key. Stop if no values are present.
        token = strtok(NULL, keyvalue_delim);
        if (!token) 
            break;

        // Split values and put each service in services array
        service = strtok(token, service_delim);
        while (service) {
            if (!filter || strcmp(filter, service) == 0) {
                services = reallocarray(services, i+1 ,sizeof (char *));
                if (!services) {
                    *returncode = -1;
                    break;
                } 

                services[i] = strdup(service);
                if (!services[i++]) {
                    *returncode = -1;
                    break;
                }
            }

            service = strtok(NULL, service_delim);
        }
    }

    if (line) free(line);
    fclose(fp);
    free(metafile);

    *servicescnt = i;

    return services;
}

// Calls initscript <service> with parameter <action>
int initscript_action(const char *service, const char *action) {
    char *initscript = NULL;
    char *argv[] = {
        action,
        NULL
    };
    int r = 0;

    r = asprintf(&initscript, "%s/%s", initd_path, service);
    if (r != -1)
        r = run(initscript, argv);

    if (initscript) free(initscript);

    return r; 
}

// Move an initscript with filepattern from <src_path> to <dest_path>
// Returns:
//   -1: Error during move or memory allocation. Details in errno
//   0: Success
//   1: file was not moved, but is already in <dest_path>
//   2: file does not exist in either in <src_path> or <dest_path>
int move_initscript_by_pattern(const char *src_path, const char *dest_path, const char *filepattern) {
    char *src = NULL;
    char *dest = NULL;
    int r = 2;
    char *filename = NULL;

    filename = find_file_in_dir(src_path, filepattern);
    if (filename) {
        // Move file
        r = asprintf(&src, "%s/%s", src_path, filename);
        if (r != -1) {
            r = asprintf(&dest, "%s/%s", dest_path, filename);
            if (r != -1)
                r = rename(src, dest);
        }

        if (src) free(src);
        if (dest) free(dest);
    } else {
        // check if file is already in dest
        filename = find_file_in_dir(dest_path, filepattern);
        if (filename) 
            r = 1;
    }

    if (filename) free(filename);

    return r;
}

// Enable/Disable addon service(s) by moving initscript symlink from/to disabled_path
// Returns:
// -1 - System error occured. Check errno.
// 0 - Success
// 1 - Service was already enabled/disabled
// 2 - Service has no valid runlevel symlink
int toggle_service(const char *service, const char *action) {
    const char *src_path, *dest_path;
    char *filepattern = NULL; 
    int r = 0;
    
    if (asprintf(&filepattern, "S??%s", service) == -1)
        return -1;

    if (strcmp(action, "enable") == 0) {
        src_path = disabled_path;
        dest_path = enabled_path;
    } else {
        src_path = enabled_path;
        dest_path = disabled_path;
    }

    // Ensure disabled_path exists
    r = mkdir(disabled_path, S_IRWXU + S_IRGRP + S_IXGRP + S_IROTH + S_IXOTH); 
    if (r != -1 || errno == EEXIST)
        r = move_initscript_by_pattern(src_path, dest_path, filepattern);

    free(filepattern);
    
    return r;
}

// Return whether <service> is enabled or disabled on boot
// Returns:
// -1 - System error occured. Check errno.
// 0 - <service> is disabled on boot
// 1 - <service> is enabled on boot
// 2 - Runlevel suymlink for <service> was not found
int get_boot_status(char *service) {
    char *filepattern = NULL;
    char *filename = NULL;
    int r = 2;

    if (asprintf(&filepattern, "S??%s", service) == -1)
        return -1;

    filename = find_file_in_dir(enabled_path, filepattern);
    if (filename)
        r = 1;
    else {
        filename = find_file_in_dir(disabled_path, filepattern);
        if (filename)
            r = 0;
        else
            r = 2;
    }

    if (filename) free(filename);
    free(filepattern);

    return r;
}

int main(int argc, char *argv[]) {
    char **services = NULL;
    int servicescnt = 0;
    char *addon = argv[1];
    char *action = argv[2];
    char *service_filter = NULL;
    int r = 0;

    if (!(initsetuid()))
        exit(1);

    if (argc < 3) {
        fprintf(stderr, "\nMissing arguments.\n\n%s\n\n", usage);
        exit(1);
    }

    // Ignore filter when list of services is requested
    if (argc == 4 && strcmp(action, "list-services") != 0)
        service_filter = argv[3];

    if (strlen(addon) > 32) {
        fprintf(stderr, "\nString too large.\n\n%s\n\n", usage);
        exit(1);
    }

    // Check if the input argument is valid
    if (!is_valid_argument_alnum(addon)) {
        fprintf(stderr, "Invalid add-on name: %s.\n", addon);
        exit(2);
    }

    // Get initscript name(s) from addon metadata
    int rc = 0;
    services = get_addon_services(addon, &servicescnt, service_filter, &rc);
    if (!services) {
        switch (rc) {
            case -1:
                fprintf(stderr, "\nSystem error occured. (Error: %m)\n\n");
                break;

            case 0:
                if (service_filter)
                    fprintf(stderr, "\nNo service '%s' found for addon '%s'. Use 'list-services' to get a list of available services\n\n%s\n\n", service_filter, addon, usage);
                else
                    fprintf(stderr, "\nAddon '%s' has no services.\n\n", addon);
                break;

            case 1:
                fprintf(stderr, "\nAddon '%s' not found.\n\n%s\n\n", addon, usage);
                break;
        }
        exit(1);
    }
        
    // Handle requested action
    if (strcmp(action, "start") == 0 ||
        strcmp(action, "stop") == 0 ||
        strcmp(action, "restart") == 0 ||
        strcmp(action, "reload") == 0 ||
        strcmp(action, "status") == 0) {

        for(int i = 0; i < servicescnt; i++) {
            if (initscript_action(services[i], action) < 0) {
                r = 1;
                fprintf(stderr, "\nSystem error occured. (Error: %m)\n\n");
                break;
            }
        }

    } else if (strcmp(action, "enable") == 0 ||
               strcmp(action, "disable") == 0) {

        for(int i = 0; i < servicescnt; i++) {
            switch (r = toggle_service(services[i], action)) {
                case -1:
                    fprintf(stderr, "\nSystem error occured. (Error: %m)\n\n");
                    break;

                case 0:
                    printf("%sd service %s\n", action, services[i]);
                    break;
                
                case 1:
                    fprintf(stderr, "Service %s is already %sd. Skipping...\n", services[i], action);
                    break;

                case 2:
                    fprintf(stderr, "\nUnable to %s service %s. (Service has no valid runlevel symlink).\n\n", action, services[i]);
                    break;
            }

            // Break from for loop in case of a system error.
            if (r == -1) {
                r = 1;
                break;
            }
        }

    } else if (strcmp(action, "boot-status") == 0) {
        // Print boot status for each service
        for(int i = 0; i < servicescnt; i++) {
            switch (get_boot_status(services[i])) {
                case -1:
                    r = 1;
                    fprintf(stderr, "\nSystem error occured. (Error: %m)\n\n");
                    break;
                
                case 0:
                    printf("%s is disabled on boot.\n", services[i]);
                    break;
                
                case 1:
                    printf("%s is enabled on boot.\n", services[i]);
                    break;

                case 2:
                    printf("%s is not available for boot. (Service has no valid symlink in either %s or %s).\n", services[i], enabled_path, disabled_path);
                    break;
            }
            
            // Break from for loop in case of an error
            if (r == 1) {
                break;
            }
        }
    
    } else if (strcmp(action, "list-services") == 0) {
        // List all services for addon
        printf("\nServices for addon %s:\n", addon);
        for(int i = 0; i < servicescnt; i++) {
            printf("  %s\n", services[i]);
        }
        printf("\n");

    } else {
        fprintf(stderr, "\nBad argument given.\n\n%s\n\n", usage);
        r = 1;
    }

    // Cleanup
    for(int i = 0; i < servicescnt; i++) 
        free(services[i]);
    free(services);

    return r;
}
