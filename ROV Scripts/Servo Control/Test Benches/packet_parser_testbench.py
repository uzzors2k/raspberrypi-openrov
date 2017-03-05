import packet_parser

print 'Starting.\n'

#Receiving garbled messages from client
defaultMessagePacket = ("<SET_VIDEO_RECORD:0;SET_LIGHT:0;ROTATE_ROV_YAW:0; \
						TRANSLATE_ROV_X:0;TRANSLATE_ROV_Y:0; \
						TRANSLATE_ROV_Z:0;ROTATE_CAMERA_YAW:0; \
						ROTATE_CAMERA_PITCH:0;>")

simplePacket = ("<SET_VIDEO_RECORD:1;SET_LIGHT:2;ROTATE_ROV_YAW:3; \
						TRANSLATE_ROV_X:4;TRANSLATE_ROV_Y:5; \
						TRANSLATE_ROV_Z:6;ROTATE_CAMERA_YAW:7; \
						ROTATE_CAMERA_PITCH:8;>")

longerPacket = ("<SET_VIDEO_RECORD:1677;SET_LIGHT:234534;ROTATE_ROV_YAW:312334; \
						TRANSLATE_ROV_X:42432;TRANSLATE_ROV_Y:-5675; \
						TRANSLATE_ROV_Z:64323;ROTATE_CAMERA_YAW:-3457; \
						ROTATE_CAMERA_PITCH:-435448;>")
						
brokenPacket = ("<SET_VIDEO_ORD:1;SET_LIGHT:2;RATE_ROV_YAW:3; \
						TRANSLATE_ROV_X:4TRANSLATE_ROV_Y:5; \
						TRANSLATE_ROV_Z:6OTATE_CAMERA_YA7; \
						ROTATE_CAMERA_PITCH:8>")
						
derpPacket = ("<SET_VIDEO_RECORD:sdas;SET_LIGHT:gfd;ROTATE_ROV_YAW:3; \
						TRANSLATE_ROV_X:4;TRANSLATE_ROV_Y:5ds; \
						TRANSLATE_ROV_Z:sdd6sd;ROTATE_CAMERA_YAW:dsd7; \
						ROTATE_CAMERA_PITCH:8;>")

print packet_parser.parseDataPacket(defaultMessagePacket)
print packet_parser.parseDataPacket(simplePacket)
print packet_parser.parseDataPacket(longerPacket)
print packet_parser.parseDataPacket(brokenPacket)
print packet_parser.parseDataPacket(derpPacket)


print '\nDone.'
