The primary intent of this program is to compare the differences within two regions which may have occurred over time.
The program inputs two (geo)JSON files and compares the polygons within the files.
To have the program work correctly the individual polygons need to have a unique identifier like a name or an ID.

The program returns an output file which contains:
-The new polygons
-The nullified polygons
-the polygons which had a significant change in area

parameters:
-h 		--help			opens Help page
-i 		--ifile1		input file 1 (new File)
-j 		--ifile2		input file 2 (old File)
-n 		--name1			name attribute of file 1
-m		--name2			name attribute of file 2
-o 		--ofile			output file
-p		--percentage 	percentage of how much change in area is counted as signifficant
						the default value is at 5