# ===============================================
# Data Merge Generator v1.8 for Krita 
# ===============================================
# Copyright (C) 2026 L.Sumireneko.M
# This program is free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>. 

# This script is work SIMPLE data combine similar as ..Data-Merge,MailMerge

import re, os, time, json ,platform
import krita
from .qt_compat import (
    QtCore, QtGui, QC, qt_major, qt_exec,qt_event,QIODevice,
    QDialog, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QFileDialog, QComboBox, QMessageBox, QRadioButton, QButtonGroup, QFrame,
    QObject, QEvent, QTimer, QSignalBlocker, pyqtSignal, Qt, QFile, QPoint,
    QGuiApplication, QClipboard, QMimeDatabase,QCheckBox
)

# ========================
# Settings
# ========================
from .setting import *

dialog_title_txt = "Data Merge Generator v1.8"

plugin_id = "data_merge"
plugin_menu_entry_name = "Data Merge..."
plugin_where = "tools/scripts"

pmenu=[
    ['A4(V) - (300dpi W2480 x H3508 px)', '2480', '3508'],
    ['A4(H) - (300dpi W3508 x H2480 px)', '3508', '2480'],
    ['---', '0', '0'],
    ['A3(V) - (300dpi W3508 x H4961 px)', '3508', '4961'],
    ['A3(H) - (300dpi W4961 x H3508 px)', '4961', '3508'],
    ['---', '0', '0'],
    ['A4(V) - (600dpi W4961 x H7016 px)', '4961', '7016'],
    ['A4(H) - (600dpi W7016 x H4961 px)', '7016', '4961'],
    ['---', '0', '0'],
    ['A3(V) - (600dpi W7016 x H9921 px)', '7016', '9921'],
    ['A3(H) - (600dpi W9921 x H7016 px)', '9921', '7016'],
    ['---', '0', '0'],
    ['QVGA - ( W320 x H240 px)', '320', '240'],
    ['VGA - ( W640 x H480 px)', '640', '480'],
    ['SVGA - ( W800 x H600 px)', '800', '600'],
    ['XGA - ( W1024 x H768 px)', '1024', '768'],
    ['2K - ( W1920 x H1080 px)', '1920', '1080']
]




# ========================
# Mode Setting
# ========================
# Vector text layer in template.kra:  <<TITLE>> <<NAME>> <<CITY>> <<COLOR>>
# The words for replace in test.csv:
# TITLE,NAME,CITY,COLOR
# aaa,bbb,ccc,ddd
# Replace as <<TITLE>> to aaa,<<NAME>> to bbb ....

image_mode = True
old_time = 0

# ========================
# Debug
# ========================
TEST_DUMP_TRANSFORM_XML = False

def dump_transform_xml():
    doc = Krita.instance().activeDocument()
    if not doc:
        print("No active document")
        return

    node = doc.activeNode()
    if not node:
        print("No active node")
        return

    # make TransformMask 
    mask = doc.createTransformMask("TestMask")
    node.addChildNode(mask, None)

    # capture some movement
    xml = mask.toXML()

    print("===== TransformMask XML Dump =====")
    print(xml)
    print("===== END =====")

    # Remove
    node.removeChildNode(mask)


# ========================
# Utilites
# ========================

def tim_info(mes,st):
    global old_time
    now = time.time()

    elapse = now - st
    elapse = round(elapse, 2)
    dif = round( elapse - old_time , 2 )
    old_time = elapse
    print(f'*** {mes} TIME: {elapse} (+ {dif}) ')


def pos_info(obj,s):
    pos = obj.position()
    print( s + f'Name:{obj.name()} Position:{pos.x()},{pos.y()}')







# ========================
# Sub Process
# ========================

# Load text file 
def read_file(file_path):
    print(f"Loading file: {file_path}")
    if not file_path:
        return

    full_path = os.path.expanduser(file_path)
    mimeType = QMimeDatabase().mimeTypeForFile(full_path)
    if not mimeType.inherits("text/plain"):
        return

    file = QFile(full_path)
    if file.open(QC.IO.ReadOnly):
        rawdata = file.readAll()
        file.close()
        data = f"{str(rawdata, 'utf-8')}"
    #print('Load data:'+data)
    return data

