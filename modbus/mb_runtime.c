/* File generated by Beremiz (PlugGenerate_C method of Modbus plugin) */

/*
 * Copyright (c) 2016 Mario de Sousa (msousa@fe.up.pt)
 *
 * This file is part of the Modbus library for Beremiz and matiec.
 *
 * This Modbus library is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
 * General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this Modbus library.  If not, see <http://www.gnu.org/licenses/>.
 *
 * This code is made available on the understanding that it will not be
 * used in safety-critical situations without a full and competent review.
 */
#define  _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <string.h>  /* required for memcpy() */

#include "MB_%(locstr)s.h"


#define MAX_MODBUS_ERROR_CODE 11
static const char *modbus_error_messages[MAX_MODBUS_ERROR_CODE+1] = {
    /* 0 */ "",                             /* un-used -> no error! */
    /* 1 */ "illegal/unsupported function",
    /* 2 */ "illegal data address",
    /* 3 */ "illegal data value",
    /* 4 */ "slave device failure",
    /* 5 */ "acknowledge -> slave intends to reply later",
    /* 6 */ "slave device busy",
    /* 7 */ "negative acknowledge",
    /* 8 */ "memory parity error",
    /* 9 */ "",                             /* undefined by Modbus */
    /* 10*/ "gateway path unavailable",
    /* 11*/ "gateway target device failed to respond"
};


#if defined(_MSC_VER) && (_MSC_VER >= 1400)
#define bswap_32 _byteswap_ulong
#define bswap_16 _byteswap_ushort
#else
#  define bswap_32 __builtin_bswap32
#endif

HANDLE hThreads[NUMBER_OF_CLIENT_NODES];

#define BIT_IN_WORD 16

#define THREADS_NUMBER 10
#define ITERATIONS_NUMBER 100
#define PAUSE 10 /* ms */

DWORD dwCounter = 0;

/*
 * Function to determine next transaction id.
 *
 * We use a library wide transaction id, which means that we
 * use a new transaction id no matter what slave to which we will
 * be sending the request...
 */
static inline u16 next_transaction_id(void) {
	static u16 next_id = 0;
	return next_id++;
}



/* The node descriptor table... */
/* NOTE: The node_table_ Must be initialized correctly here! */
static nd_table_t nd_table_ = { .node = NULL, .node_count = 0, .free_node_count = 0 };


static int configure_socket(int socket_id) {

	/* configure the socket */
	  /* Set it to be non-blocking. This is safe because we always use select() before reading from it!
	   * It is also required for the connect() call. The default timeout in the TCP stack is much too long
	   * (typically blocks for 128 s ??) when the connect does not succedd imediately!
	   */
	   //  if (fcntl(socket_id, F_SETFL, O_NONBLOCK) < 0) {
	   //#ifdef ERRMSG
	   //    perror("fcntl()");
	   //    fprintf(stderr, ERRMSG_HEAD "Error configuring socket 'non-blocking' option.\n");
	   //#endif
	   //    return -1;
	   //  }

		 /* configure the socket  set the TCP no delay flag. */

	{int bool_opt = 1;
	if (setsockopt(socket_id, IPPROTO_TCP, TCP_NODELAY, (const void*)&bool_opt, sizeof(bool_opt)) < 0)
	{
#ifdef ERRMSG
		perror("setsockopt()");
		fprintf(stderr, ERRMSG_HEAD "Error configuring socket 'TCP no delay' option.\n");
#endif
		return -1;
	}
	}

	/* set the IP low delay option. */
//  {int priority_opt = IPTOS_LOWDELAY;
//  if (setsockopt(socket_id, SOL_IP, IP_TOS, (const void *)&priority_opt, sizeof(priority_opt))  < 0) {
//#ifdef ERRMSG
//    perror("setsockopt()");
//    fprintf(stderr, ERRMSG_HEAD "Error configuring socket 'IP low delay' option.\n");
//#endif
//    return -1;
//  }
//  }

	return 0;
}


