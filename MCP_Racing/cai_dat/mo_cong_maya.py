# -*- coding: utf-8 -*-
# ==========================================================================
#  MO CONG LENH CHO MayaMCP
#
#  DAN VAO TAB "Python" CUA SCRIPT EDITOR - KHONG PHAI TAB "MEL".
#  Dan nham tab MEL se bao "// Error: Line 1.2: Syntax error".
#
#  Chay MOI PHIEN MAYA. Cong khong tu mo lai sau khi dong Maya.
#  Muon tu chay khi khoi dong thi chep noi dung file nay vao userSetup.py,
#  nhung can nhac: may se luon co mot cua chay ma. Xem BAO_MAT.md muc 5.
#
#  Ghi chu: khong dung dau tieng Viet trong file nay - Script Editor cua
#  Maya hay lam hong ky tu co dau khi dan vao.
# ==========================================================================
from maya import cmds

PORT = 50007          # MayaMCP ghi cung so nay trong code, khong doi duoc

name = ":%d" % PORT
if cmds.commandPort(name, query=True):
    print("Cong %d da mo san." % PORT)
else:
    # sourceType phai la 'mel': MayaMCP boc Python trong lenh MEL python("...")
    # Cai nay khong lien quan den tab ban dang dan - van dan vao tab Python.
    cmds.commandPort(name=name, sourceType="mel")
    print("Da mo cong %d. MayaMCP noi duoc roi." % PORT)

# Dong lai khi xong viec:
#   cmds.commandPort(name=":50007", close=True)