# get vector layers
def get_vector_node_from_group(node_layer):
    target_vlayer = []
    cnt = 0
    for node in node_layer.childNodes():
        if node.type() == 'vectorlayer':
            if node.name().startswith(keep_layr_tag) == True: continue # if keeop layer name contain $$ at first
            if len(node.shapes()) == 0: continue
            if re.search('&lt;&lt;',node.toSvg()) == None : continue # It is not contain <<TAG>> text
            
            #print("Vector Layer:"+node.name())
            target_vlayer.append(node)
            cnt += 1
    #print('vlayer cnt:'+str(cnt))
    #print(target_vlayer)
    return target_vlayer


# get file layers
def get_file_node_from_group(node_layer):
    target_vlayer = []
    cnt = 0
    for node in node_layer.childNodes():
        if node.type() == 'filelayer':
            if node.name().startswith(keep_layr_tag) == True: continue # if keeop layer name contain $$ at first
            #print("FileLayer:"+node.name())
            target_vlayer.append(node)
            cnt += 1
    return target_vlayer

# ========================
# Main
# ========================
# Push Button and execute
def get_param(txt):
    #print("Param:"+str(txt))
    if txt == '':txt='0'
    txt = re.sub(r'[A-Za-z]','',txt) 
    num=int(eval(txt))
    #print("Calculated:"+str(num))
    return num

def get_txt_param(txt):
    #print("Param:"+str(txt))
    if txt == '':txt=' '
    txt = re.sub(r'(\.|\*|\\|\'|\"|\{|\}|:|\||;)','',txt) 
    return txt

TEST_MODE = False

def opendialog():
    global docx, docy, padx, pady, dx, dy, maxcol, umax, mode, rename_tag, dialog_title_txt, records
    print('Button clicked!!')

    if TEST_DUMP_TRANSFORM_XML:
        dump_transform_xml()
        return

    # Read Parameters from Dialog 
    docx = get_param(c_dlg.texbox1.text())
    docy = get_param(c_dlg.texbox2.text())
    padx = get_param(c_dlg.texbox3.text())
    pady = get_param(c_dlg.texbox4.text())
    dx = get_param(c_dlg.texbox5.text())
    dy = get_param(c_dlg.texbox6.text())
    maxcol = get_param(c_dlg.texbox7.text())
    umax = get_param(c_dlg.texbox11.text())
    mode = c_dlg.rg.checkedId()  # 0: Mask Mode, 1: Direct Mode
    rename_tag = get_txt_param(c_dlg.texbox12.text())

    #  Handle CSV File Path 
    if TEST_MODE:
        csv_path = "/file_path/to/template.csv"
    else:
        file = QFileDialog.getOpenFileName(None, 'Open CSV File', os.path.expanduser('~' + '/Desktop'), filter='CSV or TXT (*.csv *.txt)')
        if not file[0]:
            print("No file selected")
            return
        csv_path = file[0]

    st = time.time()
    
    krita_instance = Krita.instance()
    currentDoc = krita_instance.activeDocument()
    if not currentDoc:
        return
    res = currentDoc.resolution()

    # --- Data and Template Preparation ---
    data = read_file(csv_path)
    data_list = data.split(line_break) 
    
    templ = currentDoc.nodeByName("Template")
    if templ is None:
        print("Error: 'Template' layer not found")
        return

    # Create a clean clone for processing
    cloned_layer = templ.clone()
    cloned_layer.setName("Template_Cloned")

    # WORKAROUND: Remove existing TransformMasks inside FileLayers to prevent freezes
    # Because Current Krita freeze with calcuration of FileLayer+TransformMask thumbnail
    # DISABLED: Keeping TransformMasks on FileLayers significantly increases
    # processing load and may cause Krita to freeze during duplication.
    for child in cloned_layer.childNodes():
        if child.type() == 'filelayer':
            for sub_child in child.childNodes():
                if sub_child.type() == 'transformmask':
                    child.removeChildNode(sub_child)# if this disable, Transform mask will applied

    # Canvas Size Calculation 
    tw, th = templ.bounds().width(), templ.bounds().height()
    total_items = len(data_list)
    
    if c_dlg.chkbox.isChecked():
        max_width = dx * 2 + (maxcol * (tw + padx))
        if docx < max_width:
            docx = max_width
            
        if umax > 0:
            up_row = (umax + maxcol - 1) // maxcol
            target_height = dy * 2 + (up_row * (th + pady))
        else:
            max_row = (total_items + maxcol - 1) // maxcol
            target_height = dy * 2 + (max_row * (th + pady))
            
        if docy < target_height:
            docy = target_height

    # Start Processing 
    print('------ Process Start ------')
    regloop(data_list, res, st, cloned_layer)
    
    tim_info('All Process Finished ', st)
    c_dlg.close()


