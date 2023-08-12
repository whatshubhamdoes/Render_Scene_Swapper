import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.mel as mel
import os
import sys
import json

def getCurrentRenderer():
    return cmds.getAttr('defaultRenderGlobals.currentRenderer')


def getCurrentRenderAttributes():  
    render_settings_node = "defaultRenderGlobals" 
    attributes = cmds.listAttr(render_settings_node)
    for attr in attributes:        
        attr_type = cmds.getAttr(render_settings_node + '.' + attr, type=True)
        if attr_type == 'message':
            continue
            
        print("Attribute Name:", attr)
        value = cmds.getAttr(render_settings_node + '.' + attr)
        print("Attribute Value:", value)

def setRenderer(from_index):
    renderers = ["arnold", "renderman", "vray"]
    if 0 <= from_index < len(renderers):
        cmds.setAttr("defaultRenderGlobals.currentRenderer", renderers[from_index], type="string")
    else:
        print("Not able to change renderer")

def checkCurrentRenderer(currentRenderer,anyDictionaryAddress):
    with open(anyDictionaryAddress,'r') as file :
        data=json.load(file)
        try:
            for rendererInfo in data["Lights"]["renderer"]:
                if currentRenderer in rendererInfo:
                    return ("Renderer Supported")
        except:
            for rendererInfo in data["Materials"]["renderer"]:
                if currentRenderer in rendererInfo:
                    return ("Renderer Supported")

def assignNumber(currentRenderer):
    renderer_map = {"arnold": 0, "renderman": 1, "vray": 2}
    return renderer_map.get(currentRenderer, False)


def createLightComponentMap(components_light_map,lightsData,light_type,number):
    for light in lightsData["Lights"]:
        if light != "renderer":
            for key,value in lightsData["Lights"][light_type].items():
                if key in ["attribute_intensity","attribute_color","attribute_exposure"]:
                    components_light_map[key]=value[number]

def createMaterialComponentMap(components_material_map,materialsData,material_type,number):
    for material in materialsData["Materials"]:
        if material != "renderer":
            for key,value in materialsData["Materials"][material_type].items():
                if key in ["attribute_base", "attribute_diffuse_color", "attribute_metalness", "attribute_specular", "attribute_specular_color", "attribute_specular_roughness", "attribute_transmission", "attribute_transmission_color", "attribute_subsurface", "attribute_subsurface_color", "attribute_subsurface_radius", "attribute_subsurface_scale", "attribute_subsurface_anisotropy", "attribute_coat", "attribute_coat_color", "attribute_coat_roughness", "attribute_coat_anisotropy", "attribute_sheen", "attribute_sheen_color", "attribute_sheen_roughness", "attribute_emission", "attribute_emission_color", "attribute_normal_map"]:
                    components_material_map[key]= value[number]


