import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import QuadCortexController as QC


PRINT_DEBUG = True
OUTPUT_PORT_NAME = QC.find_midi_ports(find_output_port="Quad Cortex")


with QC.QuadCortexController(port_name=OUTPUT_PORT_NAME, debug=PRINT_DEBUG) as qc:
    mode = ["stomp", "scene", "preset"][0]
    qc.load_mode(mode)

    setlist = ["Factory Presets", "My Presets", "Artists", "Users", "Rabea", "Neural DSP", "Songs"][0]
    qc.change_setlist(setlist)

    preset = 1
    qc.change_preset(preset)

    scene = "A"
    qc.select_scene(scene)

    footswitch = "A"
    qc.select_footswitch(footswitch)

    qc.tuner(True)
    qc.tuner(False)

    qc.gig_view(True)
    qc.gig_view(False)

    qc.tempo(60)

    qc.close()
