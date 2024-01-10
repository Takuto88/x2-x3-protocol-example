import socket
import struct
import uuid

# Constants for readability
PDU_TYPE_X2 = 1
PAYLOAD_DIRECTION_FROM_TARGET = 3
MATCHED_TARGET_IDENTFIER = 17
SIP_MESSAGE = 9
SIP_REGISTER_PAYLOAD = """REGISTER sip:sipgate.de SIP/2.0
Via: SIP/2.0/UDP 172.17.0.2:39394;rport;branch=z9hG4bKPj-4R98i4RvoCb4q-VSGShXvKQGBQtWIka
Route: <sip:proxy.dev.sipgate.de;lr>
Max-Forwards: 70
From: <sip:1124349e3@sipgate.de>;tag=EkHkLSqYWMb8nE3qwGYmoj.CJFMtxFUt
To: <sip:1124349e3@sipgate.de>
Call-ID: q0nY4TGkm1Q98R40QDnmVrF71BXImUgu
CSeq: 39154 REGISTER
User-Agent: pjsip python
Contact: <sip:1124349e3@172.17.0.2:39394;ob>
Expires: 300
Allow: PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, INFO, SUBSCRIBE, NOTIFY, REFER, MESSAGE, OPTIONS
Content-Length:  0

"""


class ConditionalAttribute:

    def __init__(self):
        self.type = MATCHED_TARGET_IDENTFIER
        self.value = "<E164Number>494012345678</E164Number>"

    def pack(self):
        length = len(self.value)
        format = "!HH{}s".format(length)
        return struct.pack(format, self.type, length, self.value.encode('utf-8'))

class X2X3Packet:

    def __init__(self, pduType, payload):
        self.majorVersion = 0
        self.minorVersion = 5
        self.pduType = pduType
        self.headerLength = 40 + len(ConditionalAttribute().pack())
        self.payloadLength = len(payload)
        self.payloadDirection = PAYLOAD_DIRECTION_FROM_TARGET
        self.payloadFormat = SIP_MESSAGE
        self.xid = uuid.uuid4().int
        self.correlationId = 1
        self.conditionalAttributes = ConditionalAttribute().pack()
        self.payload = payload

    def pack(self):

        format = "!hhiihh16sQ{}s{}s".format(len(self.conditionalAttributes), len(self.payload))
        xidBytes = self.xid.to_bytes(16, byteorder="big")
        return struct.pack(
            format,
        self.majorVersion + self.minorVersion,
            self.pduType,
            self.headerLength,
            self.payloadLength,
            self.payloadFormat,
            self.payloadDirection,
            xidBytes,
            self.correlationId,
            self.conditionalAttributes,
            self.payload.encode('utf-8')
        )




def send_x2_packet():
    x2packet = X2X3Packet(PDU_TYPE_X2, SIP_REGISTER_PAYLOAD).pack()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 8888))
        s.connect(("127.0.0.1", 9999))
        s.sendall(x2packet)


if __name__ == '__main__':
    send_x2_packet()
