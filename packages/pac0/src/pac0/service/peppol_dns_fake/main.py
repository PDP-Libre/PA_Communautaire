#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Local DNS Server Implementation
This script creates a DNS service that responds to dig queries.
Supports A, AAAA, TXT, and NAPTR records.
"""

import socket
import struct
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import time
import os

# DNS Constants
DNS_PORT = 53
DNS_HEADER_SIZE = 12
MAX_DNS_PACKET_SIZE = 512  # Standard DNS UDP packet size

# DNS QTYPE values (common types)
QTYPE_A = 1
QTYPE_NS = 2
QTYPE_CNAME = 5
QTYPE_SOA = 6
QTYPE_PTR = 12
QTYPE_MX = 15
QTYPE_TXT = 16
QTYPE_AAAA = 28
QTYPE_SRV = 33
QTYPE_NAPTR = 35

# DNS QCLASS values
QCLASS_IN = 1  # Internet class

# DNS Response Codes
RCODE_NO_ERROR = 0
RCODE_FORMAT_ERROR = 1
RCODE_SERVER_FAILURE = 2
RCODE_NAME_ERROR = 3
RCODE_NOT_IMPLEMENTED = 4
RCODE_REFUSED = 5


@dataclass
class DNSQuestion:
    """Represents a DNS question section."""

    name: str
    qtype: int
    qclass: int


@dataclass
class DNSResourceRecord:
    """Represents a DNS resource record."""

    name: str
    rtype: int
    rclass: int
    ttl: int
    rdata: bytes


class DNSMessage:
    """Represents a DNS message with parsing and building capabilities."""

    def __init__(self):
        # Header fields
        self.id = 0
        self.qr = 0  # 0=query, 1=response
        self.opcode = 0  # 0=standard query
        self.aa = 0  # Authoritative Answer
        self.tc = 0  # Truncated
        self.rd = 0  # Recursion Desired
        self.ra = 0  # Recursion Available
        self.z = 0  # Reserved
        self.rcode = 0  # Response code
        self.qdcount = 0  # Question count
        self.ancount = 0  # Answer count
        self.nscount = 0  # Authority count
        self.arcount = 0  # Additional count

        # Sections
        self.questions: List[DNSQuestion] = []
        self.answers: List[DNSResourceRecord] = []
        self.authorities: List[DNSResourceRecord] = []
        self.additionals: List[DNSResourceRecord] = []

    def parse(self, data: bytes) -> bool:
        """Parse DNS message from bytes."""
        if len(data) < DNS_HEADER_SIZE:
            return False

        # Parse header
        self.id = struct.unpack("!H", data[0:2])[0]
        flags = struct.unpack("!H", data[2:4])[0]

        self.qr = (flags >> 15) & 0x1
        self.opcode = (flags >> 11) & 0xF
        self.aa = (flags >> 10) & 0x1
        self.tc = (flags >> 9) & 0x1
        self.rd = (flags >> 8) & 0x1
        self.ra = (flags >> 7) & 0x1
        self.z = (flags >> 4) & 0x7
        self.rcode = flags & 0xF

        self.qdcount = struct.unpack("!H", data[4:6])[0]
        self.ancount = struct.unpack("!H", data[6:8])[0]
        self.nscount = struct.unpack("!H", data[8:10])[0]
        self.arcount = struct.unpack("!H", data[10:12])[0]

        # Parse questions
        offset = DNS_HEADER_SIZE
        for _ in range(self.qdcount):
            name, offset = self._parse_domain_name(data, offset)
            qtype = struct.unpack("!H", data[offset : offset + 2])[0]
            qclass = struct.unpack("!H", data[offset + 2 : offset + 4])[0]
            offset += 4

            self.questions.append(DNSQuestion(name, qtype, qclass))

        # Parse answers, authorities, and additionals
        for _ in range(self.ancount):
            rr, offset = self._parse_resource_record(data, offset)
            self.answers.append(rr)

        for _ in range(self.nscount):
            rr, offset = self._parse_resource_record(data, offset)
            self.authorities.append(rr)

        for _ in range(self.arcount):
            rr, offset = self._parse_resource_record(data, offset)
            self.additionals.append(rr)

        return True

    def _parse_domain_name(self, data: bytes, offset: int) -> Tuple[str, int]:
        """Parse a domain name from DNS packet."""
        parts = []
        original_offset = offset

        while True:
            length = data[offset]
            offset += 1

            if length == 0:
                break

            if (length & 0xC0) == 0xC0:  # Compression pointer
                pointer = ((length & 0x3F) << 8) | data[offset]
                offset += 1
                # Recursively parse the compressed name
                name, _ = self._parse_domain_name(data, pointer)
                return name, offset

            part = data[offset : offset + length].decode("ascii", errors="replace")
            parts.append(part)
            offset += length

        return ".".join(parts), offset

    def _parse_resource_record(
        self, data: bytes, offset: int
    ) -> Tuple[DNSResourceRecord, int]:
        """Parse a resource record from DNS packet."""
        name, offset = self._parse_domain_name(data, offset)
        rtype = struct.unpack("!H", data[offset : offset + 2])[0]
        rclass = struct.unpack("!H", data[offset + 2 : offset + 4])[0]
        ttl = struct.unpack("!I", data[offset + 4 : offset + 8])[0]
        rdlength = struct.unpack("!H", data[offset + 8 : offset + 10])[0]
        rdata = data[offset + 10 : offset + 10 + rdlength]
        offset += 10 + rdlength

        return DNSResourceRecord(name, rtype, rclass, ttl, rdata), offset

    def build_response(self) -> bytes:
        """Build DNS response packet."""
        response = bytearray()

        # Build header
        response.extend(struct.pack("!H", self.id))

        # Build flags: QR=1, OPCODE=0, AA=1 (authoritative), RD=1, RA=0
        flags = (1 << 15) | (self.opcode << 11) | (1 << 10) | (self.rd << 8)
        response.extend(struct.pack("!H", flags))

        # Counts
        response.extend(struct.pack("!H", len(self.questions)))  # QDCOUNT
        response.extend(struct.pack("!H", len(self.answers)))  # ANCOUNT
        response.extend(struct.pack("!H", 0))  # NSCOUNT
        response.extend(struct.pack("!H", 0))  # ARCOUNT

        # Build questions
        for question in self.questions:
            response.extend(self._build_domain_name(question.name))
            response.extend(struct.pack("!HH", question.qtype, question.qclass))

        # Build answers
        for answer in self.answers:
            response.extend(self._build_domain_name(answer.name))
            response.extend(
                struct.pack("!HHI", answer.rtype, answer.rclass, answer.ttl)
            )
            response.extend(struct.pack("!H", len(answer.rdata)))
            response.extend(answer.rdata)

        return bytes(response)

    def _build_domain_name(self, name: str) -> bytes:
        """Build domain name in DNS format."""
        result = bytearray()
        for part in name.split("."):
            result.append(len(part))
            result.extend(part.encode("ascii"))
        result.append(0)  # Null terminator
        return bytes(result)


class DNSServer:
    """
    Simple DNS server that responds to queries with predefined records.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5353):
        """
        Initialize DNS server.
        Using port 5353 instead of 53 to avoid requiring root privileges.
        """
        self.host = host
        self.port = port
        self.running = False
        self.socket = None

        # Predefined DNS records database
        self.records: Dict[str, List[DNSResourceRecord]] = self._create_sample_records()

    def _create_sample_records(self) -> Dict[str, List[DNSResourceRecord]]:
        """Create sample DNS records for testing."""
        records = {}

        # A record for example.com -> 127.0.0.1
        records["example.com"] = [
            DNSResourceRecord(
                name="example.com",
                rtype=QTYPE_A,
                rclass=QCLASS_IN,
                ttl=300,
                rdata=socket.inet_aton("127.0.0.1"),
            )
        ]

        # AAAA record for ipv6.example.com -> ::1
        records["ipv6.example.com"] = [
            DNSResourceRecord(
                name="ipv6.example.com",
                rtype=QTYPE_AAAA,
                rclass=QCLASS_IN,
                ttl=300,
                rdata=socket.inet_pton(socket.AF_INET6, "::1"),
            )
        ]

        # TXT record for txt.example.com
        records["txt.example.com"] = [
            DNSResourceRecord(
                name="txt.example.com",
                rtype=QTYPE_TXT,
                rclass=QCLASS_IN,
                ttl=300,
                rdata=self._build_txt_data(["Hello DNS Server!", "v=1.0"]),
            )
        ]

        # NAPTR record for naptr.example.com (SIP service)
        records["naptr.example.com"] = [
            DNSResourceRecord(
                name="naptr.example.com",
                rtype=QTYPE_NAPTR,
                rclass=QCLASS_IN,
                ttl=300,
                rdata=self._build_naptr_data(
                    order=10,
                    preference=50,
                    flags="S",
                    services="SIP+D2U",
                    regexp="",
                    replacement="_sip._udp.example.com",
                ),
            ),
            DNSResourceRecord(
                name="naptr.example.com",
                rtype=QTYPE_NAPTR,
                rclass=QCLASS_IN,
                ttl=300,
                rdata=self._build_naptr_data(
                    order=20,
                    preference=100,
                    flags="S",
                    services="SIP+D2T",
                    regexp="",
                    replacement="_sip._tcp.example.com",
                ),
            ),
        ]

        # NAPTR record for peppol.example.com (Peppol service)
        records["peppol.example.com"] = [
            DNSResourceRecord(
                name="peppol.example.com",
                rtype=QTYPE_NAPTR,
                rclass=QCLASS_IN,
                ttl=300,
                rdata=self._build_naptr_data(
                    order=10,
                    preference=100,
                    flags="S",
                    services="PEPPOL-AS4",
                    regexp="",
                    replacement="_peppol-as4._tcp.peppol.example.com",
                ),
            ),
            DNSResourceRecord(
                name="peppol.example.com",
                rtype=QTYPE_NAPTR,
                rclass=QCLASS_IN,
                ttl=300,
                rdata=self._build_naptr_data(
                    order=20,
                    preference=50,
                    flags="S",
                    services="PEPPOL-SMP",
                    regexp="",
                    replacement="_peppol-smp._tcp.peppol.example.com",
                ),
            ),
        ]

        # Wildcard record for any .test domain
        records["test"] = [
            DNSResourceRecord(
                name="*.test",
                rtype=QTYPE_A,
                rclass=QCLASS_IN,
                ttl=300,
                rdata=socket.inet_aton("192.168.1.100"),
            )
        ]

        return records

    def _build_txt_data(self, strings: List[str]) -> bytes:
        """Build TXT record data from list of strings."""
        data = bytearray()
        for s in strings:
            encoded = s.encode("ascii")
            data.append(len(encoded))
            data.extend(encoded)
        return bytes(data)

    def _build_naptr_data(
        self,
        order: int,
        preference: int,
        flags: str,
        services: str,
        regexp: str,
        replacement: str,
    ) -> bytes:
        """
        Build NAPTR record data according to RFC 3403.

        Format:
        - ORDER (16 bits): Processing order
        - PREFERENCE (16 bits): Preference within same ORDER
        - FLAGS (string): Control flags (e.g., 'S', 'A', 'U')
        - SERVICES (string): Service parameters
        - REGEXP (string): Regular expression
        - REPLACEMENT (domain-name): Replacement domain
        """
        data = bytearray()

        # Order and preference
        data.extend(struct.pack("!HH", order, preference))

        # Flags (length-prefixed string)
        flags_bytes = flags.encode("ascii")
        data.append(len(flags_bytes))
        data.extend(flags_bytes)

        # Services (length-prefixed string)
        services_bytes = services.encode("ascii")
        data.append(len(services_bytes))
        data.extend(services_bytes)

        # Regexp (length-prefixed string)
        regexp_bytes = regexp.encode("ascii")
        data.append(len(regexp_bytes))
        data.extend(regexp_bytes)

        # Replacement domain (in DNS name format)
        for part in replacement.split("."):
            if part:  # Skip empty parts
                data.append(len(part))
                data.extend(part.encode("ascii"))
        data.append(0)  # Null terminator

        return bytes(data)

    def _find_records(self, name: str, qtype: int) -> List[DNSResourceRecord]:
        """Find matching DNS records for a query."""
        # Exact match
        if name in self.records:
            matching = [r for r in self.records[name] if r.rtype == qtype]
            if matching:
                return matching

        # Wildcard match for subdomains of .test
        if name.endswith(".test") and "test" in self.records:
            # Replace the actual subdomain with wildcard
            wildcard_name = "*.test"
            matching = [r for r in self.records["test"] if r.rtype == qtype]
            if matching:
                # Clone the record with the actual query name
                return [
                    DNSResourceRecord(
                        name=name,
                        rtype=rr.rtype,
                        rclass=rr.rclass,
                        ttl=rr.ttl,
                        rdata=rr.rdata,
                    )
                    for rr in matching
                ]

        return []  # No records found

    def _handle_query(
        self, data: bytes, client_addr: Tuple[str, int]
    ) -> Optional[bytes]:
        """Handle incoming DNS query and return response."""
        
        try:
            # Parse the query
            query = DNSMessage()
            if not query.parse(data):
                print(f"Failed to parse DNS query from {client_addr[0]}")
                return None

            # Log the query
            if query.questions:
                question = query.questions[0]
                qtype_str = self._qtype_to_string(question.qtype)
                print(
                    f"Query from {client_addr[0]}:{client_addr[1]} - "
                    f"{question.name} {qtype_str} (ID: {query.id})"
                )

            # Create response
            response = DNSMessage()
            response.id = query.id
            response.rd = query.rd
            response.questions = query.questions

            # Set response code
            response.rcode = RCODE_NO_ERROR

            # Answer each question
            for question in query.questions:
                if question.qclass != QCLASS_IN:
                    # We only support IN class
                    continue

                # Find matching records
                records = self._find_records(question.name, question.qtype)

                # If no exact type match, try CNAME or return empty
                if not records and question.qtype != QTYPE_CNAME:
                    # Check for CNAME records
                    cname_records = self._find_records(question.name, QTYPE_CNAME)
                    records.extend(cname_records)

                # Add found records to answers
                for record in records:
                    response.answers.append(record)

            # Build and return response
            return response.build_response()

        except Exception as e:
            print(f"Error handling query from {client_addr}: {e}")
            return None

    def _qtype_to_string(self, qtype: int) -> str:
        """Convert QTYPE integer to string representation."""
        qtype_map = {
            QTYPE_A: "A",
            QTYPE_AAAA: "AAAA",
            QTYPE_TXT: "TXT",
            QTYPE_NAPTR: "NAPTR",
            QTYPE_CNAME: "CNAME",
            QTYPE_NS: "NS",
            QTYPE_SOA: "SOA",
            QTYPE_PTR: "PTR",
            QTYPE_MX: "MX",
            QTYPE_SRV: "SRV",
        }
        return qtype_map.get(qtype, f"UNKNOWN({qtype})")

    def start(self):
        """Start the DNS server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket.bind((self.host, self.port))
        except PermissionError:
            print(f"Error: Cannot bind to port {self.port}. Try a port above 1024.")
            print(f"Starting server on port {self.port + 1000} instead.")
            self.port += 1000
            self.socket.bind((self.host, self.port))

        self.running = True
        print(f"DNS Server started on {self.host}:{self.port}")
        print("Supported domains:")
        for domain in sorted(self.records.keys()):
            for record in self.records[domain]:
                print(f"  {domain} ({self._qtype_to_string(record.rtype)})")
        print("\nUse Ctrl+C to stop the server.\n")

    def run(self):
        """Run the DNS server main loop."""
        self.start()

        try:
            while self.running:
                try:
                    # Set timeout to allow checking self.running
                    self.socket.settimeout(1.0)
                    data, addr = self.socket.recvfrom(MAX_DNS_PACKET_SIZE)

                    # Handle query in a separate thread for concurrency
                    response = self._handle_query(data, addr)
                    if response:
                        self.socket.sendto(response, addr)

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error in main loop: {e}")

        except KeyboardInterrupt:
            print("\nShutting down DNS server...")
        finally:
            self.stop()

    def stop(self):
        """Stop the DNS server."""
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        print("DNS Server stopped.")


def main():
    """Main entry point for the DNS server."""
    # Create and run DNS server on localhost with non-privileged port
    port = int(os.environ.get("PORT", "5353"))
    server = DNSServer(host="127.0.0.1", port=port)

    # You can also run it on all interfaces with:
    # server = DNSServer(host='0.0.0.0', port=5353)

    try:
        server.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
