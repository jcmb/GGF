# GGF
 Simple tool for working with Trimble Grid Files
 
	usage: ggf_info.py [-h] [--strict] [--json] [--plot] [--image] GGF

	Geoid File Summary.

	positional arguments:
	 GGF         GGF File to display info on

	optional arguments:
		-h, --help  show this help message and exit
		--strict    Check the file for being strictly valid. If not given use default values
		--json      Output in JSON format.
		--plot      Create a plot of the data.
		--image     Create a image of the data.
		
Where 

- --strict: Validate the the file strictly, checking the flags. Without this default values are used
-  --json: Output to standard out the GGF file in JSON format
-  --plot: Plot the values of the seperations on the screen
- --image: Plot the values of the seperations to a file. The file name is GeoidName.png. Where GeoidName comes from the GGF file