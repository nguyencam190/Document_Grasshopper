# -*- coding: utf-8 -*-
# ==========================================================================
#  CAI paint_flow + retopo_paint VAO MAYA
#
#  DAN VAO TAB "Python" CUA SCRIPT EDITOR - KHONG PHAI TAB "MEL".
#  Dan nham tab MEL se bao "// Error: Line 1.2: Syntax error".
#
#  Chay xong se in ra huong dan dung. Chay MOI PHIEN MAYA (hoac chep phan
#  duoi vao userSetup.py de tu chay khi khoi dong).
#
#  Ghi chu: khong dung dau tieng Viet trong file nay - Script Editor cua
#  Maya hay lam hong ky tu co dau khi dan vao.
# ==========================================================================
import importlib
import os
import sys

from maya import cmds

# Neu tu tim khong ra, dien thang duong dan thu muc maya_tools vao day.
# Vi du: THU_MUC = r"D:\repo\Document_Grasshopper\MCP_Racing\artspec\artspec\maya_tools"
THU_MUC = ""

_DUOI = os.path.join("MCP_Racing", "artspec", "artspec", "maya_tools")


def _cac_goc():
    goc = [os.path.expanduser("~")]
    for bien in ("USERPROFILE", "OneDrive", "OneDriveConsumer"):
        if os.environ.get(bien):
            goc.append(os.environ[bien])
    for o in list(goc):
        for ten in ("Documents", "Desktop", "Downloads", "repo", "projects", "git"):
            goc.append(os.path.join(o, ten))
    for chu in "CDEF":
        goc.append(chu + ":\\")

    return goc


def tim_thu_muc():
    """Tim thu muc maya_tools trong cac cho hay dat repo."""
    goc = _cac_goc()
    for g in goc:
        thu = os.path.join(g, "Document_Grasshopper", _DUOI)
        if os.path.isdir(thu):
            return thu

    # Quet sau hon, gioi han 3 cap de khong treo Maya
    for g in goc:
        if not os.path.isdir(g):
            continue
        try:
            for ten in os.listdir(g):
                thu = os.path.join(g, ten, _DUOI)
                if os.path.isdir(thu):
                    return thu
        except OSError:
            pass
    return None


def cai(duong_dan=""):
    """Nap hai module. Truyen duong dan thu muc maya_tools neu tu tim khong ra."""
    thu = duong_dan or THU_MUC or tim_thu_muc()
    if thu and not os.path.isdir(thu):
        print("Duong dan khong ton tai: %s" % thu)
        thu = None
    if not thu:
        print("KHONG TIM RA thu muc maya_tools. Da tim trong:")
        for g in _cac_goc():
            print("    %s" % os.path.join(g, "Document_Grasshopper", _DUOI))
        print("")
        print("  Cach 1: goi thang voi duong dan cua ban, vi du")
        print("     cai(r'D:\\repo\\Document_Grasshopper%s')" % (os.sep + _DUOI))
        print("  Cach 2: dien vao dong THU_MUC o dau file nay roi dan lai.")
        print("")
        print("  Chua co repo tren may thi:  git clone "
              "https://github.com/nguyencam190/Document_Grasshopper")
        print("  Da co roi thi nho:  git pull   (hai module nay moi them)")
        return None

    if thu not in sys.path:
        sys.path.insert(0, thu)

    import paint_flow
    import retopo_paint
    importlib.reload(paint_flow)      # de sua code xong dan lai la an ngay
    importlib.reload(retopo_paint)

    print("Da nap tu: %s" % thu)
    print("")
    print("  1. Son huong luoi:")
    print("       import paint_flow")
    print("       paint_flow.start('<ten mesh>')   # bat co, mau do = net doc")
    print("       paint_flow.size(60)              # ban kinh 60 pixel")
    print("       paint_flow.v()                   # doi sang luc = net ngang")
    print("       paint_flow.stop()")
    print("     Ctrl + keo = xoa mau. Ctrl+Z hoan tac tung net.")
    print("")
    print("  2. Dung luoi quad theo vet da son:")
    print("       import retopo_paint")
    print("       bc = retopo_paint.build_from_paint('<ten mesh>')")
    print("       print(retopo_paint.report_text(bc))")
    print("")
    print("  Chay thu toan bo tren canh nhan tao:  tu_kiem()")
    return thu


