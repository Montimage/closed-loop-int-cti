#!/usr/bin/env python3

# Extract features from pcap files, then create a DecisionTree model.
# The pcap file contains packets of a single flow which is sent through switch.
#
# A very simple DecisionTree model is constructed from 2 features:
#  - packet length
#  - difference of packet length
#

from scapy.all import *
import argparse, csv, os
from sklearn import tree
import pickle


def extract_features_from_pcap( inputfile, classification ):
    results = []
    last_len = 0

    #read the pcap file and extract the features for each packet
    all_packets = rdpcap(inputfile)

    # for each packet in the pcap file
    for packet in all_packets:
        try:
            ts     = packet.time # e.g., 1712073023.619379
            ip_len = packet.len  # e.g., 76

            ts = int( ts * 1000000 * 1000) # in nanosecond

            # for the first time
            if last_len == 0:
                last_len = ip_len
                continue

            diff_len = ip_len - last_len
            diff_len += 0xFFFF #avoid negative value

            last_len = ip_len

            metric = { "diffLen": diff_len, "len": ip_len, "classification": classification }
            results.append( metric )
        except AttributeError:
            print("Error while parsing packet", packet)

    print("processed {0} packets from {1}".format( len(results), inputfile))
    return results; 

data  =  extract_features_from_pcap( "pcap/normal.pcap", 0 )
data +=  extract_features_from_pcap( "pcap/botnet.pcap", 1 )

print("got total {0} records".format( len(data)))

# write to csv file
# append to output file
print("write records to dt.csv")
with open( "dt.csv", 'a', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, data[0].keys() )
    # write the header
    writer.writeheader()
    # write multiple rows
    writer.writerows( data )

# get only values
data = [i.values() for i in data]
data = [list(i) for i in data] #to be subscriptable

#print(data[1:10])

X = [i[0:-1] for i in data] #the columns before the last one are features
Y = [i[-1]   for i in data] #last column is "classification"

# decision tree: https://scikit-learn.org/stable/modules/tree.html#tree
dt = tree.DecisionTreeClassifier()
dt.fit(X, Y)

outputfile = "dt.model"
# dump model to f
print("write model to", outputfile)
pickle.dump(dt, open(outputfile, 'wb'))