char* barray2hexstr(const unsigned char* data, size_t datalen) {

	size_t final_len = datalen * 2;
	char* chrs = (unsigned char*)malloc((final_len + 1) * sizeof(*chrs));
	unsigned int j = 0;
	for (j = 0; j < datalen; j++)
	{
		chrs[2 * j] = (data[j] >> 4) + 48;
		chrs[2 * j + 1] = (data[j] & 15) + 48;
		if (chrs[2 * j] > 57) chrs[2 * j] += 7;
		if (chrs[2 * j + 1] > 57) chrs[2 * j + 1] += 7;
	}
	chrs[2 * j] = '\0';
	return chrs;
}


/* Get a float from 4 bytes (Modbus) in inversed format (DCBA) */
float modbus_get_float_dcba(uint16_t* raw_words)
{
	float float_data;
	uint32_t i;

	i = ntohl(bswap_32((((uint32_t)raw_words[0]) << 16) + raw_words[1]));
	memcpy(&float_data, &i, sizeof(float));

	return float_data;
}

/* Set a float to 4 bytes for Modbus with byte and word swap conversion (DCBA) */
void modbus_set_float_dcba(float f, uint16_t* dest)
{
	uint32_t i;

	memcpy(&i, &f, sizeof(uint32_t));
	i = bswap_32(htonl(i));
	dest[0] = (uint16_t)(i >> 16);
	dest[1] = (uint16_t)i;
}

/* unpack analog registr  */
static inline void  __unpack_analog(client_request_t* raw_data, float* packed_data) {
	u8   bit_processed;
	u16  raw_d;
	float analog_data, scale, offset;

	raw_d = raw_data->plcv_buffer[0];

	scale = raw_data->scale;
	offset = raw_data->offset;

	if (scale > 1) {
		analog_data = raw_d / scale + offset;
	}
	else {
		analog_data = modbus_get_float_dcba(raw_data->plcv_buffer);
	}

	*packed_data = analog_data;
}

/* pack analog registr  */
static inline void  __pack_analog(client_request_t* raw_data, float* packed_data) {
	u16  raw_d;
	float analog_data ;
	analog_data = *packed_data;
	modbus_set_float_dcba(analog_data, raw_data->plcv_buffer);

}

/* pack bits from unpacked_data to packed_data */
static inline void  __pack_bits(request_registers_t* unpacked_data, u16* packed_data) {
	u8    bit_processed;
	u16 temp;

	for (bit_processed = 0; bit_processed < BIT_IN_WORD; bit_processed++) {
		temp = *packed_data;
		if (unpacked_data->num_bit[bit_processed]) {
			temp |= (1 << bit_processed); /*   set bit */
		}
		else {
			temp &= ~(1 << bit_processed); /* reset bit */
		}
		//fprintf(stderr, "Check paking bit  %%d ---\n", unpacked_data->num_bit[bit_processed]);
		*packed_data = temp;
	}
}
/* unpack bits from packed_data to unpacked_data */
static inline void  __unpack_bits(request_registers_t* unpacked_data, u16* packed_data) {
	u8    bit_processed;
	u16 temp;

	for (bit_processed = 0; bit_processed < BIT_IN_WORD; bit_processed++)
	{
		temp = *packed_data;

		unpacked_data->num_bit[bit_processed] = (temp >> bit_processed) & 1;
		//fprintf(stderr, "Check unpacking bit %%d ---\n", unpacked_data->num_bit[bit_processed]);
		*packed_data = temp;
	}
}


int init_custom_socket_new(client_node_t* CustomSocket)
{
	if (!CustomSocket) {
		printf("CustomSocket cannot be NULL.");
		return -1;
	}
	int iResult;
	struct addrinfo* result = NULL, * ptr = NULL, hints;

	WSADATA wsaData;
	iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != 0) {
		CustomSocket->Connected = false;
		CustomSocket->Stopped = true;
		printf("WSAStartup failed with error: %%d", iResult);
		return -1;
	}

	// Create a SOCKET for connecting to server
	CustomSocket->ClientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (CustomSocket->ClientSocket == INVALID_SOCKET)
	{
		printf("Listening Socket Creation failed");
		CustomSocket->Connected = false;
		CustomSocket->Stopped = true;


		WSACleanup();

		return -1;
	}

	CustomSocket->Stopped = false;
	return 0;
}


