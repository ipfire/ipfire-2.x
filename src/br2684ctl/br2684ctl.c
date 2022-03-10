#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <string.h>
#include <syslog.h>
#include <atm.h>
#include <linux/atmdev.h>
#include <linux/atmbr2684.h>

/* Written by Marcell GAL <cell@sch.bme.hu> to make use of the */
/* ioctls defined in the br2684... kernel patch */
/* Compile with cc -o br2684ctl br2684ctl.c -latm */

/*
  Modified feb 2001 by Stephen Aaskov (saa@lasat.com)
  - Added daemonization code
  - Added syslog

  TODO: Delete interfaces after exit?
*/


#define LOG_NAME "RFC1483/2684 bridge"
#define LOG_OPTION     LOG_PERROR
#define LOG_FACILITY   LOG_LOCAL0


int lastsock, lastitf;


void fatal(const char *str, int i)
{
  syslog (LOG_ERR,"Fatal: %s",str);
  exit(-2);
};


void exitFunc(void)
{
  syslog (LOG_PID,"Daemon terminated\n");
}


int create_pidfile(int num)
{
  FILE *pidfile = NULL;
  char name[32];

  if (num < 0) return -1;

  snprintf(name, 20, "/var/run/nas%d.pid", num);
  pidfile = fopen(name, "w");
  if (pidfile == NULL) return -1;
  fprintf(pidfile, "%d", getpid());
  fclose(pidfile);

  return 0;
}

int create_br(char *nstr)
{
  int num, err;

  if(lastsock<0) {
    lastsock = socket(PF_ATMPVC, SOCK_DGRAM, ATM_AAL5);
  }
  if (lastsock<0) {
    syslog(LOG_ERR, "socket creation failed: %s",strerror(errno));
  } else {
    /* create the device with ioctl: */
    num=atoi(nstr);
    if( num>=0 && num<1234567890){
      struct atm_newif_br2684 ni;
      ni.backend_num = ATM_BACKEND_BR2684;
      ni.media = BR2684_MEDIA_ETHERNET;
      ni.mtu = 1500;
      sprintf(ni.ifname, "nas%d", num);
      err=ioctl (lastsock, ATM_NEWBACKENDIF, &ni);

      if (err == 0)
	syslog(LOG_INFO, "Interface \"%s\" created sucessfully\n",ni.ifname);
      else
	syslog(LOG_INFO, "Interface \"%s\" could not be created, reason: %s\n",
	       ni.ifname,
	       strerror(errno));
      lastitf=num;	/* even if we didn't create, because existed, assign_vcc wil want to know it! */
    } else {
      syslog(LOG_ERR,"err: strange interface number %d", num );
    }
  }
  return 0;
}


int assign_vcc(char *astr, int encap, int bufsize, struct atm_qos qos)
{
    int err;
    struct sockaddr_atmpvc addr;
    int fd;
    struct atm_backend_br2684 be;

    memset(&addr, 0, sizeof(addr));
    err=text2atm(astr,(struct sockaddr *)(&addr), sizeof(addr), T2A_PVC);
    if (err!=0)
      syslog(LOG_ERR,"Could not parse ATM parameters (error=%d)\n",err);

#if 0
    addr.sap_family = AF_ATMPVC;
    addr.sap_addr.itf = itf;
    addr.sap_addr.vpi = 0;
    addr.sap_addr.vci = vci;
#endif
    syslog(LOG_INFO,"Communicating over ATM %d.%d.%d, encapsulation: %s\n", addr.sap_addr.itf,
	   addr.sap_addr.vpi,
	   addr.sap_addr.vci,
	   encap?"VC mux":"LLC");

    if ((fd = socket(PF_ATMPVC, SOCK_DGRAM, ATM_AAL5)) < 0)
      syslog(LOG_ERR,"failed to create socket %d, reason: %s", errno,strerror(errno));

    if (qos.aal == 0) {
      qos.aal                     = ATM_AAL5;
      qos.txtp.traffic_class      = ATM_UBR;
      qos.txtp.max_sdu            = 1524;
      qos.txtp.pcr                = ATM_MAX_PCR;
      qos.rxtp = qos.txtp;
    }

    if ( (err=setsockopt(fd,SOL_SOCKET,SO_SNDBUF, &bufsize ,sizeof(bufsize))) )
      syslog(LOG_ERR,"setsockopt SO_SNDBUF: (%d) %s\n",err, strerror(err));

    if (setsockopt(fd, SOL_ATM, SO_ATMQOS, &qos, sizeof(qos)) < 0)
      syslog(LOG_ERR,"setsockopt SO_ATMQOS %d", errno);

    err = connect(fd, (struct sockaddr*)&addr, sizeof(struct sockaddr_atmpvc));

    if (err < 0)
      fatal("failed to connect on socket", err);

    /* attach the vcc to device: */

    be.backend_num = ATM_BACKEND_BR2684;
    be.ifspec.method = BR2684_FIND_BYIFNAME;
    sprintf(be.ifspec.spec.ifname, "nas%d", lastitf);
    be.fcs_in = BR2684_FCSIN_NO;
    be.fcs_out = BR2684_FCSOUT_NO;
    be.fcs_auto = 0;
    be.encaps = encap ? BR2684_ENCAPS_VC : BR2684_ENCAPS_LLC;
    be.has_vpiid = 0;
    be.send_padding = 0;
    be.min_size = 0;
    err=ioctl (fd, ATM_SETBACKEND, &be);
    if (err == 0)
      syslog (LOG_INFO,"Interface configured");
    else {
      syslog (LOG_ERR,"Could not configure interface:%s",strerror(errno));
      exit(2);
    }
    return fd ;
}