def copyLightAttributes(light,lightsData,light_type,number,convNumber):
    convLight=lightsData["Lights"][light_type]["name"][convNumber]
    print(convLight)
    conv=lightsData["Lights"][light_type]["renderer"][convNumber]
    convLight=cmds.shadingNode(f"{convLight}",asLight=True,name=f"{light}_{conv}")
    
    components_light_map={}
    createLightComponentMap(components_light_map,lightsData,light_type,number)
    print(components_light_map)

    components_convLight_map={}
    createLightComponentMap(components_convLight_map,lightsData,light_type,convNumber)
    print(components_convLight_map)

    for attr,convAttr in zip(components_light_map.values(),components_convLight_map.values()):
        try:
            value=cmds.getAttr(light+'.'+attr)
            print(value)
            file_node=cmds.connectionInfo(light + '.'+ attr, sourceFromDestination=True)
            print(file_node)
            file_node=''.join(file_node)
            try:
                print("inside file node")
                if convNumber==1:
                    if number==0:
                        print("Coming in arnold to renderman_file_node")
                        file_path=cmds.listConnections(light + '.'+ attr,type='file')
                        file_path=''.join(file_path)
                        file_path=cmds.getAttr("%s.fileTextureName" % file_path)
                        print(file_path)
                        cmds.setAttr(convLight+'.'+convAttr,file_path,type='string')
                    else:
                        print("Coming in vray to renderman_file_node")
                        file_path=cmds.listConnections(light + '.'+ attr,type='file')
                        file_path=''.join(file_path)
                        file_path=cmds.getAttr("%s.fileTextureName" % file_path)
                        print(file_path)
                        cmds.setAttr(convLight+'.'+convAttr,file_path,type='string')

                if convNumber==2:
                    if number == 0:
                        print("Coming in arnold to vray_file_node")
                        file_path=cmds.listConnections(light + '.'+ attr,type='file')
                        file_path=''.join(file_path)
                        print(file_path)
                        cmds.setAttr(convLight+'.useDomeTex',1)
                        cmds.connectAttr(file_path+'.outColor',convLight+'.'+convAttr)
                    else:
                        print("Coming in renderman to vray_file_node")
                        cmds.setAttr(convLight+'.useDomeTex',1)
                        new_file_node=cmds.shadingNode('file',asTexture=True)
                        cmds.setAttr(new_file_node+'.fileTextureName',value,type='string')
                        cmds.connectAttr(new_file_node+'.outColor',convLight+'.'+convAttr)     

                if convNumber==0:
                    print("To arnold")
                    if number == 2:
                        print("Coming in vray to arnold")
                        file_path=cmds.listConnections(light + '.'+ attr,type='file')
                        file_path=''.join(file_path)
                        cmds.connectAttr(file_path+'.outColor',convLight+'.'+convAttr)
                    else:
                        print("Coming in renderman to arnold")
                        new_file_node=cmds.shadingNode('file',asTexture=True)
                        print("created new node")
                        cmds.setAttr(new_file_node+'.fileTextureName',value,type='string')
                        cmds.connectAttr(new_file_node+'.outColor',convLight+'.'+convAttr)     
            
            except:
                try:
                    try:
                        cmds.setAttr(convLight+'.'+convAttr,value)
                    except:
                        cmds.setAttr(convLight+'.'+convAttr,value[0][0],value[0][1],value[0][2],type='double3')
                    finally:
                        pass
                except:            
                    if '' in attr.lower():
                        continue
        
        except:
            if '' in attr.lower():
                continue
        
        
    
    lightTransform=cmds.listRelatives(light,parent=True,shapes=True,fullPath=True)
    cmds.matchTransform(f"{convLight}", lightTransform)
    lightSet=cmds.listRelatives(lightTransform,parent=True,fullPath=True)
    if lightSet:
        cmds.parent(f"{convLight}", lightSet)    

