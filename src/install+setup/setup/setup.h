/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Main include file.
 * 
 * $Id: setup.h,v 1.4 2003/12/11 11:25:54 riddles Exp $
 * 
 */

#include "../libsmooth/libsmooth.h"

/* hostname.c */
int handlehostname(void);

/* domainname.c */
int handledomainname(void);

/* isdn.c */
int handleisdn(void);

/* networking.c */
int handlenetworking(void);

/* dhcp.c */
int handledhcp(void);

/* passwords.c */
int handlerootpassword(void);
int handlesetuppassword(void);
int handleadminpassword(void);

/* misc.c */
int writehostsfiles(void);

/* keymap.c */
int handlekeymap(void);

/* timezone.c */
int handletimezone(void);
