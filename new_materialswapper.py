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
    with open('/transfer/s5512613_SP/Masters_Project/Render_Scene_Swapper/Dictionary/materials.json','r') as file :
        lightsData=json.load(file)
    for rendererInfo in lightsData["Materials"]["renderer"]:
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

def copyLightAttributes(light,lightsData,light_type,number,convNumber):
    try:
        a_intensity = lightsData["Lights"][f"{light_type}"]["attribute_intensity"][number]
        intensity=cmds.getAttr(f"{light}.{a_intensity}")
    except:
        pass
    try:
        a_color = lightsData["Lights"][f"{light_type}"]["attribute_color"][number]
        l_color = cmds.getAttr(f"{light}.{a_color}")
    except:
        pass
    try:
        a_exposure = lightsData["Lights"][f"{light_type}"]["attribute_exposure"][number]
        exposure = cmds.getAttr(f"{light}.{a_exposure}")
    except:
        pass
    convLight=lightsData["Lights"][light_type]["name"][convNumber]
    print(convLight)
    convLight=cmds.shadingNode(f"{convLight}",asLight=True,name=f"{light}_conv")
    try:
        a_intensity = lightsData["Lights"][f"{light_type}"]["attribute_intensity"][convNumber]
        cmds.setAttr(f"{convLight}.{a_intensity}", intensity)
    except:
        pass
    try:
        a_color = lightsData["Lights"][f"{light_type}"]["attribute_color"][convNumber]
        cmds.setAttr(f"{convLight}.{a_color}", l_color[0][0], l_color[0][1], l_color[0][2], type="double3")
    except:
        pass
    try:
        a_exposure = lightsData["Lights"][f"{light_type}"]["attribute_exposure"][convNumber] 
        cmds.setAttr(f"{convLight}.{a_exposure}", exposure)
    except:
        pass
    lightTransform=cmds.listRelatives(light,parent=True,shapes=True,fullPath=True)
    cmds.matchTransform(f"{convLight}", lightTransform)
    lightSet=cmds.listRelatives(lightTransform,parent=True,fullPath=True)
    if lightSet:
        cmds.parent(f"{convLight}", lightSet)    

def lightsConversion(convNumber):
    with open('/transfer/s5512613_SP/Masters_Project/Render_Scene_Swapper/Dictionary/materials.json','r') as file :
        lightsData=json.load(file)
    currentRenderer=getCurrentRenderer()    
    number=assignNumber(currentRenderer)
    sel = cmds.ls(sl=True)
    if not sel :
        cmds.confirmDialog(title='Error', message='Please select an object', button=['OK'], defaultButton='OK')
        cmds.warning("Error : Please select an object")
        return
    for obj in sel:    
        lights = cmds.ls(sl = True, dag = True, s = True)
        print(lights)
        for light in lights:
            print(light)  
            light_type = cmds.nodeType(light)
            print(light_type)
            if (light_type == lightsData["Lights"]["area_light"]["name"][number]):
                light_type="area_light"
                print(light_type)
                copyLightAttributes(light,lightsData,light_type,number,convNumber)
            elif(light_type == lightsData["Lights"]["point_light"]["name"][number]):
                light_type="point_light"
                print(light_type)
                copyLightAttributes(light,lightsData,light_type,number,convNumber)
            elif(light_type == lightsData["Lights"]["directional_light"]["name"][number]):
                light_type="directional_light"
                print(light_type)
                copyLightAttributes(light,lightsData,light_type,number,convNumber)
            elif(light_type == lightsData["Lights"]["spot_light"]["name"][number]):
                light_type="spot_light"
                print(light_type)
                copyLightAttributes(light,lightsData,light_type,number,convNumber)
            elif(light_type == lightsData["Lights"]["skyDome_light"]["name"][number]):
                light_type="skyDome_light"
                print(light_type)
                copyLightAttributes(light,lightsData,light_type,number,convNumber)
            elif(light_type == lightsData["Lights"]["mesh_light"]["name"][number]):
                light_type="mesh_light"
                print(light_type)
                copyLightAttributes(light,lightsData,light_type,number,convNumber) 
            else:
                pass


def convertLights(convNumber):
    currentRenderer=getCurrentRenderer()
    print(currentRenderer)
    check1=checkCurrentRenderer(currentRenderer)
    if check1== "Renderer Supported":
        lightsConversion(convNumber)
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
            convertLights(convNumber)
        elif selected_button_f == "Renderman to Arnold":
            convNumber=0
            convertLights(convNumber)
        elif selected_button_f == "Arnold to VRay":
            convNumber=2
            convertLights(convNumber)
        elif selected_button_f == "VRay to Arnold":
            convNumber=0
            convertLights(convNumber)
        elif selected_button_f == "Renderman to VRay":
            convNumber=2
            convertLights(convNumber)
        elif selected_button_f == "VRay to Renderman":
            convNumber=1
            convertLights(convNumber)
    
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