def copyMaterialAttributes(mat, materialsData, material_type, number, convNumber):
    convMaterial = materialsData["Materials"][material_type]["name"][convNumber]
    print("First Conv Material")
    print(convMaterial)
    conv= materialsData["Materials"][material_type]["renderer"][convNumber]
    convMaterial = cmds.shadingNode(f"{convMaterial}", asShader=True, name=f"{mat}_{conv}")
    print("Second Conv Material")
    print(convMaterial) 
    # Naming wrong of shading group
    convMaterialShadingGroup = cmds.sets(convMaterial, renderable=True, noSurfaceShader=True, empty=True, name=convMaterial + 'SG')
    print("Conv material shading group")
    print(convMaterialShadingGroup)
    cmds.connectAttr(convMaterial + '.outColor', convMaterialShadingGroup + '.surfaceShader', force=True)
    
    components_material_map = {}
    createMaterialComponentMap(components_material_map, materialsData, material_type, number)
    print(components_material_map)
    
    components_convMaterial_map = {}
    createMaterialComponentMap(components_convMaterial_map, materialsData, material_type, convNumber)
    print(components_convMaterial_map)
    
    for attr, convAttr in zip(components_material_map.values(), components_convMaterial_map.values()):
        print("entered for loop")
        try:
            print("attr = " , attr)
            print("convAttr = ", convAttr)
            value=cmds.getAttr(mat+'.'+attr)
            print("value = ",value)
            file_node=cmds.connectionInfo(mat+'.'+attr,sourceFromDestination=True)
            file_node=''.join(file_node)
            print("file_node = ",file_node)
            if "emissionColor" in attr:
                emissiongain=cmds.getAttr(mat+'.emission')
                if emissiongain != 0.0 :
                    print(emissiongain)
                    print("entered emission")
                    if file_node != "":
                        print("entered emission file node")
                        convMaterial=''.join(convMaterial)
                        print("if file_node is true: convMaterial = ", convMaterial)
                        cmds.connectAttr(file_node,convMaterial+'.'+convAttr)
            
                    else:
                        print("entering emission value set")
                        try:
                            try:
                                cmds.setAttr(convMaterial+'.'+convAttr,value)
                                print("Value set 1st try")
                            except:
                                cmds.setAttr(convMaterial+'.'+convAttr,value[0][0],value[0][1],value[0][2],type='double3')
                                print("Value set 2nd try")
                            finally:
                                print("Not Set = ", attr)
                        except:            
                            if '' in convAttr.lower():
                                continue   
                else:
                    continue
            else:
                if file_node != "":
                    convMaterial=''.join(convMaterial)
                    print("if file_node is true: convMaterial = ", convMaterial)
                    cmds.connectAttr(file_node,convMaterial+'.'+convAttr)
        
                else:
                    try:
                        try:
                            cmds.setAttr(convMaterial+'.'+convAttr,value)
                            print("Value set 1st try")
                        except:
                            cmds.setAttr(convMaterial+'.'+convAttr,value[0][0],value[0][1],value[0][2],type='double3')
                            print("Value set 2nd try")
                        finally:
                            print("Done  = ", attr)
                    except:            
                        if '' in convAttr.lower():
                            continue
        except:
            pass
    
    print("before returning conv material shading group = ")
    print(convMaterialShadingGroup)
    return convMaterialShadingGroup

def lightsConversion(convNumber,light_conversion_map,lightDictionaryAddress):
    with open(lightDictionaryAddress,'r') as file :
        lightsData=json.load(file)
    currentRenderer=getCurrentRenderer()    
    number=assignNumber(currentRenderer)
    sel = cmds.ls(sl=True)
    if not sel :
        cmds.confirmDialog(title='Error', message='Please select an object', button=['OK'], defaultButton='OK')
        cmds.warning("Error : Please select an object")
        return

    for obj in sel:
        lights = cmds.ls(sl=True, dag=True, s=True)
        print(lights)
        for light in lights:
            print(light)
            light_type = cmds.nodeType(light)
            print(light_type)
            if light_type in light_conversion_map:
                light_type = light_conversion_map[light_type]
                print(light_type)
                copyLightAttributes(light, lightsData, light_type, number, convNumber)
            else:
                continue

def materialsConversion(convNumber,material_conversion_map,materialDictionaryAddress):
    with open(materialDictionaryAddress,'r') as file :
        materialsData=json.load(file)
    currentRenderer=getCurrentRenderer()    
    number=assignNumber(currentRenderer)
    sel = cmds.ls(sl=True)
    if not sel :
        cmds.confirmDialog(title='Error', message='Please select an object', button=['OK'], defaultButton='OK')
        cmds.warning("Error : Please select an object")
        return

    for obj in sel:
        objects=cmds.ls(sl=True,dag=True,s=True)
        print (objects)
        for object in objects:
            print (object)
            shadeEng=cmds.listConnections(object,type='shadingEngine')
            print(shadeEng)
            if shadeEng :
                for sg in shadeEng :
                    print (sg)
                    material=cmds.ls(cmds.listConnections(sg),materials = True)
                    print(material)
                    for mat in material:
                        material_type=cmds.nodeType(mat)
                        print(material_type)
                        print("check")
                        if material_type in material_conversion_map :
                            print("check2")
                            material_type=material_conversion_map[material_type]
                            print(material_type)
                            print("check3")
                            shading_group= copyMaterialAttributes(mat, materialsData, material_type, number, convNumber)
                            cmds.sets(object,edit=True,forceElement=shading_group)
                        else :
                            if "displacementShader" in material_type:
                                print("mat = ", mat)
                                try:
                                    cmds.connectAttr(mat+'.displacement',shading_group+'.displacementShader')
                                except:
                                    cmds.confirmDialog(title='Error', message='Please check the material of your selected object', button=['OK'], defaultButton='OK')
                                    cmds.warning("Error : Please check the material of your selected object")
                                    return
                            else:
                                continue
                                

