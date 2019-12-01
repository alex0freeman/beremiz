#include "mb_headers.h"

#define TOTAL_TCPNODE_COUNT %(total_tcpnode_count)s
#define MAX_NUMBER_OF_TCPCLIENTS %(max_remote_tcpclient)s
#define NUMBER_OF_CLIENT_NODES %(tcpclient_node_count)s
#define NUMBER_OF_CLIENT_REQTS %(tcpclient_reqs_count)s
#define NUMBER_OF_REGISTER %(registers_count)s

static client_node_t client_nodes[NUMBER_OF_CLIENT_NODES] = {
%(client_nodes_params)s
};

static client_request_t	client_requests[NUMBER_OF_CLIENT_REQTS] = {
%(client_req_params)s
};

static request_registers_t request_registers[NUMBER_OF_REGISTER] = {
%(registers_params)s
};

%(loc_vars)s