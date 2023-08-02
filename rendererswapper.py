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
                a_intensity = lightsData["Lights"]["area_light"]["attribute_intensity"][number]
                a_color = lightsData["Lights"]["area_light"]["attribute_color"][number]
                a_exposure = lightsData["Lights"]["area_light"]["attribute_exposure"][number]
                intensity=cmds.getAttr(f"{light}.{a_intensity}")
                l_color = cmds.getAttr(f"{light}.{a_color}")
                exposure = cmds.getAttr(f"{light}.{a_exposure}")
                convLight=lightsData["Lights"]["area_light"]["name"][1] #change 1 to a variable as per UI
                convLight=cmds.createNode("{convLight}",name=f"{light}_conv")
                a_intensity = lightsData["Lights"]["area_light"]["attribute_intensity"][1]
                a_color = lightsData["Lights"]["area_light"]["attribute_color"][1]
                a_exposure = lightsData["Lights"]["area_light"]["attribute_exposure"][1]
                cmds.setAttr(f"{convLight}.{a_intensity}", intensity)
                cmds.setAttr(f"{convLight}.{a_color}", l_color[0][0], l_color[0][1], l_color[0][2], type="double3")
                cmds.setAttr(f"{convLight}.{a_exposure}", exposure)
                cmds.matchTransform(f"{light}_conv",f"{light}")



def convertLights():
    currentRenderer=getCurrentRenderer()
    print(currentRenderer)
    check1=checkCurrentRenderer(currentRenderer)
    if check1== "Renderer Supported":
        lightsConversion()
    else:
        print("Renderer not supported for conversion")

convertLights()