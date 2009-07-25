From 848e4c68c4695beae563f9a3d59fce596b466a74 Mon Sep 17 00:00:00 2001
From: Tejun Heo <tj@kernel.org>
Date: Tue, 21 Oct 2008 14:26:39 +0900
Subject: [PATCH] libata: transfer EHI control flags to slave ehc.i
References: bnc#441420

ATA_EHI_NO_AUTOPSY and ATA_EHI_QUIET are used to control the behavior
of EH.  As only the master link is visible outside EH, these flags are
set only for the master link although they should also apply to the
slave link, which causes spurious EH messages during probe and
suspend/resume.

This patch transfers those two flags to slave ehc.i before performing
slave autopsy and reporting.

Signed-off-by: Tejun Heo <tj@kernel.org>
Signed-off-by: Jeff Garzik <jgarzik@redhat.com>
Signed-off-by: Tejun Heo <teheo@suse.de>
---
 drivers/ata/libata-eh.c |    5 +++++
 include/linux/libata.h  |    3 +++
 2 files changed, 8 insertions(+)

--- a/drivers/ata/libata-eh.c
+++ b/drivers/ata/libata-eh.c
@@ -1973,8 +1973,13 @@ void ata_eh_autopsy(struct ata_port *ap)
 		struct ata_eh_context *mehc = &ap->link.eh_context;
 		struct ata_eh_context *sehc = &ap->slave_link->eh_context;
 
+		/* transfer control flags from master to slave */
+		sehc->i.flags |= mehc->i.flags & ATA_EHI_TO_SLAVE_MASK;
+
+		/* perform autopsy on the slave link */
 		ata_eh_link_autopsy(ap->slave_link);
 
+		/* transfer actions from slave to master and clear slave */
 		ata_eh_about_to_do(ap->slave_link, NULL, ATA_EH_ALL_ACTIONS);
 		mehc->i.action		|= sehc->i.action;
 		mehc->i.dev_action[1]	|= sehc->i.dev_action[1];
--- a/include/linux/libata.h
+++ b/include/linux/libata.h
@@ -337,6 +337,9 @@ enum {
 
 	ATA_EHI_DID_RESET	= ATA_EHI_DID_SOFTRESET | ATA_EHI_DID_HARDRESET,
 
+	/* mask of flags to transfer *to* the slave link */
+	ATA_EHI_TO_SLAVE_MASK	= ATA_EHI_NO_AUTOPSY | ATA_EHI_QUIET,
+
 	/* max tries if error condition is still set after ->error_handler */
 	ATA_EH_MAX_TRIES	= 5,
 
