from pymem import Pymem

ADDRS = [0x3A70FD4, 0x3A878DC, 0x3AA0508, 0x3AC85F0, 0x3ACF3D8, 0x3AD1908]

try:
    pm = Pymem("WeChat.exe")
    WeChatWindll_base = 0
    for m in list(pm.list_modules()):
        path = m.filename
        if path.endswith("WeChatWin.dll"):
            WeChatWindll_base = m.lpBaseOfDll
            break

    for offset in ADDRS:
        addr = WeChatWindll_base + offset
        v = pm.read_uint(addr)
        if v != 0x63090551:
            raise Exception("Wrong wechat version, need 3.9.5.81")
        else:
            pm.write_uint(addr, 0x63090A13)

    print('Fix Success')
except:
    print('Fix Failed')
