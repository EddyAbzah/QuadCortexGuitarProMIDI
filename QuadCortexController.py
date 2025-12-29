import time
import mido
import threading

"""
MIDI I/O
--------
find_midi_ports(input|output) → Print all MIDI ports, and (optional) return selected MIDI port names
send_pc(program)              → Send raw Program Change
send_cc(cc, value)            → Send raw Control Change


Triggers
----------------
change_preset(n)              → Load preset (1-based)
change_setlist(name|n)        → Change setlist (setlist name or 1–128)
select_scene(A–H | 1–8)       → Select scene
select_footswitch(A–H | 1–8)  → Trigger footswitch
load_mode(preset|scene|stomp) → Footswitch Mode


Other
-------------
gig_view(on|off)              → Visible only on the QC (not the PC companion)
tuner(on|off)                 → Visible only on the QC (not the PC companion)
tempo(bpm)                    → Tap tempo (2 CC taps)
"""


def find_midi_ports(find_input_port="", find_output_port=""):
    ports = [None, None]

    print("MIDI INPUT PORTS:")
    input_ports = mido.get_input_names()
    if input_ports is not None:
        for name in input_ports:
            print("\t", name)
        if find_input_port != "":
            for name in input_ports:
                if find_input_port.lower() in name.lower():
                    ports[0] = name
    else:
        print("NONE")

    print("\nMIDI OUTPUT PORTS:")
    output_ports = mido.get_output_names()
    if output_ports is not None:
        for name in output_ports:
            print("\t", name)
        if find_output_port != "":
            for name in output_ports:
                if find_output_port.lower() in name.lower():
                    ports[1] = name
    else:
        print("NONE")
    print()

    if find_input_port != "" and ports[0] is None:
        raise RuntimeError(f'\nInput MIDI port "{find_input_port}" is not found')
    elif find_output_port != "" and ports[1] is None:
        raise RuntimeError(f'\nOutput MIDI port "{find_output_port}" is not found')
    else:
        ports = [v for v in ports if v is not None]
        return ports[0] if len(ports) == 1 else ports


class QuadCortexController:
    def __init__(self, port_name=None, channel=0, debug=False):
        if port_name is None:
            port_name = find_midi_ports(find_output_port="Quad Cortex MIDI")

        self.debug = debug
        self.port_name = port_name
        self.channel = channel
        self.out = mido.open_output(self.port_name)
        self._tempo_lock = threading.Lock()
        self._tempo_busy = False
        if self.debug:
            print(f"[QC] Connected to MIDI port: {self.port_name}")
            print(f"[QC] MIDI channel: {self.channel + 1}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.debug:
            print("[QC] Closing MIDI port")
        self.out.close()

    # -------------------------
    # BASIC MIDI SENDERS
    # -------------------------

    def _send_pc(self, program):
        msg = mido.Message("program_change", program=program, channel=self.channel)
        if self.debug:
            print(f"[QC → MIDI] PC {program} (ch {self.channel + 1})")
        self.out.send(msg)

    def _send_cc(self, cc, value):
        msg = mido.Message("control_change", control=cc, value=value, channel=self.channel)
        if self.debug:
            print(f"[QC → MIDI] CC#{cc} = {value} (ch {self.channel + 1})")
        self.out.send(msg)

    # -------------------------
    # HIGH-LEVEL QC COMMANDS
    # -------------------------

    def send_pc(self, program):
        if self.debug:
            print(f"[QC] Send PC → {program}")
        self._send_pc(program)

    def send_cc(self, cc, value):
        if self.debug:
            print(f"[QC] Send CC → {cc} = {value}")
        self._send_cc(cc, value)

    def change_preset(self, preset_number):
        if preset_number < 1:
            raise ValueError("Preset numbers start at 1")

        preset_bank = int(preset_number / 128)
        if self.debug:
            print(f"[QC] Change preset bank → {preset_bank}")
        self._send_cc(0, preset_bank)
        if self.debug:
            print(f"[QC] Change preset → {preset_number}")
        self._send_pc((preset_number - 1) % 128)

    def change_setlist(self, setlist):
        if isinstance(setlist, str):
            setlist_map = {
                "factory_presets": 1,
                "my_presets": 2,
                "artists": 3,
                "users": 4,
                "rabea": 5,
                "neural_dsp": 6,
                "songs": 7
            }
            setlist = setlist_map.get(setlist.lower().replace(" ", "_"))
            if setlist is None:
                raise ValueError("Setlist must be 1–128 or String")
        elif not 1 <= setlist <= 128:
            raise ValueError("Setlist must be 1–128 or String")

        if self.debug:
            print(f"[QC] Change setlist → {setlist}")
        self._send_cc(32, setlist - 1)

    def select_scene(self, scene):
        if isinstance(scene, str):
            scene = ord(scene.upper()) - ord('A') + 1
        if not 1 <= scene <= 8:
            raise ValueError("Scene must be 1–8 or A–H")

        if self.debug:
            print(f"[QC] Select scene → {scene}")
        self._send_cc(43, scene - 1)

    def select_footswitch(self, footswitch):
        if isinstance(footswitch, str):
            footswitch = ord(footswitch.upper()) - ord('A') + 1
        if not 1 <= footswitch <= 8:
            raise ValueError("Footswitch must be 1–8 or A–H")

        if self.debug:
            print(f"[QC] Select Footswitch → {footswitch}")
        # Footswitch A = 35, Footswitch B = 36... Footswitch H = 42
        self._send_cc(34 + footswitch, 0)

    def tuner(self, on: bool):
        state = "ON" if on else "OFF"
        if self.debug:
            print(f"[QC] Tuner → {state}")
        self._send_cc(45, 127 if on else 0)

    def gig_view(self, on: bool):
        state = "ON" if on else "OFF"
        if self.debug:
            print(f"[QC] Gig View → {state}")
        self._send_cc(46, 127 if on else 0)

    def load_mode(self, mode):
        if isinstance(mode, str):
            modes = {"preset": 1, "scene": 2, "stomp": 3}
            mode = mode.lower()
            if mode not in modes:
                raise ValueError('Scene must be 1–3 or: "preset", "scene", or "stomp"')
            mode = modes[mode]
        elif not 1 <= mode <= 3:
            raise ValueError('Scene must be 1–3 or: "preset", "scene", or "stomp"')

        if self.debug:
            print(f"[QC] Load mode → {mode}")
        self._send_cc(47, mode - 1)

    def tempo(self, frequency: int):
        delay_between_taps = 60 / frequency
        if self.debug:
            print(f"[QC] Tempo → {frequency}")
        self._send_cc(44, 0)
        time.sleep(delay_between_taps)
        self._send_cc(44, 0)

    def tempo_asynch(self, frequency: int):
        delay_between_taps = 60 / frequency
        if self.debug:
            print(f"[QC] Tempo → {frequency}")

        with self._tempo_lock:
            if self._tempo_busy:
                return
            self._tempo_busy = True
        self._send_cc(44, 0)

        def second_tap():
            time.sleep(delay_between_taps)
            self._send_cc(44, 0)
            with self._tempo_lock:
                self._tempo_busy = False

        threading.Thread(target=second_tap).start()
