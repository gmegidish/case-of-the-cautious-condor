"""
    Extract CEL sprites and AUD samples from RTF
    Copyright (C) 2010 Gil Megidish

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import glob
import os.path
import struct
import sys
from PIL import Image

files = glob.glob("*.RTF")
files.sort()

#files = sys.argv
#files.pop(0)

for file in files:
	print "Opening %s" % file
	f = open(file, "rb")
	signature = f.read(4)
	if signature != "CD  ":
		continue
	
	f.seek(0x1a, 0)
	first_tag = struct.unpack(">H", f.read(2))[0]
	f.seek(first_tag+0x20, 0)

	palette = []
	frame = 1

	split = os.path.splitext(file)  	
	rawfile = "%s.raw" % (split[0])
	if os.path.exists(rawfile):
		os.unlink(rawfile)

	has_audio = False
	hz = None
	last_screen = Image.new("P", (320, 200))

	while True:
		tag = f.read(4)
		if tag == "":
			break

		if tag == "CLUT":
			f.read(2) # num colors
			raw = f.read(32 * 2);

			palette = [0] * 768
			for i in range(32):
				rgb = (ord(raw[i*2+0]) << 8) | ord(raw[i*2+1])
				r = ((rgb >> 8) & 0xf) << 4
				g = ((rgb >> 4) & 0xf) << 4
				b = ((rgb >> 0) & 0xf) << 4
				palette[i*3+0] = r
				palette[i*3+1] = g
				palette[i*3+2] = b

			last_screen.putpalette(palette)

		elif tag == "CEL ":
			header = f.read(0x6a)
			height = struct.unpack(">H", header[6:8])[0]
			width = struct.unpack(">H", header[8:10])[0]
			print "\tCEL%d x %d" % (width, height)
			
			im = Image.new("P", (width, height))
			raw = f.read((width * height * 5) >> 3)

			"""
			offset = 0
			for y in range(im.size[1]):
				for x in range(im.size[0]):
					xmod8 = 7 - (x & 7)
					xdiv8 = (offset >> 3)
					ypass = ((width*height) >> 3)

					c0 = (ord(raw[xdiv8+ypass*0]) >> xmod8) & 1
					c1 = (ord(raw[xdiv8+ypass*1]) >> xmod8) & 1
					c2 = (ord(raw[xdiv8+ypass*2]) >> xmod8) & 1
					c3 = (ord(raw[xdiv8+ypass*3]) >> xmod8) & 1
					c4 = (ord(raw[xdiv8+ypass*4]) >> xmod8) & 1
					c = (c4 << 4) | (c3 << 3) | (c2 << 2) | (c1 << 1) | (c0 << 0)
					im.putpixel((x, y), c)

					if c != 0:
						last_screen.putpixel((x, y), c)

					offset = offset + 1

			im.putpalette(palette)
			
			split = os.path.splitext(file)
			im.save("%s.%04d.png" % (split[0], frame))

			# uncomment the next like to generate raster png
			# last_screen.save("%s.raster-%04d.png" % (split[0], frame))
			"""

			frame = frame + 1

		elif tag == "AUD ":
			header = f.read(0x1c)
			if hz is None:
				hz = struct.unpack(">H", header[0x0c:0x0e])[0]

			size = struct.unpack(">I", header[0x12:0x16])[0]
			bytes = f.read(size)
			split = os.path.splitext(file)
			rawfile = "%s.raw" % (split[0])
			f2 = open(rawfile, "a+b")
			f2.write(bytes)
			f2.close()
			has_audio = True

	if has_audio:
		rawfile = "%s.raw" % (split[0])
		wavfile = "%s.wav" % (split[0])
		print "\tAudio is %d hz" % hz
		os.system("sox -s -b 8 -c 1 -r %d %s %s" % (hz, rawfile, wavfile))
		os.unlink(rawfile)
