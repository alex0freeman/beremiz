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


#include <stdio.h>
#include <string.h>  /* required for memcpy() */
#include "mb_slave_and_master.h"
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



/* pack bits from unpacked_data to packed_data */
static inline void  __pack_bits(request_registers_t *unpacked_data, u16  *packed_data) {
  u8    bit_processed, allbits;
  u16 temp, byte;
  allbits = 15;

  for(bit_processed = 0; bit_processed < allbits; bit_processed++)
  {
     temp = *packed_data;
      if(unpacked_data->num_bit[bit_processed]){
       temp |=  (1 << bit_processed); /*   set bit */
      }
      else{
        temp &= ~(1 << bit_processed); /* reset bit */
      }

      fprintf(stderr, "Check paking bit  %%d ---\n", unpacked_data->num_bit[bit_processed]);
      *packed_data =  temp;
    }
}


/* unpack bits from packed_data to unpacked_data */
static inline void  __unpack_bits(request_registers_t *unpacked_data, u16  *packed_data)
{
  u8    bit_processed, allbits;
  u16 temp, byte;
  allbits = 15;

  for(bit_processed = 0; bit_processed < allbits; bit_processed++)
  {
    temp = *packed_data;
    //for(bit = 0x01; (bit & 0xff) && (coils_processed < bit_count); bit <<= 1, coils_processed++) {

    unpacked_data->num_bit[bit_processed] = (temp  >> bit_processed) & 1;
    fprintf(stderr, "Check unpacking bit %%d ---\n", unpacked_data->num_bit[bit_processed]);
     *packed_data =  temp;
  }
}

/* Execute a modbus client transaction/request */
static int __execute_mb_request_in(int request_id){

   // __pack_bits(&request_registers[request_id] ,  &client_requests[request_id].plcv_buffer[0]);


	switch (client_requests[request_id].mb_function){

	case  1: /* read coils */
		return read_output_bits(client_requests[request_id].slave_id,
					client_requests[request_id].address,
					client_requests[request_id].count,
					client_requests[request_id].coms_buffer,
					(int) client_requests[request_id].count,
					client_nodes[client_requests[request_id].client_node_id].mb_nd,
					client_requests[request_id].retries,
					&(client_requests[request_id].error_code),
					&(client_requests[request_id].resp_timeout),
					&(client_requests[request_id].coms_buf_mutex));

	case  2: /* read discrete inputs */
		return read_input_bits( client_requests[request_id].slave_id,
					client_requests[request_id].address,
					client_requests[request_id].count,
					client_requests[request_id].coms_buffer,
					(int) client_requests[request_id].count,
					client_nodes[client_requests[request_id].client_node_id].mb_nd,
					client_requests[request_id].retries,
					&(client_requests[request_id].error_code),
					&(client_requests[request_id].resp_timeout),
					&(client_requests[request_id].coms_buf_mutex));

	case  3: /* read holding registers */
		return read_output_words(client_requests[request_id].slave_id,
								client_requests[request_id].address,
								client_requests[request_id].count,
								client_requests[request_id].coms_buffer,
								(int) client_requests[request_id].count,

								client_nodes[client_requests[request_id].client_node_id].mb_nd,
								client_requests[request_id].retries,
								&(client_requests[request_id].error_code),
								&(client_requests[request_id].resp_timeout),
								&(client_requests[request_id].coms_buf_mutex));

	case  4: /* read input registers */
		return read_input_words(client_requests[request_id].slave_id,
					client_requests[request_id].address,
					client_requests[request_id].count,
					client_requests[request_id].coms_buffer,
					(int) client_requests[request_id].count,
					client_nodes[client_requests[request_id].client_node_id].mb_nd,
					client_requests[request_id].retries,
					&(client_requests[request_id].error_code),
					&(client_requests[request_id].resp_timeout),
					&(client_requests[request_id].coms_buf_mutex));

	case  5: /* write single coil */
		return write_output_bit(client_requests[request_id].slave_id,
					client_requests[request_id].address,
					client_requests[request_id].coms_buffer[0],
					client_nodes[client_requests[request_id].client_node_id].mb_nd,
					client_requests[request_id].retries,
					&(client_requests[request_id].error_code),
					&(client_requests[request_id].resp_timeout),
					&(client_requests[request_id].coms_buf_mutex));

	case  6: /* write single register */
		return write_output_word(client_requests[request_id].slave_id,
								client_requests[request_id].address,
								client_requests[request_id].coms_buffer[0],

								client_nodes[client_requests[request_id].client_node_id].mb_nd,
								client_requests[request_id].retries,
								&(client_requests[request_id].error_code),
								&(client_requests[request_id].resp_timeout),
								&(client_requests[request_id].coms_buf_mutex));

	case  7: break; /* function not yet supported */
	case  8: break; /* function not yet supported */
	case  9: break; /* function not yet supported */
	case 10: break; /* function not yet supported */
	case 11: break; /* function not yet supported */
	case 12: break; /* function not yet supported */
	case 13: break; /* function not yet supported */
	case 14: break; /* function not yet supported */

	case 15: /* write multiple coils */
		return write_output_bits(client_requests[request_id].slave_id,
					 client_requests[request_id].address,
					 client_requests[request_id].count,
					 client_requests[request_id].coms_buffer,
					 client_nodes[client_requests[request_id].client_node_id].mb_nd,
					 client_requests[request_id].retries,
					 &(client_requests[request_id].error_code),
					 &(client_requests[request_id].resp_timeout),
					 &(client_requests[request_id].coms_buf_mutex));

	case 16: /* write multiple registers */
		return write_output_words(client_requests[request_id].slave_id,
								client_requests[request_id].address,
								client_requests[request_id].count,
								client_requests[request_id].coms_buffer,

								client_nodes[client_requests[request_id].client_node_id].mb_nd,
								client_requests[request_id].retries,
								&(client_requests[request_id].error_code),
								&(client_requests[request_id].resp_timeout),
								&(client_requests[request_id].coms_buf_mutex));

	default: break;  /* should never occur, if file generation is correct */
	}




	fprintf(stderr, "Modbus plugin: Modbus function %%d not supported\n", request_id); /* should never occur, if file generation is correct */
	return -1;
}