def convertLights(fromNumber,convNumber):
    lightDictionaryAddress="/transfer/s5512613_SP/Masters_Project/Render_Scene_Swapper/Dictionary/lights.json"
    with open(lightDictionaryAddress,'r') as file :
        lightsData=json.load(file)
    currentRenderer=getCurrentRenderer()
    print(currentRenderer)
    check1=checkCurrentRenderer(currentRenderer,lightDictionaryAddress)
    light_conversion_map = {
        lightsData["Lights"]["area_light"]["name"][fromNumber]: "area_light",
        lightsData["Lights"]["point_light"]["name"][fromNumber]: "point_light",
        lightsData["Lights"]["directional_light"]["name"][fromNumber]: "directional_light",
        lightsData["Lights"]["spot_light"]["name"][fromNumber]: "spot_light",
        lightsData["Lights"]["skyDome_light"]["name"][fromNumber]: "skyDome_light",
        lightsData["Lights"]["mesh_light"]["name"][fromNumber]: "mesh_light"
    }
    if check1== "Renderer Supported":
        lightsConversion(convNumber,light_conversion_map,lightDictionaryAddress)
    else:
        print("Renderer not supported for conversion")

def convertMaterials(fromNumber,convNumber):
    materialDictionaryAddress="/transfer/s5512613_SP/Masters_Project/Render_Scene_Swapper/Dictionary/materials.json"
    with open(materialDictionaryAddress,'r') as file :
        materialsData=json.load(file)
    currentRenderer=getCurrentRenderer()
    print(currentRenderer)
    check1=checkCurrentRenderer(currentRenderer,materialDictionaryAddress)
    material_conversion_map = {
        materialsData["Materials"]["standard_material"]["name"][fromNumber] : "standard_material",
        materialsData["Materials"]["hair_material"]["name"][fromNumber] : "hair_material"
    }
    if check1== "Renderer Supported":
        materialsConversion(convNumber,material_conversion_map,materialDictionaryAddress)
    else:
        print("Renderer not supported for conversion")

