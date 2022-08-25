from __future__ import annotations

from zerocom.exceptions import MalformedPacketError, MalformedPacketState
from zerocom.packets.abc import Packet
from zerocom.packets.ping import Ping, Pong
from zerocom.protocol.base_io import BaseAsyncReader, BaseAsyncWriter
from zerocom.protocol.buffer import Buffer

_PACKETS: list[type[Packet]] = [Ping, Pong]
PACKET_MAP: dict[int, type[Packet]] = {}

for packet_cls in _PACKETS:
    PACKET_MAP[packet_cls.PACKET_ID] = packet_cls


# PACKET FORMAT:
# | Field name  | Field type    | Notes                                 |
# |-------------|---------------|---------------------------------------|
# | Length      | 32-bit varint | Length (in bytes) of PacketID + Data  |
# | Packet ID   | 32-bit varint |                                       |
# | Data        | byte array    | Internal data to packet of given id   |


def _serialize_packet(packet: Packet) -> Buffer:
    """Serialize the internal packet data, along with it's pacekt id."""
    packet_buf = Buffer()
    packet_buf.write_varint(packet.PACKET_ID, max_bits=32)
    packet_buf.write(packet.serialize())
    return packet_buf


def _deserialize_packet(data: Buffer) -> Packet:
    """Deserialize the packet id and it's internal data."""
    try:
        packet_id = data.read_varint(max_bits=32)
        packet_data = data.read(data.remaining)
    except IOError as exc:
        raise MalformedPacketError(MalformedPacketState.MALFORMED_PACKET_DATA, ioerror=exc)

    try:
        packet_cls = PACKET_MAP[packet_id]
    except KeyError:
        raise MalformedPacketError(MalformedPacketState.UNRECOGNIZED_PACKET_ID, packet_id=packet_id)

    try:
        return packet_cls.deserialize(Buffer(packet_data))
    except IOError as exc:
        raise MalformedPacketError(MalformedPacketState.MALFORMED_PACKET_BODY, ioerror=exc, packet_id=packet_id)


async def write_packet(writer: BaseAsyncWriter, packet: Packet) -> None:
    """Write given packet."""
    data_buf = _serialize_packet(packet)
    await writer.write_varint(len(data_buf), max_bits=32)
    await writer.write(data_buf)


async def read_packet(reader: BaseAsyncReader) -> Packet:
    """Read any arbitrary packet based on it's ID."""
    try:
        length = await reader.read_varint(max_bits=32)
        data = await reader.read(length)
    except IOError as exc:
        raise MalformedPacketError(MalformedPacketState.MALFORMED_PACKET_DATA, ioerror=exc)
    return _deserialize_packet(Buffer(data))