static int __execute_mb_request(int request_id){
int ret = 0;

    fprintf(stderr, "request id %%d  \n", request_id);
    fprintf(stderr, "request address %%d  \n", client_requests[request_id].address);
    fprintf(stderr, "request buffer %%d  \n", client_requests[request_id].plcv_buffer[0]);

     if(client_requests[request_id].mb_function == 16)
    {
        __pack_bits(&request_registers[request_id] ,  &client_requests[request_id].plcv_buffer[0]);
    }

    ret = __execute_mb_request_in(request_id);

    if(client_requests[request_id].mb_function == 3)
    {
        __unpack_bits(&request_registers[request_id] ,  &client_requests[request_id].plcv_buffer[0]);
    }

	 return ret;
}

//
///* pack bits from unpacked_data to packed_data */
//static inline int __pack_bits(u16 *unpacked_data, u16 start_addr, u16 bit_count,  u8  *packed_data) {
//  u8 bit;
//  u16 byte, coils_processed;
//
//  if ((0 == bit_count) || (65535-start_addr < bit_count-1))
//    return -ERR_ILLEGAL_DATA_ADDRESS; /* ERR_ILLEGAL_DATA_ADDRESS defined in mb_util.h */
//
//  for( byte = 0, coils_processed = 0; coils_processed < bit_count; byte++) {
//    packed_data[byte] = 0;
//    for( bit = 0x01; (bit & 0xFF) && (coils_processed < bit_count); bit <<= 1, coils_processed++ ) {
//      if(unpacked_data[start_addr + coils_processed])
//            packed_data[byte] |=  bit; /*   set bit */
//      else  packed_data[byte] &= ~bit; /* reset bit */
//    }
//  }
//
//  //__savelogs_("pack bits");
//  return 0;
//}
//
//
///* unpack bits from packed_data to unpacked_data */
//static inline int __unpack_bits(u16 *unpacked_data, u16 start_addr, u16 bit_count,  u8  *packed_data) {
//  u8  temp, bit;
//  u16 byte, coils_processed;
//
//  if ((0 == bit_count) || (65535-start_addr < bit_count-1))
//    return -ERR_ILLEGAL_DATA_ADDRESS; /* ERR_ILLEGAL_DATA_ADDRESS defined in mb_util.h */
//
//  for(byte = 0, coils_processed = 0; coils_processed < bit_count; byte++) {
//    temp = packed_data[byte] ;
//    for(bit = 0x01; (bit & 0xff) && (coils_processed < bit_count); bit <<= 1, coils_processed++) {
//      unpacked_data[start_addr + coils_processed] = (temp & bit)?1:0;
//    }
//  }
//
//   //__savelogs_("UNpack bits");
//  return 0;
//}
//
//
//static int __read_inbits   (void *mem_map, u16 start_addr, u16 bit_count, u8  *data_bytes)
//  {return   __pack_bits(((server_mem_t *)mem_map)->ro_bits, start_addr, bit_count, data_bytes);}
//static int __read_outbits  (void *mem_map, u16 start_addr, u16 bit_count, u8  *data_bytes)
//  {return   __pack_bits(((server_mem_t *)mem_map)->rw_bits, start_addr, bit_count, data_bytes);}
//static int __write_outbits (void *mem_map, u16 start_addr, u16 bit_count, u8  *data_bytes)
//  {return __unpack_bits(((server_mem_t *)mem_map)->rw_bits, start_addr, bit_count, data_bytes); }
//
//
//
//static int __read_inwords  (void *mem_map, u16 start_addr, u16 word_count, u16 *data_words) {
//
//  if ((start_addr + word_count) > MEM_AREA_SIZE)
//    return -ERR_ILLEGAL_DATA_ADDRESS; /* ERR_ILLEGAL_DATA_ADDRESS defined in mb_util.h */
//
//  /* use memcpy() because loop with pointers (u16 *) caused alignment problems */
//  memcpy(/* dest */ (void *)data_words,
//         /* src  */ (void *)&(((server_mem_t *)mem_map)->ro_words[start_addr]),
//         /* size */ word_count * 2);
//
// // __savelogs_("read input word");
//  return 0;
//}
//
//
//
//static int __read_outwords (void *mem_map, u16 start_addr, u16 word_count, u16 *data_words) {
//
//  if ((start_addr + word_count) > MEM_AREA_SIZE)
//    return -ERR_ILLEGAL_DATA_ADDRESS; /* ERR_ILLEGAL_DATA_ADDRESS defined in mb_util.h */
//
//  /* use memcpy() because loop with pointers (u16 *) caused alignment problems */
//  memcpy(/* dest */ (void *)data_words,
//         /* src  */ (void *)&(((server_mem_t *)mem_map)->rw_words[start_addr]),
//         /* size */ word_count * 2);
//
//  //__savelogs_("read out word");
//  return 0;
//}
//
//
//
//
//static int __write_outwords(void *mem_map, u16 start_addr, u16 word_count, u16 *data_words) {
//
//  if ((start_addr + word_count) > MEM_AREA_SIZE)
//    return -ERR_ILLEGAL_DATA_ADDRESS; /* ERR_ILLEGAL_DATA_ADDRESS defined in mb_util.h */
//
//  /* WARNING: The data returned in the data_words[] array is not guaranteed to be 16 bit aligned.
//   *           It is not therefore safe to cast it to an u16 data type.
//   *           The following code cannot be used. memcpy() is used instead.
//   */
//  /*
//  for (count = 0; count < word_count ; count++)
//    ((server_mem_t *)mem_map)->rw_words[count + start_addr] = data_words[count];
//  */
//  memcpy(/* dest */ (void *)&(((server_mem_t *)mem_map)->rw_words[start_addr]),
//         /* src  */ (void *)data_words,
//         /* size */ word_count * 2);
//
//  //__savelogs_("save out word");
//  return 0;
//}




