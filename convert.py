#!/usr/bin/env python3
import argparse
from pathlib import Path

import mido
from kellog import info, warning, error, debug

# ==================================================================================================
def main(args):
	converter = MIDIConverter(args.input_file)
	if args.title:
		converter.title = args.title
	commands = converter.convert()
	print(commands)


# ==================================================================================================
class MIDIConverter():
	A4 = 69
	A4Hz = 440
	notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
	# ----------------------------------------------------------------------------------------------
	def __init__(self, path: Path):
		self.currentNote = None
		self.currentTime = None
		self.mid = mido.MidiFile(path)
		self.title = None
		self.commands = []

	# ----------------------------------------------------------------------------------------------
	def convert(self):
		self.commands = []
		if self.title:
			self.commands += [
				f";{'-' * 49}",
				f"; {self.title}",
				f";{'-' * 49}",
			]
		try:
			for msg in self.mid:
				if not msg.is_meta:
					if msg.type == "note_on":
						assert self.currentNote is None and self.currentTime is None
						self.currentNote = msg.note
						self.currentTime = msg.time
					elif msg.type == "note_off":
						assert msg.note == self.currentNote
						self.currentNote = None
						duration = msg.time - self.currentTime
						self.currentTime = None
						self.commands += [self.form_command(msg.note, duration, self.note_to_octave(msg.note), self.note_to_semitone(msg.note))]
		except:
			error("Can only one note at a time!")
			raise

		return "\n".join(self.commands)

	# ----------------------------------------------------------------------------------------------
	@classmethod
	def form_command(cls, note: int, duration: int, octave: int, semitone: int):
		comment = f"{cls.notes[semitone]}{octave}"

		return f"M300 {int(duration * 1e3)} {round(cls.note_to_freq(note))} ; {comment}"

	# ----------------------------------------------------------------------------------------------
	@classmethod
	def note_to_freq(cls, note: int) -> float:
		octaves = cls.note_to_octave(note) - cls.note_to_octave(cls.A4)
		semitones = cls.note_to_semitone(note) - cls.note_to_semitone(cls.A4)
		distance = (octaves * 12) + semitones
		freq = cls.A4Hz * 2 ** (distance / 12)

		return freq


	# ----------------------------------------------------------------------------------------------
	@staticmethod
	def note_to_octave(note: int):
		return (note - 12) // 12

	# ----------------------------------------------------------------------------------------------
	@staticmethod
	def note_to_semitone(note: int):
		return note % 12


# ==================================================================================================
def parse_args():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("input_file", type=Path, help="Input MIDI file")
	parser.add_argument("-t", "--title", type=str, help="Title to put in a comment")

	return parser.parse_args()


# ==================================================================================================
if __name__ == "__main__":
	main(parse_args())
