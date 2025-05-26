# Run this script from the main (parent) directory, i.e. do "sh tests/runstests.sh"


# Test 1D modes
echo
echo
echo "#################"
echo "# Test 1D modes #"
echo "#################"

echo
echo "Testing: sup graph1d \"x * np.cos(2 * np.pi * x)\" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20 -wb"
sup graph1d "x * np.cos(2 * np.pi * x)" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup graph1d \"x * np.cos(2 * np.pi * x)\" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20"
sup graph1d "x * np.cos(2 * np.pi * x)" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup hist1d tests/posterior.dat 0 -sz 40 20 -wb"
sup hist1d tests/posterior.dat 0 -sz 40 20 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup hist1d tests/posterior.dat 0 -sz 40 20"
sup hist1d tests/posterior.dat 0 -sz 40 20 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup post1d tests/posterior.dat 0 -sz 40 20 -wb"
sup post1d tests/posterior.dat 0 -sz 40 20 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup post1d tests/posterior.dat 0 -sz 40 20"
sup post1d tests/posterior.dat 0 -sz 40 20 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup avg1d tests/posterior.dat 0 1 -sz 40 20 -wb"
sup avg1d tests/posterior.dat 0 1 -sz 40 20 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup avg1d tests/posterior.dat 0 1 -sz 40 20"
sup avg1d tests/posterior.dat 0 1 -sz 40 20 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup max1d tests/posterior.dat 0 1 -sz 40 20 -wb"
sup max1d tests/posterior.dat 0 1 -sz 40 20 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup max1d tests/posterior.dat 0 1 -sz 40 20"
sup max1d tests/posterior.dat 0 1 -sz 40 20 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup min1d tests/posterior.dat 0 1 -sz 40 20 -wb"
sup min1d tests/posterior.dat 0 1 -sz 40 20 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup min1d tests/posterior.dat 0 1 -sz 40 20"
sup min1d tests/posterior.dat 0 1 -sz 40 20 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup plr1d tests/posterior.dat 0 1 -sz 40 20 -wb"
sup plr1d tests/posterior.dat 0 8 -sz 40 20 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup plr1d tests/posterior.dat 0 1 -sz 40 20"
sup plr1d tests/posterior.dat 0 8 -sz 40 20 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi


# Test 2D modes
echo
echo
echo "#################"
echo "# Test 2D modes #"
echo "#################"

echo
echo "Testing: sup graph2d \"np.sin(x**2 + y**2) / (x**2 + y**2)\" --x-range -5 5 --y-range -5 5 -sz 40 40 -wb"
sup graph2d "np.sin(x**2 + y**2) / (x**2 + y**2)" --x-range -5 5 --y-range -5 5 -sz 40 40 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup graph2d \"np.sin(x**2 + y**2) / (x**2 + y**2)\" --x-range -5 5 --y-range -5 5 -sz 40 40"
sup graph2d "np.sin(x**2 + y**2) / (x**2 + y**2)" --x-range -5 5 --y-range -5 5 -sz 40 40 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup hist2d tests/posterior.dat 0 1 -sz 40 40 -wb"
sup hist2d tests/posterior.dat 0 1 -sz 40 40 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup hist2d tests/posterior.dat 0 1 -sz 40 40"
sup hist2d tests/posterior.dat 0 1 -sz 40 40 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup post2d tests/posterior.dat 0 1 -sz 40 40 -wb"
sup post2d tests/posterior.dat 0 1 -sz 40 40 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup post2d tests/posterior.dat 0 1 -sz 40 40"
sup post2d tests/posterior.dat 0 1 -sz 40 40 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup avg2d tests/posterior.dat 0 1 2 -sz 40 40 -wb"
sup avg2d tests/posterior.dat 0 1 2 -sz 40 40 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup avg2d tests/posterior.dat 0 1 2 -sz 40 40"
sup avg2d tests/posterior.dat 0 1 2 -sz 40 40 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup max2d tests/posterior.dat 0 1 2 -sz 40 40 -wb"
sup max2d tests/posterior.dat 0 1 2 -sz 40 40 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup max2d tests/posterior.dat 0 1 2 -sz 40 40"
sup max2d tests/posterior.dat 0 1 2 -sz 40 40 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup min2d tests/posterior.dat 0 1 2 -sz 40 40 -wb"
sup min2d tests/posterior.dat 0 1 2 -sz 40 40 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup min2d tests/posterior.dat 0 1 2 -sz 40 40"
sup min2d tests/posterior.dat 0 1 2 -sz 40 40 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup plr2d tests/posterior.dat 0 1 8 -sz 40 40 -wb"
sup plr2d tests/posterior.dat 0 1 8 -sz 40 40 -wb > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup plr2d tests/posterior.dat 0 1 8 -sz 40 40"
sup plr2d tests/posterior.dat 0 1 8 -sz 40 40 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi


