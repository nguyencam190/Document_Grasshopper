"""Mở cổng lệnh cho MayaMCP — dán vào Script Editor của Maya, tab Python.

Chạy MỖI PHIÊN Maya. Muốn Maya tự chạy khi khởi động thì chép nội dung file này
vào userSetup.py — nhưng cân nhắc: mở cổng tự động nghĩa là máy luôn có một cửa
chạy mã. Xem BAO_MAT.md §5.
"""
from maya import cmds

PORT = 50007          # MayaMCP ghi cứng số này, không đổi được

name = f":{PORT}"
if cmds.commandPort(name, query=True):
    print(f"Cổng {PORT} đã mở sẵn.")
else:
    # sourceType phải là 'mel': MayaMCP bọc Python trong lệnh MEL python("...")
    cmds.commandPort(name=name, sourceType="mel")
    print(f"Đã mở cổng {PORT}. MayaMCP nối được rồi.")

# Đóng lại khi xong việc:
#   cmds.commandPort(name=":50007", close=True)
