from .data_merge_gen import DataMergeGenerator

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(DataMergeGenerator(Krita.instance()))