#include <pthread.h>

//static void *__mb_server_thread(void *_server_node)  {
//	server_node_t *server_node = _server_node;
//	mb_slave_callback_t callbacks = {
//			&__read_inbits,
//			&__read_outbits,
//			&__write_outbits,
//			&__read_inwords,
//			&__read_outwords,
//			&__write_outwords,
//			(void *)&(server_node->mem_area)
//			};
//
//	// Enable thread cancellation. Enabled is default, but set it anyway to be safe.
//	pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, NULL);
//
//	// mb_slave_run() should never return!
//	mb_slave_run(server_node->mb_nd /* nd */, callbacks, server_node->slave_id);
//	fprintf(stderr, "Modbus plugin: Modbus server for node %%s died unexpectedly!\n", server_node->location); /* should never occur */
//	return NULL;
//}
//

#define timespec_add(ts, sec, nsec) {		\
	ts.tv_sec  +=  sec;			\
	ts.tv_nsec += nsec;			\
	if (ts.tv_nsec >= 1000000000) {		\
		ts.tv_sec  ++;			\
		ts.tv_nsec -= 1000000000;	\
	}					\
}


static void *__mb_client_thread(void *_index)  {
	int client_node_id = (char *)_index - (char *)NULL; // Use pointer arithmetic (more portable than cast)
	struct timespec next_cycle;
	int period_sec  =  client_nodes[client_node_id].comm_period / 1000;          /* comm_period is in ms */
	int period_nsec = (client_nodes[client_node_id].comm_period %%1000)*1000000; /* comm_period is in ms */

	// Enable thread cancellation. Enabled is default, but set it anyway to be safe.
	pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, NULL);

	// get the current time
	clock_gettime(CLOCK_MONOTONIC, &next_cycle);

	// loop the communication with the client
	while (1) {
		/*
		struct timespec cur_time;
		clock_gettime(CLOCK_MONOTONIC, &cur_time);
		fprintf(stderr, "Modbus client thread - new cycle (%%ld:%%ld)!\n", cur_time.tv_sec, cur_time.tv_nsec);
		*/
		int req;
		for (req=0; req < NUMBER_OF_CLIENT_REQTS; req ++){
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
					if (client_requests[req].error_code <= MAX_MODBUS_ERROR_CODE ) {
						fprintf(stderr, "(%%s)", modbus_error_messages[client_requests[req].error_code]);
						fprintf(stderr, ".\n");
					}
				}
				client_requests[req].prev_error = client_requests[req].error_code;
				break;
			  }
			  default: {
				if ((res_tmp >= 0) && (client_nodes[client_node_id].prev_error != 0)) {
					fprintf(stderr, "Modbus plugin: Modbus client %%s has reconnected to server/slave.\n", client_nodes[client_node_id].location);
				}
				if ((res_tmp >= 0) && (client_requests[req]        .prev_error != 0)) {
					fprintf(stderr, "Modbus plugin: Modbus client request configured at location %%s has succesfully resumed comunication.\n", client_requests[req].location);
				}
				client_nodes[client_node_id].prev_error = 0;
				client_requests[req]        .prev_error = 0;
				break;
			  }
			}
		}
		// Determine absolute time instant for starting the next cycle
		struct timespec prev_cycle, now;
		prev_cycle = next_cycle;
		timespec_add(next_cycle, period_sec, period_nsec);
		/* NOTE A:
		 * When we have difficulty communicating with remote client and/or server, then the communications get delayed and we will
		 * fall behind in the period. This means that when communication is re-established we may end up running this loop continuously
		 * for some time until we catch up.
		 * This is undesirable, so we detect it by making sure the next_cycle will start in the future.
		 * When this happens we will switch from a purely periodic task _activation_ sequence, to a fixed task suspension interval.
		 *
		 * NOTE B:
		 * It probably does not make sense to check for overflow of timer - so we don't do it for now!
		 * Even in 32 bit systems this will take at least 68 years since the computer booted
		 * (remember, we are using CLOCK_MONOTONIC, which should start counting from 0
		 * every time the system boots). On 64 bit systems, it will take over
		 * 10^11 years to overflow.
		 */
		clock_gettime(CLOCK_MONOTONIC, &now);
		if (  ((now.tv_sec > next_cycle.tv_sec) || ((now.tv_sec == next_cycle.tv_sec) && (now.tv_nsec > next_cycle.tv_nsec)))
		   /* We are falling behind. See NOTE A above */
		   || (next_cycle.tv_sec < prev_cycle.tv_sec)
		   /* Timer overflow. See NOTE B above */
		   ) {
			next_cycle = now;
			timespec_add(next_cycle, period_sec, period_nsec);
		}

		clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next_cycle, NULL);
	}

	// humour the compiler.
	return NULL;
}


