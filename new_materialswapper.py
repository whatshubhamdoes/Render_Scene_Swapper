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
                if key in ["attribute_diffuse_color", "attribute_specular_color", "attribute_roughness", "attribute_metalness", "attribute_opacity", "attribute_normal_map", "attribute_displacement", "attribute_emissive_color", "attribute_transparency", "attribute_ambient_occlusion"]:
                    components_material_map[key]= value[number]


def copyMaterialAttributes(material, materialsData, material_type, number, convNumber):
    convMaterial=materialsData["Materials"][material_type]["name"][convNumber]
    print(convMaterial)
    convMaterial=cmds.shadingNode(f"{convMaterial}",asShader=True,name=f"{material}_conv")
    convMaterialShadingGroup = cmds.sets(convMaterial,renderable=True,noSurfaceShader=True,empty=True, name=convMaterial + 'SG')
    cmds.connectAttr(convMaterial + '.outColor', convMaterialShadingGroup+'.surfaceShader',force=True)
    
    components_material_map={}
    createMaterialComponentMap(components_material_map,materialsData,material_type,number)
    print(components_material_map)
    
    components_convMaterial_map={}
    createMaterialComponentMap(components_convMaterial_map,materialsData,material_type,convNumber)
    print(components_convMaterial_map)
    
    for attr, convAttr in zip(components_material_map.values(), components_convMaterial_map.values()):
        try:
            material_new=''.join(material)
            attribute=material_new+'.'+attr
            value=cmds.getAttr(attribute)
            file_node=cmds.connectionInfo(attribute,sourceFromDestination=True)
            
            convMaterial=''.join(convMaterial)
            convMaterial_new=convMaterial+'.'+convAttr
            cmds.setAttr(convMaterial_new,value[0][0],value[0][1],value[0][2],type='double3')
            if file_node:
                file_path=cmds.listConnections(attribute,type='file')
                file_path=''.join(file_path)
                cmds.connectAttr(file_path+'.outColor',convMaterial_new)

        except:
            continue
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
        materialsData["Materials"]["standard_material"]["name"][number] : "standard_material",
        materialsData["Materials"]["hair_material"]["name"][number] : "hair_material"
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
                material=cmds.ls(cmds.listConnections(shadeEng),materials = True)
                print(material)
                material_type=cmds.nodeType(material)
                if material_type in material_conversion_map :
                    material_type=material_conversion_map[material_type]
                    print(material_type)
                    shading_group= copyMaterialAttributes(material, materialsData, material_type, number, convNumber)
                cmds.sets(sel[0],edit=True,forceElement=shading_group)



def convertMaterials(convNumber):
    currentRenderer=getCurrentRenderer()
    print(currentRenderer)
    check1=checkCurrentRenderer(currentRenderer)
    if check1== "Renderer Supported":
        materialsConversion(convNumber)
    else:
        print("Renderer not supported for conversion")


def createUI():
    
    # Function to call the selected conversion function
    def convert_selected(conversion_group):
        selected_button = cmds.radioCollection(conversion_group, query=True, select=True)
        selected_button_f = cmds.radioButton(selected_button, query=True, label=True)
        print(f"{selected_button_f=}")
        if selected_button_f == "Arnold to Renderman":
            convNumber=1
            convertMaterials(convNumber)
        elif selected_button_f == "Renderman to Arnold":
            convNumber=0
            convertMaterials(convNumber)
        elif selected_button_f == "Arnold to VRay":
            convNumber=2
            convertMaterials(convNumber)
        elif selected_button_f == "VRay to Arnold":
            convNumber=0
            convertMaterials(convNumber)
        elif selected_button_f == "Renderman to VRay":
            convNumber=2
            convertMaterials(convNumber)
        elif selected_button_f == "VRay to Renderman":
            convNumber=1
            convertMaterials(convNumber)
    
    window_name = "Renderer_Scene_Swapper"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
        
    cmds.window(window_name, title="Universal Renderer Scene Swapper : Maya",widthHeight=(500, 300))

    # Creating a radio button group to choose the conversion function
    layout=cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="Please select all the lights and then select the conversion function:")
    conversion_group = cmds.radioCollection()
    arnold_to_renderman_button = cmds.radioButton(label="Arnold to Renderman")
    print(f"{arnold_to_renderman_button=}")
    renderman_to_arnold_button = cmds.radioButton(label="Renderman to Arnold")
    print(f"{renderman_to_arnold_button=}")
    arnold_to_vray_button = cmds.radioButton(label="Arnold to VRay")
    print(f"{arnold_to_vray_button=}")
    vray_to_arnold_button = cmds.radioButton(label="VRay to Arnold")
    print(f"{vray_to_arnold_button=}")
    renderman_to_vray_button = cmds.radioButton(label="Renderman to VRay")
    print(f"{renderman_to_vray_button=}")
    vray_to_renderman_button = cmds.radioButton(label="VRay to Renderman")
    print(f"{vray_to_renderman_button=}")

    # Creating a button to trigger the selected conversion function
    cmds.button(label="Convert", command=lambda *args: convert_selected(conversion_group))
    cmds.showWindow(window_name)

# Calling the createUI function
createUI()