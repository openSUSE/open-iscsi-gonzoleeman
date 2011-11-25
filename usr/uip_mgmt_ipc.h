/*
 * uIP iSCSI Daemon/Admin Management IPC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published
 * by the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * See the file COPYING included with this distribution for more details.
 */
#ifndef UIP_MGMT_IPC_H
#define UIP_MGMT_IPC_H

#include "types.h"
#include "iscsi_if.h"
#include "config.h"
#include "mgmt_ipc.h"

#include "initiator.h"
#include "transport.h"

#define ISCSID_UIP_NAMESPACE	"ISCSID_UIP_ABSTRACT_NAMESPACE"

typedef enum iscsid_uip_cmd {
	ISCSID_UIP_IPC_UNKNOWN			= 0,
	ISCSID_UIP_IPC_GET_IFACE		= 1,

        __ISCSID_UIP_IPC_MAX_COMMAND
} iscsid_uip_cmd_e;

typedef struct iscsid_uip_broadcast_header {
	iscsid_uip_cmd_e command;
	uint32_t payload_len;
} iscsid_uip_broadcast_header_t;

/* IPC Request */
typedef struct iscsid_uip_broadcast {
	struct iscsid_uip_broadcast_header header;

	union {
		/* messages */
		struct ipc_broadcast_iface_rec {
			struct iface_rec rec;
		} iface_rec;
	} u;
} iscsid_uip_broadcast_t;

typedef enum iscsid_uip_mgmt_ipc_err {
	ISCSID_UIP_MGMT_IPC_OK                     = 0,
        ISCISD_UIP_MGMT_IPC_ERR                    = 1,
        ISCISD_UIP_MGMT_IPC_ERR_NOT_FOUND          = 2,
        ISCISD_UIP_MGMT_IPC_ERR_NOMEM              = 3,
} iscsid_uip_mgmt_ipc_err_e;

/* IPC Response */
typedef struct iscsid_uip_mgmt_rsp {
	iscsid_uip_cmd_e command;
	iscsid_uip_mgmt_ipc_err_e err;
} iscsid_uip_rsp_t;

extern int uip_broadcast_params(struct iscsi_transport *t,
				struct iface_rec *iface,
				struct iscsi_session *session);
extern int uip_broadcast(void *buf, size_t buf_len);


#endif /* UIP_MGMT_IPC_H */
