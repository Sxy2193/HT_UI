# 在VideoWindow类中添加CRC校验方法
def crc16_modbus(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])


def build_packet(payload):
    head = b'\xFF'  # 包头
    footer = b'\xDD'  # 包尾
    length = bytes([len(payload)])
    crc_date = head + length + payload  # 包头+长度+载荷
    crc = crc16_modbus(crc_date)  # 校验码
    return head + length + payload + crc + footer  # 发送‘head+length+payload+crc+footer’即可


# 添加标准指令生成
def build_command(code):
    """生成标准指令 (FF + CODE + DD)"""
    return b'\xFF' + code + b'\xDD'
