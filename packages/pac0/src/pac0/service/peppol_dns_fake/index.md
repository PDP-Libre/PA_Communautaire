# peppol fake dns

```shell
# start the DNS service
uv run src/pac0/service/peppol_dns_fake/main.py
```

```shell
# Dig command to query a NAPTR record on the local Python DNS service
# Using port 5353 (non-privileged port)

# Query NAPTR record for naptr.example.com
dig @127.0.0.1 -p 5353 naptr.example.com NAPTR

# Query NAPTR record for peppol.example.com (Peppol service example)
dig @127.0.0.1 -p 5353 peppol.example.com NAPTR

# With more verbose output
dig @127.0.0.1 -p 5353 naptr.example.com NAPTR +short
dig @127.0.0.1 -p 5353 naptr.example.com NAPTR +nocomments +noquestion +noauthority +noadditional +nostats

# If you want to test other record types on the same service:
dig @127.0.0.1 -p 5353 example.com A
dig @127.0.0.1 -p 5353 ipv6.example.com AAAA
dig @127.0.0.1 -p 5353 txt.example.com TXT

# To test wildcard functionality:
dig @127.0.0.1 -p 5353 anything.test A
dig @127.0.0.1 -p 5353 myservice.test A

# Alternative using nslookup (if dig is not available)
# nslookup -type=NAPTR naptr.example.com 127.0.0.1:5353
```