static int execute_mb_request_in(int request_id) {

	switch (client_requests[request_id].mb_function) {

	case  1: break;
	case  2: break;

	case  3: /* read holding registers */
		return read_output_words(
			client_requests[request_id].slave_id,
			client_requests[request_id].address,
			client_requests[request_id].count,
			&(client_requests[request_id].coms_buffer),
			(int)client_requests[request_id].count,

			client_nodes[client_requests[request_id].client_node_id].mb_nd,
			client_requests[request_id].retries,
			&(client_requests[request_id].error_code),
			//&(client_requests[request_id].resp_timeout),
			&(client_requests[request_id].coms_buf_mutex),
			&client_nodes[client_requests[request_id].client_node_id],
			&(client_requests[request_id].plcv_buffer)


		);

	case  4:break;

	case  5:break;

	case  6:  /* write single register */
		return write_output_word(
			client_requests[request_id].slave_id,
			client_requests[request_id].address,
			&(client_requests[request_id].coms_buffer) ,

			client_nodes[client_requests[request_id].client_node_id].mb_nd,
			client_requests[request_id].retries,
			&(client_requests[request_id].error_code),
			//&(client_requests[request_id].resp_timeout),
			&(client_requests[request_id].coms_buf_mutex),
			&client_nodes[client_requests[request_id].client_node_id],
			&(client_requests[request_id].plcv_buffer)
		);

	case  7: break; /* function not yet supported */
	case  8: break; /* function not yet supported */
	case  9: break; /* function not yet supported */
	case 10: break; /* function not yet supported */
	case 11: break; /* function not yet supported */
	case 12: break; /* function not yet supported */
	case 13: break; /* function not yet supported */
	case 14: break; /* function not yet supported */

	case 15: break;
	case 16: break;


//	case 16: /* write multiple registers */
//		return write_output_words(
//			client_requests[request_id].slave_id,
//			client_requests[request_id].address,
//			client_requests[request_id].count,
//			client_requests[request_id].coms_buffer,
//
//			client_nodes[client_requests[request_id].client_node_id].mb_nd,
//			client_requests[request_id].retries,
//			&(client_requests[request_id].error_code),
//			//&(client_requests[request_id].resp_timeout),
//			&(client_requests[request_id].coms_buf_mutex),
//			& client_nodes[client_requests[request_id].client_node_id],
//			& (client_requests[request_id].plcv_buffer)
//
//		);


	default: break;  /* should never occur, if file generation is correct */
	}

	fprintf(stderr, "Modbus plugin: Modbus function %%d not supported\n", request_id); /* should never occur, if file generation is correct */
	return -1;
}


static void __print_structure(request_registers_t *unpacked_data, int request_id ){
u8    bit_processed, allbits;
    for(bit_processed = 0; bit_processed < BIT_IN_WORD; bit_processed++)
  {
    fprintf(stderr, "bits in structure %%d ---\n", unpacked_data->num_bit[bit_processed]);
  }
 //fprintf(stderr, "--2 bits  structure %%d in request %%d  ---\n", unpacked_data->num_bit[1], request_id);

}