def regloop(data_list, res, st, cloned_layer):
    global docx, docy, padx, pady, dx, dy, maxcol, umax, mode, rename_tag, records
    
    document_name = 'NewDocument'
    pdx, idx = 0, 0
    page = 0
    
    tags = data_list.pop(0).split(splitter)
    krita_instance = Krita.instance()
    
    # Initialize First Document
    newDoc = krita_instance.createDocument(docx, docy, document_name, "RGBA", "U8", "", res)
    krita_instance.activeWindow().addView(newDoc)
    newDoc.rootNode().addChildNode(cloned_layer, None)
    newDoc.refreshProjection()
    
    base = newDoc.rootNode()
    temp_origin_layer = newDoc.nodeByName('Template_Cloned')
    
    b = temp_origin_layer.bounds()
    w, h = b.width(), b.height()

    mode_prefix = ["M:", "E:"][mode]
    rename_idx = -1
    if c_dlg.chkbox2.isChecked():
        for i, v in enumerate(tags):
            if v == rename_tag:
                rename_idx = i
                break

    # Main Loop
    for itm in data_list:
        # Handle Pagination
        if umax > 0 and idx > 0 and idx % umax == 0:
            page += 1
            # Remove seed template from old doc
            old_temp = newDoc.nodeByName("Template_Cloned")
            if old_temp: old_temp.remove()
            
            newDoc = krita_instance.createDocument(docx, docy, f'{document_name}{page}', "RGBA", "U8", "", res)
            krita_instance.activeWindow().addView(newDoc)
            
            # Re-import template via clipboard
            krita_instance.action('paste_layer_from_clipboard').trigger()
            newDoc.refreshProjection()
            
            base = newDoc.rootNode()
            temp_origin_layer = newDoc.nodeByName('Template_Cloned')
            pdx = 0

        prts = itm.split(splitter)
        
        # Layer Naming
        newname = f'{mode_prefix}New{idx}'
        if c_dlg.chkbox2.isChecked() and rename_idx != -1:
            name_val = get_txt_param(prts[rename_idx])
            newname = f'{mode_prefix}{idx}_{name_val}'

        # Duplicate and Add
        got_activeLayer = temp_origin_layer.duplicate()
        got_activeLayer.setName(newname)
        base.addChildNode(got_activeLayer, None)

        # WORKAROUND: Clean up inner masks in the duplicate
        # DISABLED: Keeping TransformMasks on FileLayers significantly increases
        # processing load and may cause Krita to freeze during duplication.
        for child in got_activeLayer.childNodes():
            if child.type() == 'filelayer':
                for sub_child in child.childNodes():
                    if sub_child.type() == 'transformmask':
                        child.removeChildNode(sub_child)

        text_layers = get_vector_node_from_group(got_activeLayer)
        
        # 1. Image Replacement
        if image_mode:
            for i, tag in enumerate(tags):
                if tag.startswith(img_layr_tag):
                    targets = got_activeLayer.findChildNodes(tag)
                    if targets:
                        replace_fileLayer(targets[0], prts[i])
        
        # 2. Vector/Text Replacement
        for node in text_layers:
            if node.type() == 'vectorlayer':
                svgdata = node.toSvg()
                replaced = False
                for i, tag in enumerate(tags):
                    if tag.startswith(img_layr_tag) and image_mode: continue
                    pattern = f'{lt}{tag}{gt}'
                    if pattern in svgdata:
                        svgdata = svgdata.replace(pattern, prts[i])
                        replaced = True
                
                if replaced:
                    vnode = newDoc.createVectorLayer('vector_new')
                    vnode.addShapesFromSvg(svgdata)
                    got_activeLayer.addChildNode(vnode, None)

        # 3. Cleanup original vectors
        for n in text_layers:
            n.remove()

        # Position and Layout 
        col, row = pdx % maxcol, pdx // maxcol
        tx, ty = dx + (col * (w + padx)), dy + (row * (h + pady))

        if mode == 0: # Transform Mask Mode
            mask = newDoc.createTransformMask(f'layout_mask_{idx}')
            mask.setColorLabel(4)
            mask.fromXML(transform_exe(tx, ty))
            got_activeLayer.addChildNode(mask, None)
        elif mode == 1: # Direct Edit Mode
            # Mode 1: Reset FileLayer internal position before moving parent ---
            pos_children(got_activeLayer, tx, ty, newDoc)

        idx += 1
        pdx += 1
    
    # Final cleanup of seed template
    final_temp = newDoc.nodeByName("Template_Cloned")
    if final_temp:
        final_temp.remove()
    
    newDoc.refreshProjection()



