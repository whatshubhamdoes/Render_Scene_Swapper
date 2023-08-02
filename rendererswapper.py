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



def convertLights():
    currentRenderer=getCurrentRenderer()
    print(currentRenderer)
    check1=checkCurrentRenderer(currentRenderer)
    if check1== "Renderer Supported":
        lightsConversion()
    else:
        print("Renderer not supported for conversion")

convertLights()