int __cleanup_%(locstr)s ();
int __init_%(locstr)s (int argc, char **argv){



	int index;

	for (index=0; index < NUMBER_OF_CLIENT_NODES;index++)
		client_nodes[index].mb_nd = -1;
	for (index=0; index < NUMBER_OF_SERVER_NODES;index++)
		// mb_nd with negative numbers indicate how far it has been initialized (or not)
		//   -2  --> no modbus node created;  no thread  created
		//   -1  -->    modbus node created!; no thread  created
		//  >=0  -->    modbus node created!;    thread  created!
		server_nodes[index].mb_nd = -2;

	/* modbus library init */
	/* Note that TOTAL_xxxNODE_COUNT are the nodes required by _ALL_ the instances of the modbus
	 *  extension currently in the user's project. This file (MB_xx.c) is handling only one instance,
	 *  but must initialize the library for all instances. Only the first call to mb_slave_and_master_init()
	 *  will result in memory being allocated. All subsequent calls (by other MB_xx,c files) will be ignored
	 *  by the mb_slave_and_master_init() function, as long as they are called with the same arguments.
	 */
	if (mb_slave_and_master_init(TOTAL_TCPNODE_COUNT, TOTAL_RTUNODE_COUNT, TOTAL_ASCNODE_COUNT) <0) {
		fprintf(stderr, "Modbus plugin: Error starting modbus library\n");
		// return immediately. Do NOT goto error_exit, as we did not get to
		//  start the modbus library!
		return -1;
	}

	/* init the mutex for each client request */
	/* Must be done _before_ launching the client threads!! */
	for (index=0; index < NUMBER_OF_CLIENT_REQTS; index ++){
		if (pthread_mutex_init(&(client_requests[index].coms_buf_mutex), NULL)) {
			fprintf(stderr, "Modbus plugin: Error initializing request for modbus client node %%s\n", client_nodes[client_requests[index].client_node_id].location);
			goto error_exit;
		}
	}

	/* init each client connection to remote modbus server, and launch thread */
	/* NOTE: All client_nodes[].init_state are initialised to 0 in the code
	 *       generated by the modbus plugin
	 */
	for (index=0; index < NUMBER_OF_CLIENT_NODES;index++){
		/* establish client connection */
		client_nodes[index].mb_nd = mb_master_connect (client_nodes[index].node_address);
		if (client_nodes[index].mb_nd < 0){
			fprintf(stderr, "Modbus plugin: Error creating modbus client node %%s\n", client_nodes[index].location);
			goto error_exit;
		}
		client_nodes[index].init_state = 1; // we have created the node

		/* launch a thread to handle this client node */
		{
			int res = 0;
			pthread_attr_t attr;
			res |= pthread_attr_init(&attr);
			res |= pthread_create(&(client_nodes[index].thread_id), &attr, &__mb_client_thread, (void *)((char *)NULL + index));
			if (res !=  0) {
				fprintf(stderr, "Modbus plugin: Error starting modbus client thread for node %%s\n", client_nodes[index].location);
				goto error_exit;
			}
		}
		client_nodes[index].init_state = 2; // we have created the node and a thread
	}

	/* init each local server */
	/* NOTE: All server_nodes[].init_state are initialised to 0 in the code
	 *       generated by the modbus plugin
	 */
//	for (index=0; index < NUMBER_OF_SERVER_NODES;index++){
//		/* create the modbus server */
//		server_nodes[index].mb_nd = mb_slave_new (server_nodes[index].node_address);
//		if (server_nodes[index].mb_nd < 0){
//			fprintf(stderr, "Modbus plugin: Error creating modbus server node %%s\n", server_nodes[index].location);
//			goto error_exit;
//		}
//		server_nodes[index].init_state = 1; // we have created the node
//
//		/* launch a thread to handle this server node */
//		{
//			int res = 0;
//			pthread_attr_t attr;
//			res |= pthread_attr_init(&attr);
//			res |= pthread_create(&(server_nodes[index].thread_id), &attr, &__mb_server_thread, (void *)&(server_nodes[index]));
//			if (res !=  0) {
//				fprintf(stderr, "Modbus plugin: Error starting modbus server thread for node %%s\n", server_nodes[index].location);
//				goto error_exit;
//			}
//		}
//		server_nodes[index].init_state = 2; // we have created the node and thread
//	}

	return 0;

error_exit:
	__cleanup_%(locstr)s ();
	return -1;
}