static int __execute_mb_request(int request_id){
int ret = 0;
   // fprintf(stderr, "#_____________________________# \n" );
    //fprintf(stderr, "request id %%d  \n", request_id);
   // fprintf(stderr, "request address %%d  \n", client_requests[request_id].address);
   // fprintf(stderr, "request buffer %%d  \n", client_requests[request_id].plcv_buffer[0]);

//    if (client_requests[request_id].mb_function == 6 ) {
//        __pack_bits(&request_registers[request_id] ,  &client_requests[request_id].plcv_buffer[0]);
//    }
    if (client_requests[request_id].mb_function == 6) // || client_requests[request_id].mb_function == 16)
	{
		__pack_bits(&request_registers[request_id], &client_requests[request_id].plcv_buffer[0]);
		//__pack_bits(&request_registers[request_id], &client_requests[request_id].coms_buffer[0]);
	}

	if (client_requests[request_id].mb_function == 16 && client_requests[request_id].count > 1)
	{
		__pack_analog(&client_requests[request_id], &client_requests[request_id].analog_buffer[0]);
	}

    ret = execute_mb_request_in(request_id);

    // unpack analogs
	if (client_requests[request_id].mb_function == 3 && client_requests[request_id].count > 1)
		 __unpack_analog(&client_requests[request_id], &client_requests[request_id].analog_buffer[0]);

    // получаем биты - сигналы
    	if (client_requests[request_id].mb_function == 3 && client_requests[request_id].count == 1)	{
		__unpack_bits(&request_registers[request_id], &client_requests[request_id].plcv_buffer[0]);
	}
//    if(client_requests[request_id].mb_function == 3)
//    {
//        __unpack_bits(&request_registers[request_id] ,  &client_requests[request_id].plcv_buffer[0]);
//    }

	if (client_requests[request_id].mb_function == 3 && client_requests[request_id].count == 1)
			__print_structure(&request_registers[request_id], request_id);

   // __print_structure(&request_registers[request_id], request_id);
  //  fprintf(stderr, "#_____________________________# \n" );

	 return ret;
}


#define timespec_add(ts, sec, nsec) {		\
	ts.tv_sec  +=  sec;			\
	ts.tv_nsec += nsec;			\
	if (ts.tv_nsec >= 1000000000) {		\
		ts.tv_sec  ++;			\
		ts.tv_nsec -= 1000000000;	\
	}					\
}

int accept_and_stream_custom_socket2(void* _index)
{
	int client_node_id = (char*)_index - (char*)NULL; // Use pointer arithmetic (more portable than cast)


	do {

			u64 period_sec = client_nodes[client_node_id].comm_period / 1000;          /* comm_period is in ms */
			int period_nsec = (client_nodes[client_node_id].comm_period %% 1000) * 1000000; /* comm_period is in ms */


	// loop the communication with the client
	while (1) {

		int req;
		for (req = 0; req < NUMBER_OF_CLIENT_REQTS; req++) {
			/*just do the requests belonging to the client */
			if (client_requests[req].client_node_id != client_node_id)
				continue;
			int res_tmp = __execute_mb_request(req);
			switch (res_tmp) {
			  case PORT_FAILURE: {
				if (res_tmp != client_nodes[client_node_id].prev_error)
					fprintf(stderr, "Modbus plugin: Error connecting Modbus client %%s to remote server.\n", client_nodes[client_node_id].location);
				client_nodes[client_node_id].prev_error = res_tmp;
				break;
			  }
			  case INVALID_FRAME: {
				if ((res_tmp != client_requests[req].prev_error) && (0 == client_nodes[client_node_id].prev_error))
					fprintf(stderr, "Modbus plugin: Modbus client request configured at location %%s was unsuccesful. Server/slave returned an invalid/corrupted frame.\n", client_requests[req].location);
				client_requests[req].prev_error = res_tmp;
				break;
			  }
			  case TIMEOUT: {
				if ((res_tmp != client_requests[req].prev_error) && (0 == client_nodes[client_node_id].prev_error))
					fprintf(stderr, "Modbus plugin: Modbus client request configured at location %%s timed out waiting for reply from server.\n", client_requests[req].location);
				client_requests[req].prev_error = res_tmp;
				break;
			  }
			  case MODBUS_ERROR: {
				if (client_requests[req].prev_error != client_requests[req].error_code) {
					fprintf(stderr, "Modbus plugin: Modbus client request configured at location %%s was unsuccesful. Server/slave returned error code 0x%%2x", client_requests[req].location, client_requests[req].error_code);

				}
				client_requests[req].prev_error = client_requests[req].error_code;
				break;
			  }
			  default: {
				if ((res_tmp >= 0) && (client_nodes[client_node_id].prev_error != 0)) {
					fprintf(stderr, "Modbus plugin: Modbus client %%s has reconnected to server/slave.\n", client_nodes[client_node_id].location);
				}
				if ((res_tmp >= 0) && (client_requests[req].prev_error != 0)) {
					fprintf(stderr, "Modbus plugin: Modbus client request configured at location %%s has succesfully resumed comunication.\n", client_requests[req].location);
				}
				client_nodes[client_node_id].prev_error = 0;
				client_requests[req].prev_error = 0;
				break;
			  }
			}
		}
		 Sleep(200);

		 if (client_nodes[client_node_id].Stopped )
			{
				return 0;
			}
	}

	// humour the compiler.
	return NULL;



	} while (1); // while (!CustomSocket->Stopped);
}

