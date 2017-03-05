import recv_packet_constructor

print 'Starting.\n'

#Receiving garbled messages from client
data0 = '<full_message1>'
data1 = 'message0><full_message2><testing_'
data2 = 'message1><full_message3>'
data3 = 'garbage'
data4 = 'sdfe><start_'
data5 = 'of_new'
data6 = '_message><Hello.>dgdfg'
data7 = 'more_garbage<<<hey'
data8 = '_yo..>>>dsdsf'


print recv_packet_constructor.createCompletePacket(data0)
print recv_packet_constructor.createCompletePacket(data1)
print recv_packet_constructor.createCompletePacket(data2)
print recv_packet_constructor.createCompletePacket(data3)
print recv_packet_constructor.createCompletePacket(data4)
print recv_packet_constructor.createCompletePacket(data5)
print recv_packet_constructor.createCompletePacket(data6)
print recv_packet_constructor.createCompletePacket(data7)
print recv_packet_constructor.createCompletePacket(data8)


print '\nDone.'
