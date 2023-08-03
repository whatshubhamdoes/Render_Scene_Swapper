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
                if cmds.nodeType(material) != 'aiStandardSurface' : #change to read from all of json
                    cmds.confirmDialog(title='Error', message='Selected object does not have an Arnold Standard Surface material applied.', button=['OK'], defaultButton='OK')
                    cmds.warning("Error : Selected object does not have an Arnold Standard Surface material applied.")
                    return
                if material:
                    new_material=cmds.shadingNode('PxrSurface',asShader=True) #change to get from json
                    new_sg=cmds.sets(new_material,renderable=True, noSurfaceShader=True, empty=True, name=new_material + '_conv')
                    cmds.connectAttr(new_material + '.outColor',new_sg + '.surfaceShader',force=True)


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