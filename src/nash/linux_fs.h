/* Including <linux/fs.h> became more and more painful.
   Below a very abbreviated version of some declarations,
   only designed to be able to check a magic number
   in case no filesystem type was given. */

#ifndef BLKGETSIZE
#ifndef _IO
/* pre-1.3.45 */
#define BLKGETSIZE 0x1260		   /* return device size */
#else
/* same on i386, m68k, arm; different on alpha, mips, sparc, ppc */
#define BLKGETSIZE _IO(0x12,96)
#endif
#endif

#define MINIX_SUPER_MAGIC   0x137F         /* original minix fs */
#define MINIX_SUPER_MAGIC2  0x138F         /* minix fs, 30 char names */
struct minix_super_block {
	unsigned char   s_dummy[16];
	unsigned char   s_magic[2];
};
#define minixmagic(s)	((unsigned int) s.s_magic[0] + (((unsigned int) s.s_magic[1]) << 8))

#define ISODCL(from, to) (to - from + 1)
#define ISO_STANDARD_ID "CD001"
struct iso_volume_descriptor {
	char type[ISODCL(1,1)]; /* 711 */
	char id[ISODCL(2,6)];
	char version[ISODCL(7,7)];
	char data[ISODCL(8,2048)];
};

#define HS_STANDARD_ID "CDROM"
struct  hs_volume_descriptor {
	char foo[ISODCL (  1,   8)]; /* 733 */
	char type[ISODCL (  9,   9)]; /* 711 */
	char id[ISODCL ( 10,  14)];
	char version[ISODCL ( 15,  15)]; /* 711 */
	char data[ISODCL(16,2048)];
};

#define EXT_SUPER_MAGIC 0x137D
struct ext_super_block {
	unsigned char   s_dummy[56];
	unsigned char   s_magic[2];
};
#define extmagic(s)	((unsigned int) s.s_magic[0] + (((unsigned int) s.s_magic[1]) << 8))

#define EXT2_PRE_02B_MAGIC  0xEF51
#define EXT2_SUPER_MAGIC    0xEF53
#define EXT3_FEATURE_COMPAT_HAS_JOURNAL 0x0004
struct ext2_super_block {
	unsigned char 	s_dummy1[56];
	unsigned char 	s_magic[2];
	unsigned char	s_dummy2[34];
	unsigned char	s_feature_compat[4];
	unsigned char	s_feature_incompat[4];
	unsigned char	s_feature_ro_compat[4];
	unsigned char	s_uuid[16];
	unsigned char 	s_volume_name[16];
	unsigned char	s_dummy3[88];
	unsigned char	s_journal_inum[4];	/* ext3 only */
};
#define ext2magic(s)	((unsigned int) s.s_magic[0] + (((unsigned int) s.s_magic[1]) << 8))

struct reiserfs_super_block
{
	unsigned char		s_block_count[4];
	unsigned char		s_free_blocks[4];
	unsigned char		s_root_block[4];
	unsigned char		s_journal_block[4];
	unsigned char		s_journal_dev[4];
	unsigned char		s_orig_journal_size[4];
	unsigned char		s_journal_trans_max[4];
	unsigned char		s_journal_block_count[4];
	unsigned char		s_journal_max_batch[4];
	unsigned char		s_journal_max_commit_age[4];
	unsigned char		s_journal_max_trans_age[4];
	unsigned char		s_blocksize[2];
	unsigned char		s_oid_maxsize[2];
	unsigned char		s_oid_cursize[2];
	unsigned char		s_state[2];
	unsigned char		s_magic[12];
};
#define REISERFS_SUPER_MAGIC_STRING "ReIsErFs"
#define REISER2FS_SUPER_MAGIC_STRING "ReIsEr2Fs"
#define REISERFS_DISK_OFFSET_IN_BYTES (64 * 1024)
/* the spot for the super in versions 3.5 - 3.5.10 (inclusive) */
#define REISERFS_OLD_DISK_OFFSET_IN_BYTES (8 * 1024)

