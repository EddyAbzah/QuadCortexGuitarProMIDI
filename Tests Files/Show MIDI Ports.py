import mido


print("MIDI OUTPUT PORTS:")
for port in mido.get_output_names():
    print("\t", port)

print("\nMIDI INPUT PORTS:")
for port in mido.get_input_names():
    print("\t", port)
