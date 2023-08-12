# def createUI():
    
#     # Function to call the selected conversion function
#     def convert_selected(conversion_group):
#         selected_button = cmds.radioCollection(conversion_group, query=True, select=True)
#         selected_button_f = cmds.radioButton(selected_button, query=True, label=True)
#         print(f"{selected_button_f=}")
#         if selected_button_f == "Arnold to Renderman":
#             convNumber=1
#             convertMaterials(convNumber)
#         elif selected_button_f == "Renderman to Arnold":
#             convNumber=0
#             convertMaterials(convNumber)
#         elif selected_button_f == "Arnold to VRay":
#             convNumber=2
#             convertMaterials(convNumber)
#         elif selected_button_f == "VRay to Arnold":
#             convNumber=0
#             convertMaterials(convNumber)
#         elif selected_button_f == "Renderman to VRay":
#             convNumber=2
#             convertMaterials(convNumber)
#         elif selected_button_f == "VRay to Renderman":
#             convNumber=1
#             convertMaterials(convNumber)
    
#     window_name = "Renderer_Scene_Swapper"
#     if cmds.window(window_name, exists=True):
#         cmds.deleteUI(window_name)
        
#     cmds.window(window_name, title="Universal Renderer Scene Swapper : Maya",widthHeight=(500, 300))

#     # Creating a radio button group to choose the conversion function
#     layout=cmds.columnLayout(adjustableColumn=True)
#     cmds.text(label="Please select all the lights and then select the conversion function:")
#     conversion_group = cmds.radioCollection()
#     arnold_to_renderman_button = cmds.radioButton(label="Arnold to Renderman")
#     print(f"{arnold_to_renderman_button=}")
#     renderman_to_arnold_button = cmds.radioButton(label="Renderman to Arnold")
#     print(f"{renderman_to_arnold_button=}")
#     arnold_to_vray_button = cmds.radioButton(label="Arnold to VRay")
#     print(f"{arnold_to_vray_button=}")
#     vray_to_arnold_button = cmds.radioButton(label="VRay to Arnold")
#     print(f"{vray_to_arnold_button=}")
#     renderman_to_vray_button = cmds.radioButton(label="Renderman to VRay")
#     print(f"{renderman_to_vray_button=}")
#     vray_to_renderman_button = cmds.radioButton(label="VRay to Renderman")
#     print(f"{vray_to_renderman_button=}")

#     # Creating a button to trigger the selected conversion function
#     cmds.button(label="Convert", command=lambda *args: convert_selected(conversion_group))
#     cmds.showWindow(window_name)

# # Calling the createUI function
# createUI()


# def createUI():
    
#     # Function to call the selected conversion function
#     def convert_selected(*args):
#         selected_button_f = cmds.optionMenu(conversion_menu, query=True, value=True)
#         if selected_button_f:
#             if selected_button_f == "Arnold to Renderman":
#                 convNumber = 1
#                 convertMaterials(convNumber)
#             elif selected_button_f == "Renderman to Arnold":
#                 convNumber = 0
#                 convertMaterials(convNumber)
#             elif selected_button_f == "Arnold to VRay":
#                 convNumber = 2
#                 convertMaterials(convNumber)
#             elif selected_button_f == "VRay to Arnold":
#                 convNumber = 0
#                 convertMaterials(convNumber)
#             elif selected_button_f == "Renderman to VRay":
#                 convNumber = 2
#                 convertMaterials(convNumber)
#             elif selected_button_f == "VRay to Renderman":
#                 convNumber = 1
#                 convertMaterials(convNumber)
    
#     window_name = "Renderer_Scene_Swapper"
#     if cmds.window(window_name, exists=True):
#         cmds.deleteUI(window_name)
        
#     cmds.window(window_name, title="Universal Renderer Scene Swapper : Maya", widthHeight=(500, 300))

#     # Creating an optionMenu to choose the conversion function
#     layout = cmds.columnLayout(adjustableColumn=True)
#     cmds.text(label="Please select all the lights and then select the conversion function:")
    
#     conversion_menu = cmds.optionMenu(label="Select Conversion:")
#     cmds.menuItem(label="Arnold to Renderman")
#     cmds.menuItem(label="Renderman to Arnold")
#     cmds.menuItem(label="Arnold to VRay")
#     cmds.menuItem(label="VRay to Arnold")
#     cmds.menuItem(label="Renderman to VRay")
#     cmds.menuItem(label="VRay to Renderman")

#     # Creating a button to trigger the selected conversion function
#     cmds.button(label="Convert", command=convert_selected)
#     cmds.showWindow(window_name)

# # Calling the createUI function
# createUI()