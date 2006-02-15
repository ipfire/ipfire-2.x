/* $Id: ibod.h,v 1.1.1.1 2001/11/27 08:08:03 riddles Exp $
 * $Symbol$
 */

#define DEVICE			"ippp0"
#define ENABLE			1
#define INTERVAL			500
#define FILTER			5
#define LIMIT			7000
#define STAYUP			0
#define STAYUP_TIME		30

#define IBOD_DEFAULT_DIR	"/etc/ppp"
#define MAX_STR_LEN		512
#define ISDN_INFO_DEV		"/dev/isdninfo"
#define ISDN_CTLR_DEV		"/dev/isdnctrl"
#define IBOD_PORT			6050

#define CMD_OPEN			0
#define CMD_CLOSE			1
#define CMD_ENABLE		2
#define CMD_DISABLE		3
#define CMD_UP2			4
#define CMD_DOWN2			5

typedef struct {
	char	dev[32];
	int	enable;
	int	interval;
	int	limit;
	int	filter;
	int	stayup;
	int	stayup_time;
} Conf;

typedef struct {
	unsigned long ibytes;
	unsigned long obytes;
} Siobytes;
