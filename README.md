# Renderer_Conversion_Tool
## version 1.0

![IMAGE!](Images/logo_renderer_scene_swapper.png)

This tool can be used to convert whole scene from one renderer to another in Autodesk Maya. The tool is also flexible enough to accomodate any new material to be added as per requirement and if any renderer is added in Autodesk Maya. The whole conversion works using the dictionary files.

Currently, the supported renderers are : 
1.  Autodesk Arnold
2.  Pixar's Renderman 
3.  Chaos Group's V-Ray.

*   The supported materials are :
1.  Arnold - aiStandardSurface & aiStandardHair
2.  Renderman - PxrDisneyBSDF & PxrMarschnerHair
3.  V-Ray - VRayMtl & VRayHairNextMtl

*   The supported lights are :
1.  Arnold - aiAreaLight,pointLight,directionalLight,spotLight,aiSkyDomeLight and aiMeshLight
2.  Renderman - PxrRectLight, PxrSphereLight, PxrDistantLight, PxrDiskLight, PxrDomeLight and PxrMeshLight
3.  V-Ray - VRayLightRectShape, VRayLightSphere, VRaySunShape, VRayLightIESShape, VRayLightDomeShape and VRayLightMesh 

## Installation
* Download the complete zip folder including the dictionary files and paste it in the scripts folder of Maya.
* Load the code and save it as a shelf button if required.

## How to use
1.  Open a completed scene to be rendered in any of the supported renderers.

2.  Click on the shelf button to launch the tool  

3.  For material conversion - select all the objects, select "From:" and "To:" renderer and click on "Convert button"
![Image!](Video/5.jpg)

4.  For light conversion - select all the lights, select "From:" and "To:" renderer and click on "Convert button"
![Image!](Video/7.jpg)

5.  Done. Select Render as the default renderer as already been changed to the converted one.
![Image!](Video/8.jpg)
## Video demonstrating the tool


# Scene rendered using Arnold
![Image!](Images/Test_Renders/Scene_1/arnold_render.jpg)

# Scene converted from Arnold to V-Ray and rendered
![Image!](Images/Test_Renders/Scene_1/vray_render.jpg)

# Same scene converted from V-Ray to Renderman
![Image!](Images/Test_Renders/Scene_1/renderman_render.jpg)


## Video Demonstrating the tool


## Test renders of different scenes (Always in this order : Arnold, Renderman, VRay)
*   Scene 2
![Image!](Images/Test_Renders/Scene_2/arnold_render.jpg)
![Image!](Images/Test_Renders/Scene_2/renderman_render.jpg)
![Image!](Images/Test_Renders/Scene_2/vray_render.jpg)

*   Scene 3
![Image!](Images/Test_Renders/Scene_3/arnold_render.jpg)
![Image!](Images/Test_Renders/Scene_3/renderman_render.jpg)
![Image!](Images/Test_Renders/Scene_3/vray_render.jpg)

*   Scene 4
![Image!](Images/Test_Renders/Scene_4/arnold_render.jpg)
![Image!](Images/Test_Renders/Scene_4/renderman_render.jpg)
![Image!](Images/Test_Renders/Scene_4/vray_render.jpg)

*   Scene 5
![Image!](Images/Test_Renders/Scene_5/car/arnold_render.jpg)
![Image!](Images/Test_Renders/Scene_5/car/renderman_render.jpg)
![Image!](Images/Test_Renders/Scene_5/car/vray_render.jpg)

*   Scene 6
![Image!](Images/Test_Renders/Scene_6/arnold_render.jpg)
![Image!](Images/Test_Renders/Scene_6/renderman_render.jpg)
![Image!](Images/Test_Renders/Scene_6/vray_render.jpg)

## Required Packages/Modules
* If the user has Python, Autodesk Maya and all the supported renderers installed on their devices then the tool doesn't require any other package/module.

## Credits
Created by :
* Shubham Prabhakar
* M.Sc. Computer Animation and Visual Effects
* Bournemouth University