# The transform mask that based on Krita 5.x 
def transform_exe(xxx,yyy):
    return f'''<!DOCTYPE transform_params>
    <transform_params>
    <main id="tooltransformparams"/>
    <data mode="0">
    <free_transform>
    <transformedCenter y="{yyy}" type="pointf" x="{xxx}"/>
    <originalCenter y="0" type="pointf" x="0"/>
    <rotationCenterOffset y="0" type="pointf" x="0"/>
    <transformAroundRotationCenter value="1" type="value"/>
    <aX value="0" type="value"/>
    <aY value="0" type="value"/>
    <aZ value="0" type="value"/>
    <cameraPos y="40" type="vector3d" z="512" x="40"/>
    <scaleX value="1" type="value"/>
    <scaleY value="1" type="value"/>
    <shearX value="0" type="value"/>
    <shearY value="0" type="value"/>
    <boundsRotation type="value" value="0"/>
    <keepAspectRatio value="0" type="value"/>
    <flattenedPerspectiveTransform type="transform" m31="0" m33="1" m12="0" m13="0" m23="0" m32="0" m21="0" m11="1" m22="1"/>
    <filterId value="Bilinear" type="value"/>
    </free_transform>
    </data>
    </transform_params>
    '''



def replace_fileLayer_old(fileLayer,afterfile):
    # c:¥aaa¥bbb¥ccc.ext  ->  want to get ccc.ext 
    # get path separator for each OS
    # separate from right side , part[-1] = ccc.ext
    fpath = fileLayer.path()
    sep = os.sep
    part=fpath.split(sep)

    fileLayer.setProperties(fileLayer.path().replace(part[-1],afterfile),'None','Bicubic')
    #fileLayer.setProperties(fileLayer.path().replace(dummyfile,afterfile),'None','Bicubic')
    fileLayer.resetCache()


def replace_fileLayer(fileLayer, afterfile):
    # Standardize path for both OS
    fpath = fileLayer.path()
    if platform.system() == "Windows":
        fpath = fpath.replace('\\', '/')
    
    # Split by '/' to get the filename regardless of os.sep
    parts = fpath.split('/')
    old_filename = parts[-1]

    # Reconstruct path and apply properties
    new_path = fpath.replace(old_filename, afterfile)
    
    fileLayer.setProperties(new_path, 'None', 'Bicubic')
    fileLayer.resetCache()




# ========================
# Debug
# ========================

def pos_move(targ_layer,v0,v1):
    targ_layer.move(v0,v1)


