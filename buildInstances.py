import os
from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor, InstanceDescriptor, AxisDescriptor
from mutatorMath.ufo.document import DesignSpaceDocumentWriter, DesignSpaceDocumentReader

def buildDesignSpace(sources, instances, axes):
    doc = DesignSpaceDocument()
    # build source descriptors from source list
    for source in sources:
        s = SourceDescriptor()
        s.path = source["path"]
        s.name = source["name"]
        s.copyInfo = source["copyInfo"]
        s.location = source["location"]
        s.familyName = source["familyName"]
        s.styleName = source["styleName"]
        doc.addSource(s)
    # build instance descriptors from instance list
    for instance in instances:
        i = InstanceDescriptor()
        i.location = instance["location"]
        i.familyName = instance["familyName"]
        i.styleName = instance["styleName"]
        i.path = instance["path"]
        i.postScriptFontName = instance["postScriptFontName"]
        i.styleMapFamilyName = instance["styleMapFamilyName"]
        i.styleMapStyleName = instance["styleMapStyleName"]
        doc.addInstance(i)
    # build axis descriptors from axis list
    for axis in axes:
        a = AxisDescriptor()
        a.minimum = axis["minimum"]
        a.maximum = axis["maximum"]
        a.default = axis["default"]
        a.name = axis["name"]
        a.tag = axis["tag"]
        for languageCode, labelName in axis["labelNames"].items():
            a.labelNames[languageCode] = labelName
        a.map = axis["map"]
        doc.addAxis(a)
    return doc
    
# set values for family

familyName = 'Adsworth'

labels = {
    'opsz': {"en": "Optical Size"},
    'GRAD': {"en": "Grade"},
    'XTRA': {"en": "X Transparent"}
    }

namesToValues = {
    'opsz': {
        '8PT': 8,
        '24PT': 24,
        '72PT': 72
        },
    'GRAD': {
        'G0': 20,
        'G': 80,
        'G1': 240
        },
    'XTRA': {
        'XT0': 220,
        'XT': 450,
        'XT1': 635
        }
    }

# build axis list
axes = []
for axisName in ['opsz', 'GRAD', 'XTRA']:
    axisValueList = namesToValues[axisName].values()
    axisValueList.sort()
    minimum = axisValueList[0]
    maximum = axisValueList[1]
    default = axisValueList[2]
    
    axes.append(
        dict(minimum=minimum, maximum=maximum, default=default, name=axisName, tag=axisName, labelNames=labels[axisName], map=[])
        )

# build sources list (this I did manually)
sources = [
    dict(path="Sources/Adsworth-XTRAmax.ufo", name="Adsworth-XTRAmax.ufo", location=dict(opsz=24, GRAD=80, XTRA=635), styleName="XTRAmax", familyName=familyName, copyInfo=False),
    dict(path="Sources/Adsworth-XTRAmin.ufo", name="Adsworth-XTRAmin.ufo", location=dict(opsz=24, GRAD=80, XTRA=220), styleName="XTRAmin", familyName=familyName, copyInfo=False),
    dict(path="Sources/Adsworth-Regular.ufo", name="Adsworth-Regular.ufo", location=dict(opsz=24, GRAD=80, XTRA=450), styleName="Regular", familyName=familyName, copyInfo=True),
    dict(path="Sources/Adsworth-GRADmin.ufo", name="Adsworth-GRADmin.ufo", location=dict(opsz=24, GRAD=20, XTRA=450), styleName="GRADmin", familyName=familyName, copyInfo=False),
    dict(path="Sources/Adsworth-GRADmax.ufo", name="Adsworth-GRADmax.ufo", location=dict(opsz=24, GRAD=240, XTRA=450), styleName="GRADmax", familyName=familyName, copyInfo=False),
    dict(path="Sources/Adsworth-opszmax.ufo", name="Adsworth-opszmax.ufo", location=dict(opsz=72, GRAD=80, XTRA=450), styleName="opszmax", familyName=familyName, copyInfo=False),
    dict(path="Sources/Adsworth-opszmin.ufo", name="Adsworth-opszmin.ufo", location=dict(opsz=8, GRAD=80, XTRA=450), styleName="opszmin", familyName=familyName, copyInfo=False)
    ]

# build instances by looping through all 27 permutations

styleMapStyleName = 'regular'
instances = []
for opszName in sorted(namesToValues['opsz'].keys()):
    for GRADName in sorted(namesToValues['GRAD'].keys()):
        for XTRAName in sorted(namesToValues['XTRA'].keys()):
            opszValue = namesToValues['opsz'][opszName]
            GRADValue = namesToValues['GRAD'][GRADName]
            XTRAValue = namesToValues['XTRA'][XTRAName]
            instances.append(                
                dict(
                    path="instances/%s-%s %s %s.ufo" %(familyName, opszName, GRADName, XTRAName),  
                    location={
                        'opsz': opszValue, 
                        'GRAD': GRADValue, 
                        'XTRA': XTRAValue
                    },   
                    styleName="%s %s %s" %(opszName, GRADName, XTRAName),  
                    familyName=familyName, 
                    postScriptFontName=familyName+"-%s%s%s" %(opszName, GRADName, XTRAName),  
                    styleMapFamilyName=familyName+' %s %s %s' %(opszName, GRADName, XTRAName),  
                    styleMapStyleName=styleMapStyleName
                    ),
                )

# build and write fresh designspace file
dsDoc = buildDesignSpace(sources, instances, axes)
dsPath = os.path.join( os.path.split(__file__)[0], '%s_makeInstances.designspace' %familyName)
dsDoc.write(dsPath)

# now use Mutator math to build the designspace into instances
doc = DesignSpaceDocumentReader(dsPath, ufoVersion=3)
print(doc.sources)
doc.process(makeGlyphs=True, makeKerning=True, makeInfo=True)
print('done')
