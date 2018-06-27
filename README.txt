There are three python files: 

1. Part1_Data_Download.py: output URL content and metadata and saved those files in the local computer (Multiple files generated and saved in local computer)

2. Part2_Data_Clean.py: output a file with all the metadata information and saved that file in the local computer. Output file name: all*metadata_map_for_analysis.txt

3. Part3_Data_Analysis.py


Step 1:
pip install Package: requests and bs4

Step2:
Edit HOME_DIR to your local computer location. Make sure that location is empty. HOME_DIR  is defined in all three python programs. Make sure you edit all of them.
HOME_DIR = “/Users/xinmiaotan/PycharmProjects/PythonBerkeley/data”

Step3: 
Run python code sequentially: Part1_Data_Download.py, Part2_Data_Clean.py and Part3_Data_Analysis

Note: 

Your may not want to crawl all the data from Redfin, because that may take a couple days. I also did not finished crawling all the house information in Fremont, California. You can test run the file (Part1_Data_Download.py) and then stop the program. And then run  Part2_Data_Clean.py. But the output you created (all*metadata_map_for_analysis.txt) may not big enough to proceed Part3_Data_Analysis.py. You can replace your all*metadata_map_for_analysis.txt with the one I attached. Mine should be big enough.




