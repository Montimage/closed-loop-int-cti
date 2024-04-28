import os, csv, sys, json
import numpy as np

def proc_str( val ):
    #strip space
    val = val.strip()
    if val.startswith('"'):
        val = val[1:]
    if val.endswith('"'):
        val = val[:-1]
    return val

#convert to integer
def proc_ip_len( val ):
    val = int(val)
    val -= 14 #ethernet header
    val -= 56 #INT
    return val

def proc_float( val ):
    return float(val)

# convert nanosecond to microsecond
def proc_nsms( val ):
    return round(int(val) / 1000)

#map from MMT  metrics to the required metrics
MAP = {
    "ip.src"               : {"pre_proc": proc_str,    "new_name": "src-ip"},
    "ip.dst"               : {"pre_proc": proc_str,    "new_name": "dst-ip"},
    "meta.packet_len"      : {"pre_proc": proc_ip_len, "new_name": "len"},
    "timestamp"            : {"pre_proc": proc_float,  "new_name": "timestamp"}
}

RAW_HEADER_STR='report-id,probe-id,source,timestamp,report-name,int.hop_queue_ids,meta.packet_index,meta.packet_len,ip.src,ip.dst,ip.proto_tos,ip.ecn,ip.identification,udp.src_port,udp.dest_port,udp.len,tcp.src_port,tcp.dest_port,tcp.payload_len,tcp.seq_nb,tcp.ack_nb,tcp.tsval,tcp.tsecr,quic_ietf.header_form,quic_ietf.spin_bit,quic_ietf.rtt,int.hop_latencies,int.hop_queue_occups,int.hop_ingress_times,int.hop_egress_times,int.hop_l4s_mark,int.hop_l4s_drop,int.mark_probability'
# header of raw data generated by INT-collector
RAW_HEADER = [x.strip() for x in RAW_HEADER_STR.split(",")]

# convert raw message which is a line generated by INT-collector
#  to a dictionary
# Example:
#  input:
#   '1000,3,"l4s-mon-nic",1689953203.215916,"int",1,13,879,"10.0.1.13","10.0.0.13",131,3,0,10000,58630,789,0,0,0,0,0,0,0,1,0,0,24246,1,119775888000,119800134000,1,0,4294967295'
#  output:
#   {'len': 879, 'src-ip': '10.0.1.13', 'dst-ip': '10.0.0.13'}
def convert_message( raw_msg ):
    try:
        if not type(raw_msg) == str:
            return {}
        arr = [x.strip() for x in raw_msg.split(",")]
        #print( arr )
        # we are intersted in only event-based reports which have id=1000 and its name is "int"
        if not( arr[0] == "1000" and arr[4] == '"int"'):
            return {}

        new_msg = {}
        for i in range( len(arr) ):
            raw_header = RAW_HEADER[i]
            raw_value  = arr[i]
            #print("  {0} : {1}".format( raw_header, raw_value ))
            if raw_header in MAP:
                v = MAP[ raw_header ]
                new_msg[v["new_name"]] = v["pre_proc"]( raw_value )
        return new_msg
    except Exception as ex:
        print(ex)
        return {}


def _sort( v ):
    return v["timestamp"]


def _synthese_data( data, time_window ):
    data.sort(key = _sort )

    new_data = []
    last_len = data[0]["len"]

    for i in range(1, len(data)):
        row = data[i]
        # print(row)
        new_row = row.copy()
        new_row["diffLen"] = row["len"] - last_len;
        new_row["diffLen"] += 0xFFFF #shift to avoid negative value
        last_len = row["len"];  

        new_data.append( new_row )

    return new_data;


# all messages msg in a given time window
DATABASE=[]

# time_window is in microsecond
def get_synthesis_msg( msg, time_window=0.33000 ):
    global DATABASE
    DATABASE.append( msg )
    now = msg["timestamp"]
    #print(now)
    #whether we got enough messages in a timewindow
    if now - DATABASE[0]["timestamp"] > time_window:
        synthesis_msgs = _synthese_data( DATABASE, time_window )
        #clean database
        DATABASE = [DATABASE[-1]] # keep last element
        return synthesis_msgs
    return []


# to run a test
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\nUsage: python3 {0} <raw-message>".format( sys.argv[0]))
        print("""   Ex: python3 {0} '1000,3,"l4s-mon-nic",1689953203.215916,"int",1,13,879,"10.0.1.13","10.0.0.13",131,3,0,10000,58630,789,0,0,0,0,0,0,0,1,0,0,24246,1,119775888000,119800134000,1,0,4294967295'\n""".format( sys.argv[0]))
        sys.exit(1)
    print( convert_message( sys.argv[1]) )