def pos_children(targ_layer, tx, ty, newDoc):
    """
    Moves all child nodes to the target position (tx, ty) based on their original offsets.
    """
    if not targ_layer:
        return

    children = targ_layer.childNodes()
    for child in children:
        # Correct Krita API: Use position() to get a QPoint object
        original_pos = child.position()
        ox = original_pos.x()
        oy = original_pos.y()
        
        # Move child to: Target position + Original offset
        child.move(tx + ox, ty + oy)

def get_tr_xy(xml):
    xy = [0,0]
    m=re.search(r'(?=transformedCenter).+(x="(\d+)")',xml)
    if m != None:xy[0]=int(m.group(2))
    m=re.search(r'(?=transformedCenter).+(y="(\d+)")',xml)
    if m != None:xy[1]=int(m.group(2))
    return xy

def rep_tr_xml(b_xml,a_xml):
    m=re.search(r'(?=transformedCenter)(.*?)(?=keepAspectRatio)',b_xml,re.S)
    if m == None:return a_xml
    rep = m.group()
    n=re.search(r'(?=transformedCenter)(.*?)(?=keepAspectRatio)',a_xml,re.S)
    trg = n.group()
    
    dist=a_xml.replace(trg,rep)
    return dist

def checkbox_toggle(s):
    if QC.CheckState.Checked == s:
        c_dlg.label8.setText("Checked")
    else:
        c_dlg.label8.setText("NotChecked.")


def combo_box_changed(cbox):
    # cbox = index of selected item
    c_dlg.texbox1.setText(pmenu[cbox][1])
    c_dlg.texbox2.setText(pmenu[cbox][2])

def rad_clicked(s):
    rad = s.sender()