void __publish_%(locstr)s (){
	int index;

	for (index=0; index < NUMBER_OF_CLIENT_REQTS; index ++){
		/*just do the output requests */
		if (client_requests[index].req_type == req_output){
			if(pthread_mutex_trylock(&(client_requests[index].coms_buf_mutex)) == 0){
                // copy from plcv_buffer to coms_buffer
                memcpy((void *)client_requests[index].coms_buffer /* destination */,
                       (void *)client_requests[index].plcv_buffer /* source */,
                       REQ_BUF_SIZE * sizeof(u16) /* size in bytes */);
                pthread_mutex_unlock(&(client_requests[index].coms_buf_mutex));
            }
		}
	}
}





void __retrieve_%(locstr)s (){
	int index;

	for (index=0; index < NUMBER_OF_CLIENT_REQTS; index ++){
		/*just do the input requests */
		if (client_requests[index].req_type == req_input){
			if(pthread_mutex_trylock(&(client_requests[index].coms_buf_mutex)) == 0){
                // copy from coms_buffer to plcv_buffer
                memcpy((void *)client_requests[index].plcv_buffer /* destination */,
                       (void *)client_requests[index].coms_buffer /* source */,
                       REQ_BUF_SIZE * sizeof(u16) /* size in bytes */);
                pthread_mutex_unlock(&(client_requests[index].coms_buf_mutex));
            }
		}
	}
}





