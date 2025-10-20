# Data Merge Generator v1.7 for Krita 

This plugin working simple version of Data Merge.
(v1.7) Support Krita v5.2.14 later (PyQt5 with Python 3.13)
(v1.6) Support Krita v5.2.2

### What is Data Merge?
Arrange them in order according to the contents of the database (csv) based on the prepared template krita file. For example, it can be useful for printing number tags, equipment tags, and employee business cards.

There are exist many systems for example ,Adobe InDesign's feature,LibreOffice MailMerge,[Scribus Generator](https://berteh.github.io/ScribusGenerator/)  ,[Inkscape NextGenerator](https://gitlab.com/Moini/nextgenerator) 
Also,this plugin inspired from the script "[Improved version of Data Join](http://indesigner.blog101.fc2.com/blog-entry-230.html
)"  for Adobe Illustrator.Thank you very much.

## Ussage
See [Usage Manual](https://sumireneko.github.io/data_merge/data_merge_gen/Manual.html)

### Note and Disclaimer
* This plugin is experimental. It is not suitable for large amounts of data.
* Please try it with a small amount of data first.
* It is slow as the number of items and pixel resolution increases.
* Loading and editing kra file with many linked images will be slowly.
So,it can also specify the max number of units to be placed per each export image file.
* Layer styles in template files are not supported.


##How to install a python plugin to krita
1. Run Krita application,
2. From `Menu → Setting → Manage Resources`
3. Click `Open Resource Folder` Button
4. Find `pykrita` folder (Explorer or Finder)
5. Copy `data_merge_gen`folder and `data_merge_gen.desktop` into `pykrita`
6. ReLunch Krita,and open `Preferences dialog  → Select  Python Plugin Manager` list.
7. For enable this plugin,find and click the Checkbox of `Data Maneger Generator`(This plugin) from the plugin list.

Note:
In Step7,Select plugin name in the list,you can read built-in Manual.
Also error message indicate with mouse hover tool-tip on the list when this plug-in load failed.

See also [this article](https://docs.krita.org/en/user_manual/python_scripting/install_custom_python_plugin.html) in Krita wiki.

### Uninstall
* Remove `data_merge_gen`folder and `data_merge_gen.desktop` from `pykrita` folder


## How to work this plug-in
* Users need to prepare customized kra and csv files.

### Preparation
1. Create a CSV file (.csv,.txt) The 1st line define for Tag keyword list,charactor code:UTF-8) and list...
2. Create a Krita's image file (.kra) - Need one `GroupLayer` that named `Template`,Some `FileLayers` that named%%Tag%%,and `VectorLayer` that for replace `&lt;&lt;Tag&gt;&gt;s embed in text object)

### Run
1. Open the Template .kra file
2. Run on Krita (from `Tools → Scripts →Data Merge...`)
3. Setting (Optional)
4. Select the CSV file

## Place algorithms (v1.6)
In each mode, prefix added to GroupLayer's name,For example "E:New0","M:New2" and the TransformMasks for fix positon. 
These prefix M,E means Moveable and Editable.The number mean index.
* Moveable  : Add Transform to GroupLayer(Template). So all editable positions are shift by TransformMask.(Default)
* Editable  : Add Transform to TransformMask, So normal layers editable position match. 

## Group renamer by tag (v1.6)
If it chcked and the specified tag name matched,that text will be exported as the grouplayer's name from csv data.
For example "E:3 CardTitleString", M:6 person_name,The number mean index.
If not match the tag and data, use default name "New" use to.

## Version history
* 2025.10.18 v1.7 : Support two place algorithms that Moveable and Editable, Add GroupLayerRenamer
 - Some bugfix, because this script doesn't work in Krita v5.2.14(PyQT5 with Python 3.13)
 - Changed use an cloned layer node instead of copy paste action to new document.
 - In Editable mode,fix unusual coordinates that has minus position in some case.
 - Preliminary PyQt6 compatibility added Updated import logic to support PyQt6 for future Krita 6.x compatibility.
 - Note: PyQt6 functionality has not been tested yet. This change is preparatory and not guaranteed to be stable.

* 2024.02.17 v1.6 : Support two place algorithms that Moveable and Editable, Add GroupLayerRenamer
* 202X.??.?? v1.5.4 : fist release, Place to multiple kra file by page

