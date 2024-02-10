# ===============================================
# Data Merge Generator v1.54 for Krita 
# ===============================================
# Copyright (C) 2024 L.Sumireneko.M
# This program is free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>. 



# This script is work SIMPLE data combine similar as ..Data-Merge,MailMerge
from krita import *
from PyQt5.QtWidgets import QDialog,QHBoxLayout,QVBoxLayout,QPushButton,QLabel,QLineEdit,QFileDialog,QComboBox,QMessageBox
from PyQt5.QtCore import *
from PyQt5.QtGui import QGuiApplication,QClipboard
import re,os,time

# ========================
# Settings
# ========================
from .setting import *


# ========================
# GUI Settings
# ========================
label1= QLabel("Document Width(px)")
texbox1 = QLineEdit(str(docx))
texbox1.resize(40, 20)

label2= QLabel("Document Height(px)")
texbox2 = QLineEdit(str(docy))
texbox2.resize(40, 20)

label3= QLabel("Padding W(px)")
texbox3 = QLineEdit(str(padx))
texbox3.resize(40, 20)

label4= QLabel("Padding H(px)")
texbox4 = QLineEdit(str(pady))

label5= QLabel("Base X(px)")
texbox5 = QLineEdit(str(dx))

label6= QLabel("Base Y(px)")
texbox6 = QLineEdit(str(dy))


label7= QLabel("Max number of placed per row")
texbox7 = QLineEdit(str(maxcol))

label8= QLabel(" ")
chkbox = QCheckBox("Override by layout size,if document size smaller")

label9= QLabel("Preset")
label10= QLabel("This dpi is rough indication.\n Template's resolution apply to a generated image")

pbox = QComboBox()
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
label11= QLabel("Placements per page (0=ALL)")
texbox11 = QLineEdit(str(umax))

newDialog = QDialog()

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
    if file.open(QIODevice.ReadOnly):
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


def opendialog():
    global docx,docy,padx,pady,dx,dy,maxcol,umax
    print('Button clicked!!')
    docx = get_param(texbox1.text())
    docy = get_param(texbox2.text())
    padx = get_param(texbox3.text())
    pady = get_param(texbox4.text())
    dx = get_param(texbox5.text())
    dy = get_param(texbox6.text())
    maxcol = get_param(texbox7.text())
    umax = get_param(texbox11.text())
    
    print("---- Read Parameters ----")
    file = QFileDialog.getOpenFileName(None,'Open CSV File',os.path.expanduser('~' + '/Desktop'), filter = 'CSV or TXT (*.csv *.txt)')
    # file = ('file path',' extension filter')
    # print(file,file[0]) ,docx,docy,padx,pady,dx,dy,maxcol
    
    if file[0] == '':print('No select to file for open');return
    print('Select file:'+file[0])
    csv_path = file[0]

    st = time.time()
    tim_info('Start ',st)
    
    krita_instance = Krita.instance()
    currentDoc = krita_instance.activeDocument()
    res = currentDoc.resolution()

    # Read csv data file
    data = read_file(csv_path)
    list = data.split(line_break) # detect line break
    
    # find Template Layer
    templ = currentDoc.nodeByName("Template")
    tw,th = templ.bounds().width(),templ.bounds().height()
    currentDoc.setActiveNode(templ)
    krita_instance.action('copy_layer_clipboard').trigger()

    # create new document 
    # createDocument(width, height, name, colorSpace, bitDepth, colorProfile, dpi)
    
    max_width = dx*2+(maxcol*(tw+padx))
    maxrow = (len(list)+maxcol) // maxcol
    max_height = dy*2+(maxrow*(th+pady))
    
    up_row = (umax+maxcol) // maxcol
    up_height = dy*2+(up_row*(th+pady))
    
    if QtCore.Qt.Checked == chkbox.checkState():
        if docx < max_width: docx = max_width
        if docy < max_height:
            if umax > 0:max_height = up_height
            docy = max_height

    print('------ Replace Start ------')

    regloop(list,res,st)
    tim_info('Finished ',st)

    print('------ Finished ------')
    tim_info('Remove_temp layer ',st)
    newDialog.close()


