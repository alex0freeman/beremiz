#include <mblib.h>

/* The total number of nodes, needed to support _all_ instances of the modbus plugin */
#define TOTAL_TCPNODE_COUNT       %(total_tcpnode_count)s
#define TOTAL_RTUNODE_COUNT       %(total_rtunode_count)s
#define TOTAL_ASCNODE_COUNT       %(total_ascnode_count)s

/* Values for instance %(locstr)s of the modbus plugin */
#define MAX_NUMBER_OF_TCPCLIENTS  %(max_remote_tcpclient)s

#define NUMBER_OF_TCPSERVER_NODES %(tcpserver_node_count)s
#define NUMBER_OF_TCPCLIENT_NODES %(tcpclient_node_count)s
#define NUMBER_OF_TCPCLIENT_REQTS %(tcpclient_reqs_count)s

#define NUMBER_OF_RTUSERVER_NODES %(rtuserver_node_count)s
#define NUMBER_OF_RTUCLIENT_NODES %(rtuclient_node_count)s
#define NUMBER_OF_RTUCLIENT_REQTS %(rtuclient_reqs_count)s

#define NUMBER_OF_ASCIISERVER_NODES %(ascserver_node_count)s
#define NUMBER_OF_ASCIICLIENT_NODES %(ascclient_node_count)s
#define NUMBER_OF_ASCIICLIENT_REQTS %(ascclient_reqs_count)s

#define NUMBER_OF_SERVER_NODES (NUMBER_OF_TCPSERVER_NODES + \
                                NUMBER_OF_RTUSERVER_NODES + \
                                NUMBER_OF_ASCIISERVER_NODES)

#define NUMBER_OF_CLIENT_NODES (NUMBER_OF_TCPCLIENT_NODES + \
                                NUMBER_OF_RTUCLIENT_NODES + \
                                NUMBER_OF_ASCIICLIENT_NODES)

#define NUMBER_OF_CLIENT_REQTS (NUMBER_OF_TCPCLIENT_REQTS + \
                                NUMBER_OF_RTUCLIENT_REQTS + \
                                NUMBER_OF_ASCIICLIENT_REQTS)


#define NUMBER_OF_REGISTER %(registers_count)s

/*initialization following all parameters given by user in application*/

static client_node_t		client_nodes[NUMBER_OF_CLIENT_NODES] = {
%(client_nodes_params)s
};


static client_request_t	client_requests[NUMBER_OF_CLIENT_REQTS] = {
%(client_req_params)s
};



static request_registers_t request_registers[NUMBER_OF_REGISTER] = {
%(registers_params)s
};

/*******************/
/*located variables*/
/*******************/

%(loc_vars)s