def createUI():
    
    # Function to call the selected conversion function
    def convert_selected_materials(*args):
        from_renderer = cmds.optionMenu(from_material_menu, query=True, value=True)
        to_renderer = cmds.optionMenu(to_material_menu, query=True, value=True)
        
        conversion_map = {
            "Arnold": 0,
            "Renderman": 1,
            "VRay": 2
        }
        
        if from_renderer and to_renderer:
            from_index = conversion_map.get(from_renderer)
            to_index = conversion_map.get(to_renderer)
            
            if from_index is not None and to_index is not None:
                setRenderer(from_index)
                convertMaterials(from_index, to_index)
                setRenderer(to_index)
                
    def convert_selected_lights(*args):
        from_renderer = cmds.optionMenu(from_light_menu, query=True, value=True)
        to_renderer = cmds.optionMenu(to_light_menu, query=True, value=True)
        
        conversion_map = {
            "Arnold": 0,
            "Renderman": 1,
            "VRay": 2
        }
        
        if from_renderer and to_renderer:
            from_index = conversion_map.get(from_renderer)
            to_index = conversion_map.get(to_renderer)
            
            if from_index is not None and to_index is not None:
                setRenderer(from_index)
                convertLights(from_index, to_index)
                setRenderer(to_index)
    
    window_name = "Renderer_Scene_Swapper"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
        
    cmds.window(window_name, title="Renderer Conversion Tool : Maya", iconName="RCT",widthHeight=(500, 300))

    #cmds.columnLayout()
    #cmds.image( image='/transfer/s5512613_SP/Masters_Projects/Maya_Files/images/logo_renderer_scene_swapper' )
    #cmds.separator(height=40, style='shelf')


    # Creating two optionMenus to choose the conversion from and to renderers for materials
    cmds.columnLayout(adjustableColumn=True, width=500, height=265,columnAlign="center")  # Set width and alignment
    
    cmds.text(label=" Renderer Conversion Tool : Maya ", height=20,font="boldLabelFont",align="center", backgroundColor=[0.8, 0.8, 0.8])  # Center align with background color
    cmds.text(label=" Note : Please make sure all the objects and lights are in separate groups. ", height=13,font="smallPlainLabelFont",align="center", backgroundColor=[0.8, 0.8, 0.8])  # Center align with background color
    #cmds.image( image='/transfer/s5512613_SP/Masters_Projects/Maya_Files/images/logo_renderer_scene_swapper' )
    cmds.separator(height=10, style='single')

    cmds.columnLayout(adjustableColumn=True, width=500, columnAlign="center",bgc=[0.8,0.8,0.8])
    # Materials Conversion Section
    cmds.text(label=" Materials Conversion ", height = 25,font="smallBoldLabelFont",align="center", backgroundColor=[0.0, 0.0, 0.3])  # Center align with background color
    cmds.text(label="Please select the object group/groups or all the objects and then press the CONVERT button:", align="center", backgroundColor=[0.0, 0.0, 0.2])  # Center align
    
    from_material_menu = cmds.optionMenu(label="From :", backgroundColor=[0.2, 0.2, 0.2])
    cmds.menuItem(label="Arnold")
    cmds.menuItem(label="Renderman")
    cmds.menuItem(label="VRay")
    
    to_material_menu = cmds.optionMenu(label="To   :", backgroundColor=[0.2, 0.2, 0.2])
    cmds.menuItem(label="Arnold")
    cmds.menuItem(label="Renderman")
    cmds.menuItem(label="VRay")
    
    # Convert Button for Materials
    cmds.button(label="Convert", command=convert_selected_materials)
    
    cmds.columnLayout(adjustableColumn=True, width=500, columnAlign="center",bgc=[0.8,0.8,0.8])
    # Create a separator
    cmds.separator(height=5, style='shelf')

    cmds.columnLayout(adjustableColumn=True, width=500, columnAlign="center",bgc=[0.2,0.2,0.5])
    # Lights Conversion Section
    cmds.text(label=" Lights Conversion ", height = 25,font="smallBoldLabelFont",align="center", backgroundColor=[0.3, 0.3, 0.0])  # Center align with background color
    cmds.text(label="Please select the light group/groups or all the lights and then press the CONVERT button:", align="center", backgroundColor=[0.2, 0.2, 0.0])  # Center align
    
    from_light_menu = cmds.optionMenu(label="From :", backgroundColor=[0.2, 0.2, 0.2])
    cmds.menuItem(label="Arnold")
    cmds.menuItem(label="Renderman")
    cmds.menuItem(label="VRay")
    
    to_light_menu = cmds.optionMenu(label="To   :", backgroundColor=[0.2, 0.2, 0.2])
    cmds.menuItem(label="Arnold")
    cmds.menuItem(label="Renderman")
    cmds.menuItem(label="VRay")
    
    cmds.columnLayout(adjustableColumn=True, width=500, columnAlign="center",bgc=[0.8,0.8,0.8])
    # Convert Button for Lights
    cmds.button(label="Convert", command=convert_selected_lights)
    
    cmds.showWindow(window_name)

# Calling the createUI function
createUI()