# Main loop
def regloop(list,res,st):
    global docx,docy,padx,pady,dx,dy,maxcol,umax
    
    document_name = 'NewDocument'
    pdx,idx = 0,0
    page = 0
    
    tags = []
    tags = list.pop(0).split(splitter)

    krita_instance = Krita.instance()
    krita_inscance_activedoc = krita_instance.activeDocument()
    krita_inscance_activedoc_createVectorLayer = krita_inscance_activedoc.createVectorLayer
    krita_inscance_activedoc_createTransformMask = krita_inscance_activedoc.createTransformMask

    newDoc = krita_instance.createDocument(docx, docy, document_name, "RGBA", "U8", "", res)
    krita_instance.activeWindow().addView(newDoc) # Add New window
    print(f'Resolution Setting: {res} ppi')

    krita_instance.action('paste_layer_from_clipboard').trigger()
    newDoc.refreshProjection()
    base = newDoc.rootNode()
    
    temp_origin_layer = newDoc.nodeByName('Template')
    b=temp_origin_layer.bounds()
    w,h = b.width(),b.height()
    
    row,col = 0,0
    up_max = umax
    for itm in list:
    
        if up_max > 0 and idx > 0 and idx % up_max == 0:
            # Add new document
            page += 1
            newDoc.nodeByName("Template").remove()
            newDoc = krita_instance.createDocument(docx,docy, f'{document_name}{page}', "RGBA", "U8", "", res)
            krita_instance.activeWindow().addView(newDoc) # shows it in the application
            krita_instance.action('paste_layer_from_clipboard').trigger()
            newDoc.refreshProjection()
            base = newDoc.rootNode()
            temp_origin_layer = newDoc.nodeByName('Template')
            b=temp_origin_layer.bounds()
            w,h = b.width(),b.height()
            pdx,row,col = 0,0,0

        prts = itm.split(splitter) # splitter in data file

        # Copy template Layer and duplicate it
        newname = f'New{idx}'
        
        # if idx > 2: continue # debug for revert
        got_activeLayer = temp_origin_layer.duplicate()
        got_activeLayer_findChildNodes = got_activeLayer.findChildNodes
        got_activeLayer_addChildNode = got_activeLayer.addChildNode
        got_activeLayer.setName(newname)
        base.addChildNode( got_activeLayer, None )

        # These nodes are remove when replace finished after
        text_layers = get_vector_node_from_group(got_activeLayer)
        file_layers = get_file_node_from_group(got_activeLayer)
        
        print(f'------ Group Layer Output : {newname}------')
        tim_info('List:',st)
        # Check nodes  from template copyed layers,and extract only text layer
        
        if image_mode:
            for node in file_layers:
                mat,rdx = 0,0
                ntype = node.type()
                #if rdx == 0: tim_info(f'Replace start: {ntype}',st)
                for i in range(len(prts)):
                     # if tag contain image layer tag %%
                     if tags[i].startswith(img_layr_tag):
                         ichk=[];ichk= got_activeLayer_findChildNodes(tags[i])
                         if len(ichk) : replace_fileLayer(ichk[0],prts[i]) # Image filename Replace
        
        for node in text_layers:
            mat,rdx = 0,0
            ntype = node.type()
            
            if ntype== 'vectorlayer': svgdata = node.toSvg()
            #if rdx == 0: tim_info(f'Replace start: {ntype}',st)
            
            for rd in prts:
                # skip file Layer tag
                if tags[rdx].startswith(img_layr_tag) and image_mode: rdx += 1; continue

                pat = f'{lt}{tags[rdx]}{gt}'
                #print(pat)
                
                if (re.search(pat,svgdata)):
                    mat += 1
                    #print( f'Success:{mat}'  )
                    svgdata = svgdata.replace(pat,rd) # match and replace
                    #print(f'RegNo.{pat} , replace to {rd} ,in list:{idx}')
                rdx += 1
            # Loop End
            if mat > 0:
                vnode = krita_inscance_activedoc_createVectorLayer('vector')
                vnode.addShapesFromSvg(svgdata)
                got_activeLayer_addChildNode( vnode , None )

        # Loop End

        # Layout
        col = pdx % maxcol # 0123401234...
        row = 0 if pdx == 0 else pdx // maxcol
        #row = row if page == 0 else (idx-(up_max*(page-1))) // maxcol
        
        tim_info(f'\nFinished all replace:',st)
        # remove original nodes
        for n in text_layers:
            n.remove()
        tim_info('Remove text_layers:',st)
        # Position set
        tx,ty = dx+(col*(w+padx)), dy+(row*(h+pady))
        new_layout = krita_inscance_activedoc_createTransformMask(f'Layout{idx}')
        new_layout.fromXML(transform_exe(tx,ty))
        got_activeLayer_addChildNode(new_layout,None)
        tim_info('Finish position set:',st)
        idx += 1
        pdx += 1
        # Loop End
    
    newDoc.nodeByName("Template").remove()

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
    <keepAspectRatio value="0" type="value"/>
    <flattenedPerspectiveTransform type="transform" m31="0" m33="1" m12="0" m13="0" m23="0" m32="0" m21="0" m11="1" m22="1"/>
    <filterId value="Bilinear" type="value"/>
    </free_transform>
    </data>
    </transform_params>
    '''

def replace_fileLayer(fileLayer,afterfile):
    # c:¥aaa¥bbb¥ccc.ext  ->  want to get ccc.ext
    # get path separator for each OS
    # separate from right side , part[-1] = ccc.ext
    fpath = fileLayer.path()
    sep = os.sep
    part=fpath.split(sep)

    fileLayer.setProperties(fileLayer.path().replace(part[-1],afterfile),'None','Bicubic')
    #fileLayer.setProperties(fileLayer.path().replace(dummyfile,afterfile),'None','Bicubic')
    fileLayer.resetCache()

# ========================
# Debug
# ========================


def checkbox_toggle(s):
    if QtCore.Qt.Checked == s:
        label8.setText("Checked")
    else:
        label8.setText("NotChecked.")

def combo_box_changed(cbox):
    # cbox = index of selected item
    texbox1.setText(pmenu[cbox][1])
    texbox2.setText(pmenu[cbox][2])


# ========================
# GUI
# ========================
# add button and layout for button
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
fileButton = QPushButton("Select CSV file")
fileButton.clicked.connect(opendialog)

hbox1.addWidget(label1)
hbox1.addWidget(texbox1)

hbox2.addWidget(label2)
hbox2.addWidget(texbox2)

hbox3.addWidget(label3)
hbox3.addWidget(texbox3)

hbox4.addWidget(label4)
hbox4.addWidget(texbox4)

hbox5.addWidget(label5)
hbox5.addWidget(texbox5)

hbox6.addWidget(label6)
hbox6.addWidget(texbox6)

hbox7.addWidget(label7)
hbox7.addWidget(texbox7)

hbox8.addWidget(label11)
hbox8.addWidget(texbox11)

hb_chk.addWidget(chkbox)
#hbox8.addWidget(label8)
#chkbox.stateChanged.connect(checkbox_toggle)

# Combo box setting
l = 0
for itm in pmenu:
    if itm[0]=='---': pbox.insertSeparator(l);l+=1;continue
    pbox.addItem(itm[0]);l+=1
pbox.currentIndexChanged.connect(combo_box_changed)

hb_cbx.addWidget(label9)
hb_cbx.addWidget(pbox)
hb_mes.addWidget(label10)

vbox.addLayout(hb_cbx)
vbox.addLayout(hbox1)
vbox.addLayout(hbox2)
vbox.addLayout(hb_chk)
vbox.addLayout(hb_mes)
vbox.addLayout(hbox3)
vbox.addLayout(hbox4)
vbox.addLayout(hbox5)
vbox.addLayout(hbox6)
vbox.addLayout(hbox7)
vbox.addLayout(hbox8)
vbox.addWidget(fileButton)

def init_main():
    # create dialog  and show it
    newDialog.setLayout(vbox)
    newDialog.setWindowTitle("Replace text with data merge insertion") 
    newDialog.exec_() # show the dialog

plugin_id = "data_merge"
plugin_menu_entry_name = "Data Merge..."
plugin_where = "tools/scripts"

class DataMergeGenerator(Extension):

    def __init__(self, parent):
        super(DataMergeGenerator,self).__init__(parent)

    # Krita.instance() exists, so do any setup work
    def setup(self):
        pass

    # called after setup(self)
    def createActions(self, window):
        self.action = window.createAction(plugin_id, plugin_menu_entry_name ,plugin_where)
        self.action.triggered.connect(init_main)


