from tkinter import ttk
import tkinter as tk
import threading
import mido
import QuadCortexController as QC


"""
This Python app allows you to control the Neural DSP Quad Cortex using MIDI input from Guitar Pro via loopMIDI or any virtual MIDI port.

Configuration:
  - input_port           : MIDI input port (Guitar Pro)
  - output_port          : MIDI output port (Quad Cortex MIDI)
  - IGNORE_MESSAGE_TYPES : List of MIDI message types to ignore
  - PRINT_DEBUG          : True/False for verbose console output

Instructions:
  1. Make sure a virtual MIDI cable is set up (loopMIDI or similar).
  2. Configure Guitar Pro MIDI output via "Sound" → "Audio / MIDI Settings..."
  3. Add an instrument for each channel you want to use for Quad Cortex control:
       a. Channel 0 will give you control of: Mode, Gig View, Tuner, Foot-switches, and Scene selection.
       b. Channel 2 will give you control of Setlists and Presets.
       c. Channel 4 will give you control of the Tempo.
  4. Set all instruments to Standard Tuning, and set the to output to the MIDI port and channel.
  5. Start this Python app, ensuring the INPUT_PORT_NAME matches your Guitar Pro MIDI output.
  6. Play notes in Guitar Pro; each note will trigger the assigned Quad Cortex command.

Important Notes:
  1. Guitar Pro's MIDI range is 0–127 → Keep that in mind for Preset or Tempo changes.
  2. The low E's value (in a Standard Tuning) is 40 → coincidentally this is the QC's lowest tempo.
  3. The Tuner screen and the "Gig View" will be visible ONLY on the QC itself, not on the PC companion.
  4. Tempo might be a little off, as there is no direct way to send it, but rather send two commands like a tap tempo.
  5. As such, do not send MIDI commands whilst the Tempo is being set (I couldn't make it work asynchronously).
  
To convert to .exe:
pyinstaller QuadCortexGuitarProMIDI.spec
"""


# App Controls:
PRINT_DEBUG = True
IGNORE_MESSAGE_TYPES = ["clock", "active_sensing", "control_change", "note_off"]

# Quad Cortex Controls:
QC_MODES    = ["stomp", "scene", "preset"]
QC_SETLISTS = ["Factory Presets", "My Presets", "Artists", "Users", "Rabea", "Neural DSP", "Songs"]

# MIDI Channels and fret ranges per action:
BASE_FRET             = 40
MAX_MIDI_RANGE        = 127
MIN_QC_TEMPO          = 40
CHANNEL_COMMAND       = 0
FRET_RANGE_MODES      = range(BASE_FRET + 0,  BASE_FRET + 3)       # 6th string, frets 0–2 → load_mode
FRET_RANGE_GIG_VIEW   = range(BASE_FRET + 5,  BASE_FRET + 10)      # 5th string, frets 0–4 → gig_view (0=off)
FRET_RANGE_TUNER      = range(BASE_FRET + 10, BASE_FRET + 15)      # 4th string, frets 0–4 → tuner (0=off)
FRET_RANGE_FOOTSWITCH = range(BASE_FRET + 15, BASE_FRET + 23)      # 3rd string, frets 0–7 → footswitch
FRET_RANGE_SCENE      = range(BASE_FRET + 24, BASE_FRET + 32)      # 1st string, frets 0–7 → scene
CHANNEL_SETLIST       = 2
FRET_RANGE_SETLIST    = range(BASE_FRET + 0,  BASE_FRET + 24)      # 6th string, frets 0–23 → setlist
FRET_RANGE_PRESET     = range(BASE_FRET + 24, MAX_MIDI_RANGE)      # 1st string, frets 0–63 → preset
CHANNEL_TEMPO         = 4
FRET_RANGE_TEMPO      = range(BASE_FRET + 0,  MAX_MIDI_RANGE)      # All notes beginning from 6th string - 0th fret (low E)


def set_status(text, error=False):
    status_label.config(
        text=text,
        foreground="red" if error else "green"
    )


running = False
midi_thread = None


