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
    with open('Dictionary/lights.json','r') as file :
        lightsData=json.load(file)
    for rendererInfo in lightsData["Lights"]["renderer"]:
        #print(rendererInfo)
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

def copyLightAttributes(light,lightsData,light_type,number):
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
    convLight=lightsData["Lights"][light_type]["name"][2] #change 1 to a variable as per UI
    print(convLight)
    convLight=cmds.shadingNode(f"{convLight}",asLight=True,name=f"{light}_conv")
    try:
        a_intensity = lightsData["Lights"][f"{light_type}"]["attribute_intensity"][2]
        cmds.setAttr(f"{convLight}.{a_intensity}", intensity)
    except:
        pass
    try:
        a_color = lightsData["Lights"][f"{light_type}"]["attribute_color"][2]
        cmds.setAttr(f"{convLight}.{a_color}", l_color[0][0], l_color[0][1], l_color[0][2], type="double3")
    except:
        pass
    try:
        a_exposure = lightsData["Lights"][f"{light_type}"]["attribute_exposure"][2] 
        cmds.setAttr(f"{convLight}.{a_exposure}", exposure)
    except:
        pass
    lightTransform=cmds.listRelatives(light,parent=True,shapes=True,fullPath=True)
    cmds.matchTransform(f"{convLight}", lightTransform)
    lightSet=cmds.listRelatives(lightTransform,parent=True,fullPath=True)
    if lightSet:
        cmds.parent(f"{convLight}", lightSet)    

def lightsConversion():
    with open('Dictionary/lights.json','r') as file :
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
                copyLightAttributes(light,lightsData,light_type,number)
            elif(light_type == lightsData["Lights"]["point_light"]["name"][number]):
                light_type="point_light"
                print(light_type)
                copyLightAttributes(light,lightsData,light_type,number)
            elif(light_type == lightsData["Lights"]["directional_light"]["name"][number]):
                light_type="directional_light"
                print(light_type)
                copyLightAttributes(light,lightsData,light_type,number)
            elif(light_type == lightsData["Lights"]["spot_light"]["name"][number]):
                light_type="spot_light"
                print(light_type)
                copyLightAttributes(light,lightsData,light_type,number)
            elif(light_type == lightsData["Lights"]["skyDome_light"]["name"][number]):
                light_type="skyDome_light"
                print(light_type)
                copyLightAttributes(light,lightsData,light_type,number)
            elif(light_type == lightsData["Lights"]["mesh_light"]["name"][number]):
                light_type="mesh_light"
                print(light_type)
                copyLightAttributes(light,lightsData,light_type,number)            
            else:
                pass


def convertLights():
    currentRenderer=getCurrentRenderer()
    print(currentRenderer)
    check1=checkCurrentRenderer(currentRenderer)
    if check1== "Renderer Supported":
        lightsConversion()
    else:
        print("Renderer not supported for conversion")

convertLights()