# Test stdin modes
echo
echo
echo "####################"
echo "# Test stdin modes #"
echo "####################"

echo
echo "Testing: cat tests/sample_pipe.txt | sup hist1d - 0 --stdin-format txt --delimiter \" \" -sz 30 10"
cat tests/sample_pipe.txt | sup hist1d - 0 --stdin-format txt --delimiter " " -sz 30 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: cat tests/sample_pipe.csv | sup hist1d - 0 --stdin-format csv -sz 30 10"
cat tests/sample_pipe.csv | sup hist1d - 0 --stdin-format csv -sz 30 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: cat tests/sample_pipe.csv | sup list - --stdin-format csv"
cat tests/sample_pipe.csv | sup list - --stdin-format csv > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi


# Test stdin error handling
echo
echo
echo "#############################"
echo "# Test stdin error handling #"
echo "#############################"

echo
echo "Testing: sup hist1d - 0 # Expect error: missing --stdin-format"
sup hist1d - 0

echo
echo "Testing: sup hist1d - 0 --stdin-format hdf5 # Expect error: hdf5 from stdin not supported"
sup hist1d - 0 --stdin-format hdf5

echo
echo "Testing: cat tests/sample_pipe.txt | sup hist1d - 0 --stdin-format txt --watch 1 # Expect error: watch mode with stdin"
cat tests/sample_pipe.txt | sup hist1d - 0 --stdin-format txt --watch 1


# Test CSV and JSON inputs
echo
echo
echo "#################################"
echo "# Test CSV and JSON input modes #"
echo "#################################"

# CSV Tests
echo
echo "Testing: sup list tests/sample.csv"
sup list tests/sample.csv > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup hist1d tests/sample.csv 0 --x-range 0 1 --size 10 10"
sup hist1d tests/sample.csv 0 --x-range 0 1 --size 10 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup hist2d tests/sample.csv 1 2 --x-range 0 20 --y-range 15 25 --size 10 10"
sup hist2d tests/sample.csv 1 2 --x-range 0 20 --y-range 15 25 --size 10 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup hist1d tests/sample.csv 0 -f 3 --x-range 0 1 --size 10 10"
sup hist1d tests/sample.csv 0 -f 3 --x-range 0 1 --size 10 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing CSV hist1d mode via stdin..."
cat tests/sample.csv | sup hist1d - 0 --stdin-format csv --x-range 0 1 --size 10 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi


# JSON Object of Arrays Tests
echo
echo "Testing: sup list tests/sample_object.json"
sup list tests/sample_object.json > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup hist1d tests/sample_object.json 0 --x-range 0 1 --size 10 10"
sup hist1d tests/sample_object.json 0 --x-range 0 1 --size 10 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup hist2d tests/sample_object.json 1 2 --x-range 0 20 --y-range 15 25 --size 10 10"
sup hist2d tests/sample_object.json 1 2 --x-range 0 20 --y-range 15 25 --size 10 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: cat tests/sample_object.json | sup hist1d - 0 --stdin-format json --x-range 0 1 --size 10 10"
cat tests/sample_object.json | sup hist1d - 0 --stdin-format json --x-range 0 1 --size 10 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

# JSON List of Records Tests
echo
echo "Testing: sup list tests/sample_records.json"
sup list tests/sample_records.json > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup hist1d tests/sample_records.json 0 --x-range 0 1 --size 10 10"
sup hist1d tests/sample_records.json 0 --x-range 0 1 --size 10 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: sup hist2d tests/sample_records.json 1 2 --x-range 0 20 --y-range 15 25 --size 10 10"
sup hist2d tests/sample_records.json 1 2 --x-range 0 20 --y-range 15 25 --size 10 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi

echo "Testing: cat tests/sample_records.json | sup hist1d - 0 --stdin-format json --x-range 0 1 --size 10 10"
cat tests/sample_records.json | sup hist1d - 0 --stdin-format json --x-range 0 1 --size 10 10 > /dev/null
if [ $? -ne 0 ]; then echo "Test FAILED"; exit 1; fi


echo
echo
echo "##############"
echo "# Tests done #"
echo "##############"
echo