def midi_loop(input_port, output_port):
    global running

    try:
        with QC.QuadCortexController(port_name=output_port, debug=PRINT_DEBUG) as qc:
            with mido.open_input(input_port) as port:
                if PRINT_DEBUG:
                    print(f"[MIDI OUT] Transmitting to: {output_port}")
                    print(f"[MIDI IN ] Listening on: {input_port}")
                    print(f"[MIDI IN ] Waiting for messages...\n")
                set_status("Running")

                for msg in port:
                    if msg.type in IGNORE_MESSAGE_TYPES:
                        continue

                    elif msg.type == "program_change" and msg.channel == 0:
                        if PRINT_DEBUG:
                            print(f"# ## ###   PLAY START   ### ## #")
                        # qc.tuner(False)
                        # qc.gig_view(True)

                    elif msg.type == "note_on":
                        if PRINT_DEBUG:
                            print(f"[NOTE ON ]   channel={msg.channel:03}   note={msg.note:03}   vel={msg.velocity:03}")

                        if msg.channel == CHANNEL_COMMAND:
                            if PRINT_DEBUG:
                                print(f"[CHANNEL_COMMAND]", end=" ")
                            if msg.note in FRET_RANGE_MODES:
                                qc.load_mode(mode=QC_MODES[msg.note - min(FRET_RANGE_MODES)])
                            elif msg.note in FRET_RANGE_GIG_VIEW:
                                qc.gig_view(on=msg.note != min(FRET_RANGE_GIG_VIEW))
                            elif msg.note in FRET_RANGE_TUNER:
                                qc.tuner(on=msg.note != min(FRET_RANGE_TUNER))
                            elif msg.note in FRET_RANGE_FOOTSWITCH:
                                qc.select_footswitch(footswitch=msg.note - min(FRET_RANGE_FOOTSWITCH) + 1)
                            elif msg.note in FRET_RANGE_SCENE:
                                qc.select_scene(scene=msg.note - min(FRET_RANGE_SCENE) + 1)

                        elif msg.channel == CHANNEL_SETLIST:
                            if PRINT_DEBUG:
                                print(f"[CHANNEL_SETLIST]", end=" ")
                            if msg.note in FRET_RANGE_SETLIST:
                                if (msg.note - min(FRET_RANGE_SETLIST)) >= len(QC_SETLISTS):
                                    if PRINT_DEBUG:
                                        print(f"No index {msg.note - min(FRET_RANGE_SETLIST)} for QC_SETLISTS (len={len(QC_SETLISTS)})")
                                else:
                                    qc.change_setlist(setlist=QC_SETLISTS[msg.note - min(FRET_RANGE_SETLIST)])
                            elif msg.note in FRET_RANGE_PRESET:
                                qc.change_preset(preset_number=msg.note - min(FRET_RANGE_PRESET) + 1)

                        elif msg.channel == CHANNEL_TEMPO:
                            if PRINT_DEBUG:
                                print(f"[CHANNEL_COMMAND]", end=" ")
                            if msg.note in FRET_RANGE_TEMPO:
                                qc.tempo(frequency=msg.note - min(FRET_RANGE_TEMPO) + MIN_QC_TEMPO)


    except Exception as e:
        set_status(f"[ERROR] {e}", error=True)

    set_status("Stopped")


def start():
    global running, midi_thread

    if running:
        return

    input_port = input_var.get()
    output_port = output_var.get()

    if not input_port:
        set_status("[ERROR] no input port selected", error=True)
        return

    if not output_port:
        set_status("[ERROR] no output port selected", error=True)
        return

    if input_port not in mido.get_input_names():
        set_status(f"[ERROR] unknown port '{input_port}'", error=True)
        return

    if output_port not in mido.get_output_names():
        set_status(f"[ERROR] unknown port '{output_port}'", error=True)
        return

    running = True
    midi_thread = threading.Thread(
        target=midi_loop,
        args=(input_port, output_port),
        daemon=True
    )
    midi_thread.start()


def stop():
    global running
    running = False
    set_status("Stopped")


# ---------------- GUI ----------------

root = tk.Tk()
root.title("Quad Cortex MIDI Controller")
root.resizable(False, False)

frame = ttk.Frame(root, padding=12)
frame.grid()

# Input dropdown
ttk.Label(frame, text="Input MIDI Port").grid(row=0, column=0, sticky="w")
input_var = tk.StringVar()
input_combo = ttk.Combobox(
    frame,
    textvariable=input_var,
    values=mido.get_input_names(),
    width=45,
    state="readonly"
)
input_combo.grid(row=1, column=0)
if input_combo["values"]:
    input_combo.current(0)

# Output dropdown
ttk.Label(frame, text="Output MIDI Port").grid(row=2, column=0, sticky="w")
output_var = tk.StringVar()
output_combo = ttk.Combobox(
    frame,
    textvariable=output_var,
    values=mido.get_output_names(),
    width=45,
    state="readonly"
)
output_combo.grid(row=3, column=0)
if output_combo["values"]:
    output_combo.current(0)

# Buttons
button_frame = ttk.Frame(frame)
button_frame.grid(row=4, column=0, pady=10)

ttk.Button(button_frame, text="Start", command=start).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="Stop", command=stop).grid(row=0, column=1, padx=5)

# Status label
status_label = ttk.Label(frame, text="Stopped", foreground="green")
status_label.grid(row=5, column=0)

root.mainloop()