#define _XIAFS_SUPER_MAGIC 0x012FD16D
struct xiafs_super_block {
    unsigned char     s_boot_segment[512];     /*  1st sector reserved for boot */
    unsigned char     s_dummy[60];
    unsigned char     s_magic[4];
};
#define xiafsmagic(s)	((unsigned int) s.s_magic[0] + (((unsigned int) s.s_magic[1]) << 8) + \
			(((unsigned int) s.s_magic[2]) << 16) + \
			(((unsigned int) s.s_magic[3]) << 24))

/* From jj@sunsite.ms.mff.cuni.cz Mon Mar 23 15:19:05 1998 */
#define UFS_SUPER_MAGIC 0x00011954
struct ufs_super_block {
    unsigned char     s_dummy[0x55c];
    unsigned char     s_magic[4];
};
#define ufsmagic(s)	((unsigned int) s.s_magic[0] + (((unsigned int) s.s_magic[1]) << 8) + \
			 (((unsigned int) s.s_magic[2]) << 16) + \
			 (((unsigned int) s.s_magic[3]) << 24))

/* From Richard.Russon@ait.co.uk Wed Feb 24 08:05:27 1999 */
#define NTFS_SUPER_MAGIC "NTFS"
struct ntfs_super_block {
    unsigned char    s_dummy[3];
    unsigned char    s_magic[4];
};

/* From inspection of a few FAT filesystems - aeb */
/* Unfortunately I find almost the same thing on an extended partition;
   it looks like a primary has some directory entries where the extended
   has a partition table: IO.SYS, MSDOS.SYS, WINBOOT.SYS */
struct fat_super_block {
    unsigned char    s_dummy[3];
    unsigned char    s_os[8];		/* "MSDOS5.0" or "MSWIN4.0" or "MSWIN4.1" */
				/* mtools-3.9.4 writes "MTOOL394" */
    unsigned char    s_dummy2[32];
    unsigned char    s_label[11];	/* for DOS? */
    unsigned char    s_fs[8];		/* "FAT12   " or "FAT16   " or all zero   */
                                /* OS/2 BM has "FAT     " here. */
    unsigned char    s_dummy3[9];
    unsigned char    s_label2[11];	/* for Windows? */
    unsigned char    s_fs2[8];	        /* garbage or "FAT32   " */
};

#define XFS_SUPER_MAGIC "XFSB"
struct xfs_super_block {
    unsigned char    s_magic[4];
    unsigned char    s_dummy[28];
    unsigned char    s_uuid[16];
    unsigned char    s_dummy2[60];
    unsigned char    s_fname[12];
};

#define CRAMFS_SUPER_MAGIC 0x28cd3d45
struct cramfs_super_block {
	unsigned char    s_magic[4];
	unsigned char    s_dummy[12];
	unsigned char    s_id[16];
};
#define cramfsmagic(s)	((unsigned int) s.s_magic[0] + (((unsigned int) s.s_magic[1]) << 8) + \
			 (((unsigned int) s.s_magic[2]) << 16) + \
			 (((unsigned int) s.s_magic[3]) << 24))

#define HFS_SUPER_MAGIC 0x4244
struct hfs_super_block {
	unsigned char    s_magic[2];
	unsigned char    s_dummy[18];
	unsigned char    s_blksize[4];
};
#define hfsmagic(s)	((unsigned int) s.s_magic[0] + (((unsigned int) s.s_magic[1]) << 8))
#define hfsblksize(s)	((unsigned int) s.s_blksize[0] + \
			 (((unsigned int) s.s_blksize[1]) << 8) + \
			 (((unsigned int) s.s_blksize[2]) << 16) + \
			 (((unsigned int) s.s_blksize[3]) << 24))

#define HPFS_SUPER_MAGIC 0xf995e849
struct hpfs_super_block {
	unsigned char    s_magic[4];
	unsigned char    s_magic2[4];
};
#define hpfsmagic(s)	((unsigned int) s.s_magic[0] + (((unsigned int) s.s_magic[1]) << 8) + \
			 (((unsigned int) s.s_magic[2]) << 16) + \
			 (((unsigned int) s.s_magic[3]) << 24))

struct adfs_super_block {
	unsigned char    s_dummy[448];
	unsigned char    s_blksize[1];
	unsigned char    s_dummy2[62];
	unsigned char    s_checksum[1];
};
#define adfsblksize(s)	((unsigned int) s.s_blksize[0])
