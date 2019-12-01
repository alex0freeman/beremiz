
#ifndef SOCKET_CUSTOM_H
#define SOCKET_CUSTOM_H

#if defined _WIN64 || defined _WIN32
#include <winsock2.h>
#include <windows.h>
#include <ws2tcpip.h>
#else
#include <unistd.h>
#endif

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Define max registers and bits  */
#define MAX_READ_BITS           2000    /* Functions 0x01 and 0x02 */
#define MAX_READ_REGS           125     /* Functions 0x03 and 0x04 */
#define MAX_WRITE_COILS         1968    /* Function 0x0F */
#define MAX_WRITE_REGS          123     /* Function 0x10 */

/* We use the _leastX_t versions of the data types as these are guaranteed
 * to be the exact size we want.
 * The int8_t, etc..., may have been defined to be the same as the
 * _fastX_t version, which may take up more space than what is really wanted
 * in order as to speed up memory access.
 */
typedef uint_least64_t      u64; /* 64-bit unsigned integer */
typedef  int_least64_t      i64; /* 64-bit signed integer   */

typedef uint_least32_t      u32; /* 32-bit unsigned integer */
typedef  int_least32_t      i32; /* 32-bit signed integer   */

typedef uint_least16_t      u16; /* 16-bit unsigned integer */
typedef  int_least16_t      i16; /* 16-bit signed integer   */

typedef uint_least8_t       u8;  /*  8-bit unsigned integer */
typedef  int_least8_t       i8;  /*  8-bit signed integer   */

 /* Layer 1 - TCP Frame sizes... */
#define TCP_HEADER_LENGTH       6

#define MB_MASTER_NODE 12
#define MB_LISTEN_NODE 14
#define MB_SLAVE_NODE  16
#define MB_FREE_NODE   18

typedef ADDRESS_FAMILY sa_family_t;
typedef sa_family_t nd_type_t;

typedef sa_family_t nd_type_t;

typedef struct {
	int    fd;                 /* socket descriptor == file descriptor */
							   /* NOTE:
								*   Modbus TCP says that on error, we should close
								*   a connection and retry with a new connection.
								*   Since it takes time for a socket to close
								*   a connection if the remote server is down,
								*   we close the connection on the socket, close the
								*   socket itself, and create a new one for the new
								*   connection. There will be times when the node will
								*   not have any valid socket, and it will have to
								*   be created on the fly.
								*   When the node does not have a valid socket,
								*   fd will be set to -1
								*/
	int    node_type;          /*   What kind of use we are giving to this node...
								*   If node_type == MB_MASTER_NODE
								*      The node descriptor was initialised by the
								*      modbus_connect() function.
								*      The node descriptor is being used by a master
								*      device, and the addr contains the address of the slave.
								*      Remember that in this case fd may be >= 0 while
								*      we have a valid connection, or it may be < 0 when
								*      the connection needs to be reset.
								*   If node_type == MB_LISTEN_NODE
								*      The node descriptor was initialised by the
								*      modbus_listen() function.
								*      The node is merely used to accept() new connection
								*      requests. The new slave connections will use another
								*      node to transfer data.
								*      In this case fd must be >= 0.
								*      fd < 0 is an ilegal state and should never occur.
								*   If node_type == MB_SLAVE_NODE
								*      The node descriptor was initialised when a new
								*      connection request arrived on a MB_LISTEN type node.
								*      The node descriptor is being used by a slave device,
								*      and is currently being used to connect to a master.
								*      In this case fd must be >= 0.
								*      fd < 0 is an ilegal state and should never occur.
								*   If node_type == FREE_ND
								*      The node descriptor is currently not being used.
								*      In this case fd is set to -1, but is really irrelevant.
								*/
	struct sockaddr_in addr;   /* The internet adress we are using.
								*   If node_type == MB_MASTER_NODE
								*      addr will be the address of the remote slave
								*   If node_type == MB_LISTEN_NODE
								*      addr will be the address of the local listening port and network interface
								*   If node_type == MB_SLAVE_NODE
								*      addr will be the address of the local port and network interface
								*       of the connection to the specific client.
								*/
	int listen_node;           /* When a slave accepts a connection through a MB_LISTEN_NODE, it will
								* will use an empty node for the new connection, and configure this new node
								* to use the type MB_SLAVE_NODE.
								* The listen_node entry is only used by nodes of type MB_SLAVE_NODE.
								* In this case, listen_node will be the node of type MB_LISTEN_NODE through
								* which the connection request came through...
								*/
	int close_on_silence;      /* A flag used only by Master Nodes.
								* When (close_on_silence > 0), then the connection to the
								* slave device will be shut down whenever the
								* modbus_tcp_silence_init() function is called.
								* Remember that the connection will be automatically
								* re-established the next time the user wishes to communicate
								* with the same slave (using this same node descripto).
								* If the user wishes to comply with the sugestion
								* in the OpenModbus Spec, (s)he should set this flag
								* if a silence interval longer than 1 second is expected.
								*/
	int print_connect_error;   /* flag to guarantee we only print an error the first time we
								* attempt to connect to a emote server.
								* Stops us from generting a cascade of errors while the slave
								* is down.
								* Flag will get reset every time we successfully
								* establish a connection, so a message is once again generated
								* on the next error.
								*/
	u8* recv_buf;              /* This node's receive buffer
								* The library supports multiple simultaneous connections,
								* and may need to receive multiple frames through mutiple nodes concurrently.
								* To make the library thread-safe, we use one buffer for each node.
								*/
} nd_entry_t;