def ui_composite():
    # create dialog
    dlg = QDialog()
    dlg.setWindowTitle(dialog_title_txt)

    # ========================
    # GUI Settings 
    # ========================
    label1 = QLabel("Document Width(px)")
    dlg.texbox1 = QLineEdit(str(docx))
    dlg.texbox1.resize(40, 20)

    label2 = QLabel("Document Height(px)")
    dlg.texbox2 = QLineEdit(str(docy))
    dlg.texbox2.resize(40, 20)

    label3 = QLabel("Padding W(px)")
    dlg.texbox3 = QLineEdit(str(padx))
    dlg.texbox3.resize(40, 20)

    label4 = QLabel("Padding H(px)")
    dlg.texbox4 = QLineEdit(str(pady))

    label5 = QLabel("Base X(px)")
    dlg.texbox5 = QLineEdit(str(dx))

    label6 = QLabel("Base Y(px)")
    dlg.texbox6 = QLineEdit(str(dy))

    label7 = QLabel("Max number of placed per row")
    dlg.texbox7 = QLineEdit(str(maxcol))

    dlg.label8 = QLabel(" ")
    dlg.chkbox = QCheckBox("Override by layout size,if document size smaller")

    label9 = QLabel("Preset")
    label10 = QLabel("This dpi is rough indication.\n Template's resolution apply to a generated image")

    dlg.pbox = QComboBox()

    label11 = QLabel("Placements per page (0=ALL)")
    dlg.texbox11 = QLineEdit(str(umax))

    label12 = QLabel("Place algorithm for")

    dlg.rg = QButtonGroup(dlg)
    dlg.rad1 = QRadioButton("Moveable")
    dlg.rad2 = QRadioButton("Editable")
    dlg.rad1.setChecked(True)

    mode = 0  # place algorithm
    dlg.rg.addButton(dlg.rad1, 0)
    dlg.rg.addButton(dlg.rad2, 1)

    dlg.chkbox2 = QCheckBox("Group renamer by the tag")
    dlg.texbox12 = QLineEdit(str(rename_tag))

    # ========================
    # Layouts
    # ========================
    vbox = QVBoxLayout()
    hbox1 = QHBoxLayout()
    hbox2 = QHBoxLayout()
    hbox3 = QHBoxLayout()
    hbox4 = QHBoxLayout()
    hbox5 = QHBoxLayout()
    hbox6 = QHBoxLayout()
    hbox7 = QHBoxLayout()
    hbox8 = QHBoxLayout()
    hb_chk = QHBoxLayout()
    hb_cbx = QHBoxLayout()
    hb_mes = QHBoxLayout()
    hb_rad = QHBoxLayout()
    hb_chk2 = QHBoxLayout()
    hb_hline = QHBoxLayout()
    hb2_hline = QHBoxLayout()

    # file select button
    fileButton = QPushButton("Select CSV file")
    fileButton.clicked.connect(opendialog)

    # radio buttons
    hb_rad.addWidget(label12)
    hb_rad.addWidget(dlg.rad1)
    hb_rad.addWidget(dlg.rad2)

    # row 1
    hbox1.addWidget(label1)
    hbox1.addWidget(dlg.texbox1)

    # row 2
    hbox2.addWidget(label2)
    hbox2.addWidget(dlg.texbox2)

    # row 3
    hbox3.addWidget(label3)
    hbox3.addWidget(dlg.texbox3)

    # row 4
    hbox4.addWidget(label4)
    hbox4.addWidget(dlg.texbox4)

    # row 5
    hbox5.addWidget(label5)
    hbox5.addWidget(dlg.texbox5)

    # row 6
    hbox6.addWidget(label6)
    hbox6.addWidget(dlg.texbox6)

    # row 7
    hbox7.addWidget(label7)
    hbox7.addWidget(dlg.texbox7)

    # row 8
    hbox8.addWidget(label11)
    hbox8.addWidget(dlg.texbox11)

    # checkbox row
    hb_chk.addWidget(dlg.chkbox)
    # chkbox.stateChanged.connect(checkbox_toggle)  # if you have this handler

    # combobox settings
    l = 0
    for pm in pmenu:
        if pm[0] == '---':
            dlg.pbox.insertSeparator(l)
            l += 1
            continue
        dlg.pbox.addItem(pm[0])
        l += 1
    # By writing [int] you force to receive a "number" instead of a string
    dlg.pbox.currentIndexChanged[int].connect(combo_box_changed)

    hb_cbx.addWidget(label9)
    hb_cbx.addWidget(dlg.pbox)
    hb_mes.addWidget(label10)

    # second checkbox row
    hb_chk2.addWidget(dlg.chkbox2)
    hb_chk2.addWidget(dlg.texbox12)

    # horizontal lines
    hl = QFrame()
    hl.setFrameShape(QC.Shape.HLine)
    hl.setFrameShadow(QC.Shadow.Sunken)

    hl2 = QFrame()
    hl2.setFrameShape(QC.Shape.HLine)
    hl2.setFrameShadow(QC.Shadow.Sunken)

    hb_hline.addWidget(hl)
    hb2_hline.addWidget(hl2)

    # compose main layout
    vbox.addLayout(hb_cbx)
    vbox.addLayout(hbox1)
    vbox.addLayout(hbox2)
    vbox.addLayout(hb_chk)
    vbox.addLayout(hb_mes)
    vbox.addLayout(hb_hline)
    vbox.addLayout(hbox3)
    vbox.addLayout(hbox4)
    vbox.addLayout(hbox5)
    vbox.addLayout(hbox6)
    vbox.addLayout(hb2_hline)
    vbox.addLayout(hbox7)
    vbox.addLayout(hbox8)
    vbox.addLayout(hb_rad)
    vbox.addLayout(hb_chk2)
    vbox.addWidget(fileButton)

    dlg.setLayout(vbox)
    global c_dlg
    c_dlg = dlg
    qt_exec(dlg)

class DataMergeGenerator(Extension):

    def __init__(self, parent):
        super(DataMergeGenerator,self).__init__(parent)

    # Krita.instance() exists, so do any setup work
    def setup(self):
        pass

    # called after setup(self)
    def createActions(self, window):
        self.action = window.createAction(plugin_id, plugin_menu_entry_name ,plugin_where)
        self.action.triggered.connect(ui_composite)



# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(DataMergeGenerator(Krita.instance()))
