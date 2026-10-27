
chars = [(chr(0xc9),chr(0xc8),chr(0xc0),chr(0xc7),chr(0xca),chr(0xd9),chr(0xdb),chr(0xdc),chr(0xce),chr(0xd4),chr(0xd6),chr(0x152),chr(0xab),chr(0xbb),chr(0xb0))]
for c in chars[0]:
    b = c.encode("utf-8")
    l1 = "".join(chr(x) for x in b)
    try:
        cp = b.decode("cp1252")
    except:
        cp = None
    l1e = "+".join("U+%04X" % ord(x) for x in l1)
    cpe = "+".join("U+%04X" % ord(x) for x in cp) if cp else "FAIL"
    print("U+%04X L1=%s CP=%s" % (ord(c), l1e, cpe))
