import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.mel as mel
import os
import sys
import json

def getCurrentRenderer():
    currentRenderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
    return currentRenderer

def checkCurrentRenderer(currentRenderer):
    with open('/transfer/s5512613_SP/Masters_Project/Render_Scene_Swapper/Dictionary/lights.json','r') as file :
        lightsData=json.load(file)
    for rendererInfo in lightsData["Lights"]["renderer"]:
        if currentRenderer in rendererInfo:
            return ("Renderer Supported")

def assignNumber(currentRenderer):
    if currentRenderer == "arnold" :
        return 0
    elif currentRenderer == "renderman" :
        return 1
    elif currentRenderer == "vray" :
        return 2
    else:
        return False 


def createMaterialComponentMap(components_material_map,materialsData,material_type,number):
    for material in materialsData["Materials"]:
        if material != "renderer":
            for key,value in materialsData["Materials"][material_type].items():
                if key in ["attribute_base", "attribute_diffuse_color", "attribute_metalness", "attribute_specular", "attribute_specular_color", "attribute_specular_roughness", "attribute_transmission", "attribute_transmission_color", "attribute_subsurface", "attribute_subsurface_color", "attribute_subsurface_radius", "attribute_subsurface_scale", "attribute_subsurface_anisotropy", "attribute_coat", "attribute_coat_color", "attribute_coat_roughness", "attribute_coat_anisotropy", "attribute_sheen", "attribute_sheen_color", "attribute_sheen_roughness", "attribute_emission", "attribute_emission_color", "attribute_normal_map"]:
                    components_material_map[key]= value[number]


def copyMaterialAttributes(material, materialsData, material_type, number, convNumber):
    convMaterial = materialsData["Materials"][material_type]["name"][convNumber]
    print(convMaterial)
    convMaterial = cmds.shadingNode(f"{convMaterial}", asShader=True, name=f"{material}_conv")
    print(convMaterial) 
    # Naming wrong of shading group
    convMaterialShadingGroup = cmds.sets(convMaterial, renderable=True, noSurfaceShader=True, empty=True, name=convMaterial + 'SG')
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
            value=cmds.getAttr(material+'.'+attr)
            print(value)
            file_node=cmds.connectionInfo(material+'.'+attr,sourceFromDestination=True)
            print(file_node)
            file_node=''.join(file_node)
        except:
            pass

    return convMaterialShadingGroup


def materialsConversion(convNumber):
    with open('/transfer/s5512613_SP/Masters_Project/Render_Scene_Swapper/Dictionary/materials.json','r') as file :
        materialsData=json.load(file)
    currentRenderer=getCurrentRenderer()    
    number=assignNumber(currentRenderer)
    sel = cmds.ls(sl=True)
    if not sel :
        cmds.confirmDialog(title='Error', message='Please select an object', button=['OK'], defaultButton='OK')
        cmds.warning("Error : Please select an object")
        return

    material_conversion_map = {
        materialsData["Materials"]["standard_material"]["name"][number] : "standard_material"
    }

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
                            shading_group= copyMaterialAttributes(material, materialsData, material_type, number, convNumber)
                            cmds.sets(object,edit=True,forceElement=shading_group)



def convertMaterials(fromNumber,convNumber):
    currentRenderer=getCurrentRenderer()
    print(currentRenderer)
    check1=checkCurrentRenderer(currentRenderer)
    if check1== "Renderer Supported":
        materialsConversion(convNumber)
    else:
        print("Renderer not supported for conversion")

def createUI():
    
    # Function to call the selected conversion function
    def convert_selected(*args):
        from_renderer = cmds.optionMenu(from_menu, query=True, value=True)
        to_renderer = cmds.optionMenu(to_menu, query=True, value=True)
        
        conversion_map = {
            "Arnold": 0,
            "Renderman": 1,
            "VRay": 2
        }
        
        if from_renderer and to_renderer:
            from_index = conversion_map.get(from_renderer)
            to_index = conversion_map.get(to_renderer)
            
            if from_index is not None and to_index is not None:
                convertMaterials(from_index, to_index)
    
    window_name = "Renderer_Scene_Swapper"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
        
    cmds.window(window_name, title="Universal Renderer Scene Swapper : Maya", widthHeight=(500, 300))

    # Creating two optionMenus to choose the conversion from and to renderers
    layout = cmds.columnLayout(adjustableColumn=True, width=500, columnAlign="center")  # Set width and alignment
    
    cmds.text(label="Please select all the lights and then select the conversion function:", align="center")  # Center align
    
    from_menu = cmds.optionMenu(label="From Renderer:")
    cmds.menuItem(label="Arnold")
    cmds.menuItem(label="Renderman")
    cmds.menuItem(label="VRay")
    
    to_menu = cmds.optionMenu(label="To Renderer:")
    cmds.menuItem(label="Arnold")
    cmds.menuItem(label="Renderman")
    cmds.menuItem(label="VRay")

    # Creating a button to trigger the selected conversion function
    cmds.button(label="Convert", command=convert_selected)
    cmds.showWindow(window_name)

# Calling the createUI function
createUI()