int __cleanup_%(locstr)s (){
	int index, close;
	int res = 0;

	/* kill thread and close connections of each modbus client node */
	for (index=0; index < NUMBER_OF_CLIENT_NODES; index++) {
		close = 0;
		if (client_nodes[index].init_state >= 2) {
			// thread was launched, so we try to cancel it!
			close  = pthread_cancel(client_nodes[index].thread_id);
			close |= pthread_join  (client_nodes[index].thread_id, NULL);
			if (close < 0)
				fprintf(stderr, "Modbus plugin: Error closing thread for modbus client %%s\n", client_nodes[index].location);
		}
		res |= close;

		close = 0;
		if (client_nodes[index].init_state >= 1) {
			// modbus client node was created, so we try to close it!
			close = mb_master_close (client_nodes[index].mb_nd);
			if (close < 0){
				fprintf(stderr, "Modbus plugin: Error closing modbus client node %%s\n", client_nodes[index].location);
				// We try to shut down as much as possible, so we do not return noW!
			}
			client_nodes[index].mb_nd = -1;
		}
		res |= close;
		client_nodes[index].init_state = 0;
	}

	/* kill thread and close connections of each modbus server node */
//	for (index=0; index < NUMBER_OF_SERVER_NODES; index++) {
//		close = 0;
//		if (server_nodes[index].init_state >= 2) {
//			// thread was launched, so we try to cancel it!
//			close  = pthread_cancel(server_nodes[index].thread_id);
//			close |= pthread_join  (server_nodes[index].thread_id, NULL);
//			if (close < 0)
//				fprintf(stderr, "Modbus plugin: Error closing thread for modbus server %%s\n", server_nodes[index].location);
//		}
//		res |= close;
//
//		close = 0;
//		if (server_nodes[index].init_state >= 1) {
//			// modbus server node was created, so we try to close it!
//			close = mb_slave_close (server_nodes[index].mb_nd);
//			if (close < 0) {
//				fprintf(stderr, "Modbus plugin: Error closing node for modbus server %%s (%%d)\n", server_nodes[index].location, server_nodes[index].mb_nd);
//				// We try to shut down as much as possible, so we do not return noW!
//			}
//			server_nodes[index].mb_nd = -1;
//		}
//		res |= close;
//		server_nodes[index].init_state = 0;
//	}

	/* destroy the mutex of each client request */
	for (index=0; index < NUMBER_OF_CLIENT_REQTS; index ++) {
		if (pthread_mutex_destroy(&(client_requests[index].coms_buf_mutex))) {
			fprintf(stderr, "Modbus plugin: Error destroying request for modbus client node %%s\n", client_nodes[client_requests[index].client_node_id].location);
			// We try to shut down as much as possible, so we do not return noW!
			res |= -1;
		}
	}

	/* modbus library close */
	//fprintf(stderr, "Shutting down modbus library...\n");
	if (mb_slave_and_master_done()<0) {
		fprintf(stderr, "Modbus plugin: Error shutting down modbus library\n");
		res |= -1;
	}

	return res;
}

 