typedef struct {
	/* the array of node descriptors, and current size... */
	nd_entry_t* node;           /* array of node entries. if NULL => node table not initialized */
	int             node_count;      /* total number of nodes in the node[] array */
	int             free_node_count; /* number of free nodes in the node[] array */
	CONST HANDLE  mutex;
} nd_table_t;



/* Library Error codes */
#define PORT_FAILURE   -101
#define INTERNAL_ERROR -102
#define TIMEOUT        -103
#define INVALID_FRAME  -104
#define MODBUS_ERROR   -105


 /* Layer 2 Frame Structure...                */
 /* Valid for both master and slave protocols */
#define L2_FRAME_HEADER_LENGTH    6
#define L2_FRAME_BYTECOUNT_LENGTH 1
//#define L2_FRAME_DATABYTES_LENGTH 255
#define L2_FRAME_DATABYTES_LENGTH 5
#define MAX_L2_FRAME_LENGTH (L2_FRAME_HEADER_LENGTH + L2_FRAME_BYTECOUNT_LENGTH +    \
                             L2_FRAME_DATABYTES_LENGTH)

#define QUERY_BUFFER_SIZE       (255)//


#ifdef WIN32

/* same as WSABUF */
struct iovec {
	u_long iov_len;
	char* iov_base;

};

struct msghdr {
	void* msg_name;       /* optional address */
	socklen_t     msg_namelen;    /* size of address */
	struct iovec* msg_iov;        /* scatter/gather array */
	size_t        msg_iovlen;     /* # elements in msg_iov */
	void* msg_control;    /* ancillary data, see below */
	size_t        msg_controllen; /* ancillary data buffer len */
	int           msg_flags;      /* flags on received message */
};

#define inline __inline

static inline int writev(int sock, struct iovec* iov, int nvecs)
{
	DWORD ret;
	if (WSASend(sock, (LPWSABUF)iov, nvecs, &ret, 0, NULL, NULL) == 0) {
		return ret;

	}
	return -1;
}


typedef ADDRESS_FAMILY sa_family_t;
typedef sa_family_t nd_type_t;

SOL_TCP = IPPROTO_TCP;
SOL_IP = IPPROTO_IPV4;
#define	IPTOS_LOWDELAY		0x10

#endif /* WIN32 */



#define REQ_BUF_SIZE 2000

struct custom_socket {
	//SOCKET ListenSocket;
	SOCKET ClientSocket;
	uint16_t Port;
	uint16_t BufferSize;
	uint16_t ThreadSleepingTime;
	bool Connected;
	bool Stopped;
	char* SendPacket;

	char* ReceivePacket;
	int receiveByte;

	u16	  plcv_buffer[REQ_BUF_SIZE];
	u8  p_buffer[REQ_BUF_SIZE];
	u8  send_buffer[REQ_BUF_SIZE];
};

#define RGISTR_SIZE 16

#define BIT_IN_WORD 16


#if defined(_MSC_VER) && (_MSC_VER >= 1400)
#  define bswap_32 _byteswap_ulong
#  define bswap_16 _byteswap_ushort
#endif

#define DEF_REQ_SEND_RETRIES 0

#define DEF_CLOSE_ON_SILENCE 1    /* Used only by master nodes.
								   * Flag indicating whether, by default, the connection
								   * to the slave device should be closed whenever the
								   * modbus_tcp_silence_init() function is called.
								   *
								   * 0  -> do not close connection
								   * >0 -> close connection
								   *
								   * The spec sugests that connections that will not
								   * be used for longer than 1 second should be closed.
								   * Even though we expect most connections to have
								   * silence intervals much shorted than 1 second, we
								   * decide to use the default of shuting down the
								   * connections because it is safer, and most other
								   * implementations seem to do the same.
								   * If we do not close we risk using up all the possible
								   * connections that the slave can simultaneouly handle,
								   * effectively locking out every other master that
								   * wishes to communicate with that same slave.
								   */




typedef enum {
	naf_ascii,
	naf_rtu,
	naf_tcp,
} node_addr_family_t;

typedef struct {
	const char* host;
	const char* service;
	int         close_on_silence;
} node_addr_tcp_t;


typedef union {
	/*node_addr_ascii_t ascii;
	node_addr_rtu_t   rtu;*/
	node_addr_tcp_t   tcp;
} node_addr_common_t;

typedef struct {
	node_addr_family_t  naf;
	node_addr_common_t  addr;
} node_addr_t;


  // Used by the Modbus client node
typedef struct {
	const char* location;
	node_addr_t	node_address;
	int		mb_nd;
	int		init_state; // store how far along the client's initialization has progressed
	u64		comm_period;
	int		prev_error; // error code of the last printed error message (0 when no error)
	HANDLE 	thread_id;  // thread handling all communication with this client
		SOCKET ClientSocket;
		//uint16_t Port;
		//uint16_t BufferSize;
		//uint16_t ThreadSleepingTime;
		bool Connected;
		bool Stopped;

} client_node_t;


// Used by the Modbus client plugin
typedef enum {
	req_input,
	req_output,
	no_request		/* just for tests to quickly disable a request */
} iotype_t;

#define REQ_BUF_SIZE 2000
typedef struct {
	const char* location;
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

	u16		plcv_buffer[REQ_BUF_SIZE];// buffer used to store located PLC variables

	u16		coms_buffer[REQ_BUF_SIZE];// buffer used to store data coming from / going to server

	float   analog_buffer[REQ_BUF_SIZE];// buffer for analog data
	u16 offset;
	u16 scale;
	CONST HANDLE coms_buf_mutex; // было: - pthread_mutex_t  --  mutex to access coms_buffer[]

} client_request_t;



#define RGISTR_SIZE 16
typedef struct{
	    u16     address;
	    u16	    num_bit[RGISTR_SIZE];

	} request_registers_t;
