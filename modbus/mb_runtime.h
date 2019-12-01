
#define DEF_REQ_SEND_RETRIES 0

  // Used by the Modbus server node
#define MEM_AREA_SIZE 65536
typedef struct{
	    u16		ro_bits [MEM_AREA_SIZE];
	    u16		rw_bits [MEM_AREA_SIZE];
	    u16		ro_words[MEM_AREA_SIZE];
	    u16		rw_words[MEM_AREA_SIZE];
	} server_mem_t;

typedef struct{
	    const char *location;
	    u8		slave_id;
	    node_addr_t	node_address;
	    int		mb_nd;      // modbus library node used for this server
	    int		init_state; // store how far along the server's initialization has progressed
	    pthread_t	thread_id;  // thread handling this server
	    server_mem_t	mem_area;
	} server_node_t;


  // Used by the Modbus client node
typedef struct{
	    const char *location;
	    node_addr_t	node_address;
	    int		mb_nd;
	    int		init_state; // store how far along the client's initialization has progressed
	    u64		comm_period;
	    int		prev_error; // error code of the last printed error message (0 when no error)
	    pthread_t	thread_id;  // thread handling all communication with this client
	} client_node_t;


  // Used by the Modbus client plugin
typedef enum {
	    req_input,
	    req_output,
	    no_request		/* just for tests to quickly disable a request */
	} iotype_t;

#define REQ_BUF_SIZE 2000
typedef struct{
	    const char *location;
	    int		client_node_id;
	    u8		slave_id;
	    iotype_t	req_type;
	    u8		mb_function;
	    u16		address;
	    u16		count;
	    int		retries;
	    u8		error_code; // modbus error code (if any) of current request
	    int		prev_error; // error code of the last printed error message (0 when no error)
	    struct timespec resp_timeout;
	      // buffer used to store located PLC variables
	    u16		plcv_buffer[REQ_BUF_SIZE];
	      // buffer used to store data coming from / going to server
	    u16		coms_buffer[REQ_BUF_SIZE];
	    u16 offset;
	    u16 scale;
	    pthread_mutex_t coms_buf_mutex; // mutex to access coms_buffer[]
	} client_request_t;


#define RGISTR_SIZE 16
typedef struct{
	    u16     address;
	    u16	    num_bit[RGISTR_SIZE];

	} request_registers_t;

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


static server_node_t		server_nodes[NUMBER_OF_SERVER_NODES] = {
%(server_nodes_params)s
};


static request_registers_t request_registers[NUMBER_OF_REGISTER] = {
%(registers_params)s
};

/*******************/
/*located variables*/
/*******************/

%(loc_vars)s