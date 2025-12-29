import mido


INPUT_PORT_NAME = "Guitar Pro MIDI"
IGNORE_MESSAGE_TYPES = ["clock", "active_sensing", "control_change", "note_off"]


for name in mido.get_input_names():
    print("MIDI INPUT PORTS:")
    print("\t", name)
    if INPUT_PORT_NAME in name:
        INPUT_PORT_NAME = name
        break

if not INPUT_PORT_NAME:
    raise RuntimeError("MIDI input port not found")
print(f"[MIDI IN] Listening on: {INPUT_PORT_NAME}")
print("[MIDI IN] Waiting for messages...\n")


with mido.open_input(INPUT_PORT_NAME) as port:
    for msg in port:
        if msg.type in IGNORE_MESSAGE_TYPES:
            continue
        elif msg.type == "program_change" and msg.channel == 0:
            print(f"# ## ###   PLAY START   ### ## #")
        elif msg.type == "note_on":
            print(f"[NOTE ON ]   channel={msg.channel:03}   note={msg.note:03}   vel={msg.velocity:03}")
        elif msg.type == "note_off":
            print(f"[NOTE OFF]   channel={msg.channel:03}   note={msg.note:03}")