int clean_custom_socket(struct custom_socket* CustomSocket) {
	if (CustomSocket) {
		CustomSocket->Stopped = true;
		CustomSocket->Connected = false;
		// cleanup
		closesocket(CustomSocket->ClientSocket);
		WSACleanup();
	}
#if defined _WIN64 || defined _WIN32
	WSACleanup();
#endif
}




//static void *__mb_client_thread(void *_index)  {
//
//
//	// humour the compiler.
//	return NULL;
//}

DWORD WINAPI run_accept_and_stream_custom_socket2(CONST LPVOID lpParam) {

	struct client_request_t* client_requests = lpParam;
	int tt = accept_and_stream_custom_socket2(client_requests);

}


int __cleanup_%(locstr)s ();
int __init_%(locstr)s (int argc, char **argv){

	TCHAR szMessage[256];
	DWORD dwTemp, i;

	//CONST HANDLE hStdOut = GetStdHandle(STD_OUTPUT_HANDLE);
	//CONST HANDLE hMutex = CreateMutex(NULL, FALSE, NULL);



//	struct timeval st, et;
//	getTick(&st);



	//struct custom_socket CustomSocket = { NULL, NULL, 0,0,0 };
	uint16_t Port = 501;

	// Setup the TCP listening socket
	SetUpSocket(client_nodes[0].node_address); // 172.16.13.142

	uint16_t deelay_ = client_nodes[0].comm_period;
	int count = 0;


	char* bufTxt;
	uint16_t tab_reg[2];

	//int mbRead = 8000;
	//int mbWrite = 8400;
	int count_registers = 1;
	uint16_t  reg = 0;
	u16  data = 5;
	int request_id = 0;


	client_requests[1].coms_buffer[0] = 0;

	Sleep(deelay_);

	int index;

	for (index = 0; index < NUMBER_OF_CLIENT_NODES; index++)
	{
		client_nodes[index].mb_nd = -1;
		int initResult = init_custom_socket_new(&client_nodes[index]);
		if (initResult != 0) {
			fprintf(stderr,   "Failed to initialise socket.\n");
		}
		else
		{
			client_nodes[index].mb_nd = 1;
		}
	}

	for (index = 0; index < NUMBER_OF_CLIENT_NODES; index++)
	{

		client_nodes[index].init_state = 1;
		{
			int res = 0;

			hThreads[index] = CreateThread(NULL, 0, &run_accept_and_stream_custom_socket2, index, 0, &(client_nodes[index].thread_id));

			Sleep(500);
			if (res != 0) {
				printf("Modbus plugin: Error starting modbus client thread for node %%s\n", client_nodes[index].location);
				return -1;
			}
		}
		client_nodes[index].init_state = 2; // we have created the node and a thread
	}

//	do {
//		bufTxt = barray2hexstr(&client_requests[0].plcv_buffer[0], 2);
//		printf(bufTxt);
//		printf("\n");
//
//
//		count++;
//		client_requests[1].coms_buffer[0] = count;
//
//		bufTxt = barray2hexstr(&client_requests[1].coms_buffer[0], 2);
//		printf(bufTxt);
//		printf("\n");
//		//printf(&client_requests[0].plcv_buffer[0] ) ;
//		Sleep(deelay_);
//
//
//		for (index = 0; index < NUMBER_OF_CLIENT_NODES; index++)
//		{
//
//			if (client_nodes[index].Connected == false)
//			{
//				int initResult = init_custom_socket_new(&client_nodes[index]);
//				if (initResult != 0) {
//					//Error(hStdOut, TEXT("Failed to initialise socket.\r\n"));
//					fprintf(stderr,   "Failed to initialise socket.\n");
//				}
//			}
//		}
//
//	} while (1);

//	CloseHandle(hThreads[0]);
//	CloseHandle(hMutex);
//	ExitProcess(0);

	return 0;

error_exit:
	__cleanup_%(locstr)s ();
	return -1;
}





