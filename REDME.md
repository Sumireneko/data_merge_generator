# Data Merge Generator v1.54 for Krita 

This plugin working simple version of Data Merge.
Require Krita v5.2.2 later

### What is Data Merge?
Arrange them in order according to the contents of the database (csv) based on the prepared template krita file. For example, it can be useful for printing number tags, equipment tags, and employee business cards.

There are exist many systems for example ,Adobe InDesign's feature,LibreOffice MailMerge,[Scribus Generator](https://berteh.github.io/ScribusGenerator/)  ,[Inkscape NextGenerator](https://gitlab.com/Moini/nextgenerator) 
Also,this plugin inspired from the script "[Improved version of Data Join](http://indesigner.blog101.fc2.com/blog-entry-230.html
)"  for Adobe Illustrator.Thank you very much.

## Ussage
See [Usage Manual](./Manual.html)

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



