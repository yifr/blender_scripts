import numpy as np

try:
    import bpy
except ImportError:
    print(
        "Unable to import Blender Python Interface (bpy). \
        No procedural textures will be available."
    )


def Shader(name):
    return "ShaderNodeTex" + name.capitalize()


PROCEDURAL_TEXTURES = [
    "voronoi",
    "wave",
    "magic",
    "noise",
    "checker",
    "brick",
    "musgrave",
]

TEXTURE_MAPS = {
    "ShaderNodeTexVoronoi": {"Scale": [0.5, 5], "Randomness": [0.6, 1]},
    "ShaderNodeTexWave": {
        "Scale": [0.25, 4],
        "Distortion": [5.0, 50.0],
        "Detail": [0, 5],
        "Detail Scale": [0.5, 2],
        "Detail Roughness": [0.25, 0.75],
    },
    "ShaderNodeTexNoise": {
        "Scale": [0.25, 3],
        "Detail": [1, 5],
        "Roughness": [0.2, 1],
        "Distortion": [0.2, 4],
    },
    "ShaderNodeTexMagic": {"Scale": [0.1, 1], "Distortion": [0.5, 10]},
    "ShaderNodeTexChecker": {"Scale": [1, 5]},
    "ShaderNodeTexBrick": {
        "Scale": [1, 10],
        "Mortar Size": [0, 0.025],
        "Mortar Smooth": [0, 1],
        "Bias": [-1, 0],
        "Brick Width": [0.02, 2],
        "Row Height": [0.25, 1],
    },
    "ShaderNodeTexMusgrave": {
        "Scale": [1, 5],
        "Detail": [1, 10],
        "Dimension": [0.25, 2],
        "Lacunarity": [0.25, 3],
    },
}


def base_texture(
    texture_type, texture_params, width=0.5, material_name="texture", shading=True,
):
    """
    Appends procedural texture polka dot texture to mesh.
    Params:
        scene: (BlenderScene): The BlenderScene in which the mesh lives
        scale: (int) controls the number of dots
        randomness: (int) controls how random the dots are arranged
        distance: (str) controls distance function for texture texture
        colors: (tuple list) colors of texture
        width: relative size of dots
    """

    scene = bpy.context.scene

    mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    def random_color():
        base_color = [np.random.uniform(0, 1) for i in range(3)] + [1]
        return base_color

    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = random_color()
    bsdf.inputs["Specular"].default_value = np.random.uniform(0.5, 0.75)
    bsdf.inputs["Roughness"].default_value = np.random.uniform(0.5, 0.75)
    bsdf.inputs["Transmission"].default_value = np.random.uniform(0, 0.1)
    bsdf.inputs["Sheen Tint"].default_value = np.random.uniform(0, 0.1)
    output_node = bsdf

    texture = nodes.new(type=texture_type)
    color_ramp = nodes.new(type="ShaderNodeValToRGB")
    mapping_node = nodes.new(type="ShaderNodeMapping")
    coordinate_node = nodes.new(type="ShaderNodeTexCoord")

    nodes["Material Output"].location = (600, 0)
    output_node.location = (400, 0)
    color_ramp.location = (200, 0)
    texture.location = (0, 0)
    mapping_node.location = (-200, 0)
    coordinate_node.location = (-400, 0)

    ##############
    # Link Nodes
    ##############
    links = mat.node_tree.links
    links.new(output_node.outputs[0], nodes["Material Output"].inputs[0])

    # Coordinate Texture -> Mapping Node --> Noise Texture
    links.new(coordinate_node.outputs["Object"], mapping_node.inputs[0])
    links.new(mapping_node.outputs[0], texture.inputs[0])

    links.new(texture.outputs[0], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], output_node.inputs[0])
    color_ramp_loc = np.random.uniform(0.25, 0.75)
    color_ramp.color_ramp.elements.new(color_ramp_loc)

    color_ramp.color_ramp.elements[0].color = random_color()
    color_ramp.color_ramp.elements[1].color = random_color()

    # Evenly interpolate between color/white spots
    color_ramp.color_ramp.elements[0].position = 0
    color_ramp.color_ramp.elements[1].position = width
    color_ramp.color_ramp.interpolation = "CONSTANT"

    for param in texture_params:
        param_val = texture_params[param]
        if type(param_val) == list:
            param_val = np.random.uniform(param_val[0], param_val[1])
        try:
            texture.inputs[param].default_value = param_val
        except KeyError:
            print(
                f"Invalid texture parameter: {param} for texture type: {texture_type}."
            )

    print(f"Created {texture_type} Texture...")
    return mat


def create_texture(texture_type="random"):
    """ Adds texture to an object

        Params:
        -------
        texture_type: str
            Name of texture type. Options are:
            [voronoi, noise, magic, wave, checker, brick]
            if set to "random", will randomly choose from the
            above selection
        texture_params: dict
            Dictionary of parameters for texture. If left empty
            they will be randomly selected from a range specified
            in a global dictionary at the top of the files
    """
    if texture_type == "random":
        texture_type = np.random.choice(PROCEDURAL_TEXTURES)

    elif texture_type not in PROCEDURAL_TEXTURES:
        raise ValueError(
            f"""Texture type: {texture_type} is not an option.
            Please specify a texture type from the following list:
            {', '.join(PROCEDURAL_TEXTURES)}"""
        )

    shader = Shader(texture_type)
    shader_params = TEXTURE_MAPS[shader]
    texture_params = {}
    for param in shader_params:
        shader_range = shader_params[param]
        texture_params[param] = np.random.uniform(shader_range[0], shader_range[1])

    mat = base_texture(texture_type=shader, texture_params=texture_params, width=0.5,)

    print("Completed")
    return mat, texture_params