void __publish_%(locstr)s (){
	int index;

//	for (index=0; index < NUMBER_OF_CLIENT_REQTS; index ++){
//		/*just do the output requests */
//		if (client_requests[index].req_type == req_output){
//			if(pthread_mutex_trylock(&(client_requests[index].coms_buf_mutex)) == 0){
//                // copy from plcv_buffer to coms_buffer
//                memcpy((void *)client_requests[index].coms_buffer /* destination */,
//                       (void *)client_requests[index].plcv_buffer /* source */,
//                       REQ_BUF_SIZE * sizeof(u16) /* size in bytes */);
//                pthread_mutex_unlock(&(client_requests[index].coms_buf_mutex));
//            }
//		}
//	}
}


void __retrieve_%(locstr)s (){
	int index;

//	for (index=0; index < NUMBER_OF_CLIENT_REQTS; index ++){
//		/*just do the input requests */
//		if (client_requests[index].req_type == req_input){
//			if(pthread_mutex_trylock(&(client_requests[index].coms_buf_mutex)) == 0){
//                // copy from coms_buffer to plcv_buffer
//                memcpy((void *)client_requests[index].plcv_buffer /* destination */,
//                       (void *)client_requests[index].coms_buffer /* source */,
//                       REQ_BUF_SIZE * sizeof(u16) /* size in bytes */);
//                pthread_mutex_unlock(&(client_requests[index].coms_buf_mutex));
//            }
//		}
//	}

}


int __cleanup_%(locstr)s (){
		int index, close;
	int res = 0;

	/* kill thread and close connections of each modbus client node */
	for (index=0; index < NUMBER_OF_CLIENT_NODES; index++) {
		close = 0;
		if (client_nodes[index].init_state >= 2) {
			// thread was launched, so we try to cancel it!
			close = CloseHandle(hThreads[index]);
			if (close == false)
				fprintf(stderr, "Modbus plugin: Error closing thread for modbus client \n" );
            client_nodes[index].Stopped = true;
		}
		res |= close;

		close = 0;
//		if (client_nodes[index].init_state >= 1) {
//			// modbus client node was created, so we try to close it!
//			close = modbus_tcp_close(client_nodes[index].mb_nd);
//			if (close < 0){
//				fprintf(stderr, "Modbus plugin: Error closing modbus client node %%s\n", client_nodes[index].location);
//				// We try to shut down as much as possible, so we do not return noW!
//			}
//			client_nodes[index].mb_nd = -1;
//		}
		res |= close;
		client_nodes[index].init_state = 0;
	}

	/* destroy the mutex of each client request */
//	for (index=0; index < NUMBER_OF_CLIENT_REQTS; index ++) {
//		if (CloseHandle(&(client_requests[index].coms_buf_mutex))) {
//			fprintf(stderr, "Modbus plugin: Error destroying request for modbus client node %%s\n", client_nodes[client_requests[index].client_node_id].location);
//			// We try to shut down as much as possible, so we do not return noW!
//			res |= -1;
//		}
//	}

	/* modbus library close */

	////fprintf(stderr, "Shutting down modbus library...\n");
//    fprintf(stderr, "Shutting down modbus library...\n");
//	if (mb_slave_and_master_done()<0) {
//		fprintf(stderr, "Modbus plugin: Error shutting down modbus library\n");
//		res |= -1;
//	}

	return res;
}