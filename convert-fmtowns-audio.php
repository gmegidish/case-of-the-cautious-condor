<?
	array_shift($argv);

	$to = "";
	$from = "";
	for ($i=0; $i<=255; $i++)
	{
		$from .= chr($i);
		$to .= ($i & 0x80) ? chr($i & 0x7f) : chr(0xff - $i);
	}

	foreach($argv as $filename)
	{
		print "Converting $filename ..\n";

		$f = file_get_contents($filename);
		$header = substr($f, 0, 0x20);
		$rate = unpack("v", substr($header, 0x18, 2));
		$rate = 10 * $rate[1];
		if ($rate != 19600)
		{
			print "WARNING: $filename has sample rate of $rate, please check manually\n";
		}

		$rate = 11025;

		$raw = substr($f, 0x20);
		//$raw = strtr($raw, $from, $to);

		file_put_contents(".dummy.raw", $raw);
		system("sox -c 1 -r $rate -u -b 8 .dummy.raw $filename.wav");
		unlink(".dummy.raw");
	}
?>