# ==========================================================================
#  TU KIEM - dung canh thu roi chay ca quy trinh, bao hong o buoc nao
# ==========================================================================

NHOM = "retopoTuKiem_grp"


def tu_kiem():
    """Tao mat cong gia, son san hai ho vet, roi chay dung luoi va bao ket qua.

    Khong dong scene hien tai. Moi thu tao ra nam trong nhom retopoTuKiem_grp,
    xoa bang:  cmds.delete('retopoTuKiem_grp')
    """
    import numpy as np
    from maya.api import OpenMaya as om
    import retopo_paint

    buoc = "tao mat cong gia"
    try:
        if cmds.objExists(NHOM):
            cmds.delete(NHOM)
        mesh = cmds.polyPlane(w=10, h=10, sx=40, sy=40, name="tuKiem_scan")[0]
        cmds.group(mesh, name=NHOM)

        sel = om.MSelectionList()
        sel.add(mesh)
        dag = sel.getDagPath(0)
        dag.extendToShape()
        fn = om.MFnMesh(dag)

        pts = fn.getPoints(om.MSpace.kObject)
        for i in range(len(pts)):
            p = pts[i]
            p.y = 1.2 * np.cos(p.x * 0.25) * np.cos(p.z * 0.25)   # vom nhe
            pts[i] = p
        fn.setPoints(pts, om.MSpace.kObject)

        buoc = "tao color set va son vet"
        cmds.polyColorSet(mesh, create=True, colorSet="flowGuide",
                          representation="RGB")
        cmds.polyColorSet(mesh, currentColorSet=True, colorSet="flowGuide")
        cmds.setAttr(cmds.listRelatives(mesh, shapes=True)[0] + ".displayColors", 1)

        P = np.array([(p.x, p.y, p.z) for p in fn.getPoints(om.MSpace.kWorld)])
        day = 0.30
        for gia_tri, mau, truc in ((-3.0, (1, 0, 0), 0), (0.0, (1, 0, 0), 0),
                                   (3.0, (1, 0, 0), 0), (-3.0, (0, 1, 0), 2),
                                   (0.0, (0, 1, 0), 2), (3.0, (0, 1, 0), 2)):
            idx = np.flatnonzero(np.abs(P[:, truc] - gia_tri) < day)
            if idx.size:
                cmds.polyColorPerVertex(
                    ["%s.vtx[%d]" % (mesh, i) for i in idx.tolist()],
                    rgb=list(mau), colorDisplayOption=True)

        buoc = "doc mau va dung luoi"
        importlib.reload(retopo_paint)
        bc = retopo_paint.build_from_paint(mesh, out_name="tuKiem_luoi")
        cmds.parent(bc["mesh"], NHOM)

        print("")
        print(retopo_paint.report_text(bc))
        print("")
        b = bc["bien"]
        so_quad = bc["cham_diem"]["so_quad"]
        if bc["so_diem_giao"] != 9:
            print("CHU Y: mong doi 9 diem giao (3 net x 3 net), duoc %d"
                  % bc["so_diem_giao"])
        if not b["da_conform"]:
            print("CHU Y: chua conform bien - %s" % b.get("ly_do", ""))
        print("TU KIEM XONG: %d quad, %s. Xem nhom '%s' trong Outliner."
              % (so_quad, "da conform bien" if b["da_conform"] else "chua conform",
                 NHOM))
        print("Xoa canh thu:  cmds.delete('%s')" % NHOM)
        return bc

    except Exception as loi:                                  # noqa: BLE001
        import traceback
        print("")
        print("HONG O BUOC: %s" % buoc)
        print("%s: %s" % (type(loi).__name__, loi))
        print("")
        traceback.print_exc()
        print("")
        print("Gui nguyen doan tren cho Claude de sua.")
        return None


cai()