void usage(char *s)
{
  printf("usage: %s [-b] [[-c number] [-e 0|1] [-s sndbuf] [-q qos] [-a [itf.]vpi.vci]*]*\n", s);
  exit(1);
}



int main (int argc, char **argv)
{
  int c, background=0, encap=0, sndbuf=8192;
  struct atm_qos reqqos;
  int itfnum;
  lastsock=-1;
  lastitf=0;

  /* st qos to 0 */
  memset(&reqqos, 0, sizeof(reqqos));

  openlog (LOG_NAME,LOG_OPTION,LOG_FACILITY);
  if (argc>1)
    while ((c = getopt(argc, argv,"q:a:bc:e:s:?h")) !=EOF)
      switch (c) {
      case 'q':
	printf ("optarg : %s",optarg);
	if (text2qos(optarg,&reqqos,0)) fprintf(stderr,"QOS parameter invalid\n");
	break;
      case 'a':
	assign_vcc(optarg, encap, sndbuf, reqqos);
	break;
      case 'b':
	background=1;
	break;
      case 'c':
	create_br(optarg);
	itfnum = atoi(optarg);
	break;
      case 'e':
	encap=(atoi(optarg));
	if(encap<0){
	  syslog (LOG_ERR, "invalid encapsulation: %s:\n",optarg);
	  encap=0;
	}
	break;
      case 's':
	sndbuf=(atoi(optarg));
	if(sndbuf<0){
	  syslog(LOG_ERR, "Invalid sndbuf: %s, using size of 8192 instead\n",optarg);
	  sndbuf=8192;
	}
	break;
      case '?':
      case 'h':
      default:
	usage(argv[0]);
      }
  else
    usage(argv[0]);

  if (argc != optind) usage(argv[0]);

  if(lastsock>=0) close(lastsock);

  if (background) {
    pid_t pid;

    pid=fork();
    if (pid < 0) {
      fprintf(stderr,"Error detaching\n");
      exit(2);
    } else if (pid)
      exit(0); // This is the parent

    // Become a process group and session group leader
    if (setsid()<0) {
      fprintf (stderr,"Could not set process group\n");
      exit(2);
    }

    // Fork again to let process group leader exit
    pid = fork();
    if (pid < 0) {
      fprintf(stderr,"Error detaching during second fork\n");
      exit(2);
    } else if (pid)
      exit(0); // This is the parent

    // Now we're ready for buisness
    chdir("/");            // Don't keep directories in use
    close(0); close(1); close(2);  // Close stdin, -out and -error
    /*
      Note that this implementation does not keep an open
      stdout/err.
      If we need them they can be opened now
    */

  }

  create_pidfile(itfnum);

  syslog (LOG_INFO, "RFC 1483/2684 bridge daemon started\n");
  atexit (exitFunc);

  while (1) sleep(30);	/* to keep the sockets... */
  return 0;
}

