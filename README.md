# <img src="icon.png" width="24" alt="App Icon"> Quad Cortex Controller

This Python app allows you to control the Neural DSP Quad Cortex using MIDI input from Guitar Pro via loopMIDI or any virtual MIDI port.

## Instructions
1. Make sure a virtual MIDI cable is set up (loopMIDI or similar).
<img src="Screenshots\01 loopMIDI.png" width="360" alt="screenshot">

2. Configure Guitar Pro MIDI output via "Sound" → "Audio / MIDI Settings..."
<img src="Screenshots\02 Guitar Pro MIDI Settings.png" width="360" alt="screenshot">

3. Add an instrument for each "channel" you want to use for the QC control, and set the output to the MIDI port and channel:
   1. Channel 0 will give you control of: Mode, Gig View, Tuner, Foot-switches, and Scene selection.
   2. Channel 2 will give you control of Setlists and Presets.
   3. Channel 4 will give you control of the Tempo.
<img src="Screenshots\03 Guitar Pro Tracks.png" width="360" alt="screenshot">

4. Start the app, and select the appropriate MIDI input (loopMIDI) and output (Quad Cortex).
<img src="Screenshots\04 QuadCortexController.png" width="360" alt="screenshot">

5. Play notes in Guitar Pro; each note will trigger the assigned Quad Cortex command.
<img src="Screenshots\05 Guitar Pro.png" width="360" alt="screenshot">

### There is a simple Guitar Pro file located "\Tests Files\Quad Cortex MIDI Test.gp", to give you a simple usage example.


## Guitar Pro "Commands"
| MIDI Channel | String      | Frets       | Command                       |
|--------------|-------------|-------------|-------------------------------|
| 0            | 6th string  | 0–2         | Mode (Stomp / Scene / Preset) |
| 0            | 5th string  | 0–4         | Gig View (0=off, 1-4=on)      |
| 0            | 4th string  | 0–4         | Tuner (0=off, 1-4=on)         |
| 0            | 3rd string  | 0–7         | Footswitch                    |
| 0            | 1st string  | 0–7         | Switch Scene                  |
| 2            | 6th string  | 0–23        | Select Setlist                |
| 2            | 1st string  | 0–63        | Select Preset                 |
| 4            | All strings | ≥ 0 (Low E) | Tempo change                  |


## Important Notes
1. Set all instruments to Standard Tuning.
2. Track labels are irrelevant.
3. Guitar Pro's MIDI range is 0–127 → Keep that in mind for Preset or Tempo changes.
4. The low E's value (in a Standard Tuning) is 40 → coincidentally this is the QC's lowest tempo.
5. The Tuner screen and the "Gig View" will be visible ONLY on the QC itself, not on the PC companion.
6. Tempo might be a little off, as there is no direct way to send it, but rather send two commands like a tap tempo.
7. As such, do not send MIDI commands whilst the Tempo is being set (I couldn't make it work asynchronously).


## Requirements

* tkinter (built into Python)
* mido>=1.3.0
* python-rtmidi>=1.5.8
