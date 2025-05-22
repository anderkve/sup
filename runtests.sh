
# Test 1d modes

echo
echo
echo "./sup.py graph1d \"x * np.cos(2 * np.pi * x)\" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20 -wb"
./sup.py graph1d "x * np.cos(2 * np.pi * x)" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20 -wb
echo
echo "./sup.py graph1d \"x * np.cos(2 * np.pi * x)\" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20"
./sup.py graph1d "x * np.cos(2 * np.pi * x)" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20

echo
echo
echo "./sup.py hist1d posterior.dat 0 -sz 40 20 -wb"
./sup.py hist1d posterior.dat 0 -sz 40 20 -wb
echo
echo "./sup.py hist1d posterior.dat 0 -sz 40 20"
./sup.py hist1d posterior.dat 0 -sz 40 20

echo
echo
echo "./sup.py post1d posterior.dat 0 -sz 40 20 -wb"
./sup.py post1d posterior.dat 0 -sz 40 20 -wb
echo
echo "./sup.py post1d posterior.dat 0 -sz 40 20"
./sup.py post1d posterior.dat 0 -sz 40 20

echo
echo
echo "./sup.py avg1d posterior.dat 0 1 -sz 40 20 -wb"
./sup.py avg1d posterior.dat 0 1 -sz 40 20 -wb
echo
echo "./sup.py avg1d posterior.dat 0 1 -sz 40 20"
./sup.py avg1d posterior.dat 0 1 -sz 40 20

echo
echo
echo "./sup.py max1d posterior.dat 0 1 -sz 40 20 -wb"
./sup.py max1d posterior.dat 0 1 -sz 40 20 -wb
echo
echo "./sup.py max1d posterior.dat 0 1 -sz 40 20"
./sup.py max1d posterior.dat 0 1 -sz 40 20

echo
echo
echo "./sup.py min1d posterior.dat 0 1 -sz 40 20 -wb"
./sup.py min1d posterior.dat 0 1 -sz 40 20 -wb
echo
echo "./sup.py min1d posterior.dat 0 1 -sz 40 20"
./sup.py min1d posterior.dat 0 1 -sz 40 20

echo
echo
echo "./sup.py plr1d posterior.dat 0 1 -sz 40 20 -wb"
./sup.py plr1d posterior.dat 0 1 -sz 40 20 -wb
echo
echo "./sup.py plr1d posterior.dat 0 1 -sz 40 20"
./sup.py plr1d posterior.dat 0 1 -sz 40 20


# Test 2d modes

echo
echo
echo "./sup.py graph2d \"np.sin(x**2 + y**2) / (x**2 + y**2)\" --x-range -5 5 --y-range -5 5 -sz 40 40 -wb"
./sup.py graph2d "np.sin(x**2 + y**2) / (x**2 + y**2)" --x-range -5 5 --y-range -5 5 -sz 40 40 -wb
echo
echo "./sup.py graph2d \"np.sin(x**2 + y**2) / (x**2 + y**2)\" --x-range -5 5 --y-range -5 5 -sz 40 40"
./sup.py graph2d "np.sin(x**2 + y**2) / (x**2 + y**2)" --x-range -5 5 --y-range -5 5 -sz 40 40

echo
echo
echo "./sup.py hist2d posterior.dat 0 1 -sz 40 40 -wb"
./sup.py hist2d posterior.dat 0 1 -sz 40 40 -wb
echo
echo "./sup.py hist2d posterior.dat 0 1 -sz 40 40"
./sup.py hist2d posterior.dat 0 1 -sz 40 40

echo
echo
echo "./sup.py post2d posterior.dat 0 1 -sz 40 40 -wb"
./sup.py post2d posterior.dat 0 1 -sz 40 40 -wb
echo
echo "./sup.py post2d posterior.dat 0 1 -sz 40 40"
./sup.py post2d posterior.dat 0 1 -sz 40 40

echo
echo
echo "./sup.py avg2d posterior.dat 0 1 2 -sz 40 40 -wb"
./sup.py avg2d posterior.dat 0 1 2 -sz 40 40 -wb
echo
echo "./sup.py avg2d posterior.dat 0 1 2 -sz 40 40"
./sup.py avg2d posterior.dat 0 1 2 -sz 40 40

echo
echo
echo "./sup.py max2d posterior.dat 0 1 2 -sz 40 40 -wb"
./sup.py max2d posterior.dat 0 1 2 -sz 40 40 -wb
echo
echo "./sup.py max2d posterior.dat 0 1 2 -sz 40 40"
./sup.py max2d posterior.dat 0 1 2 -sz 40 40

echo
echo
echo "./sup.py min2d posterior.dat 0 1 2 -sz 40 40 -wb"
./sup.py min2d posterior.dat 0 1 2 -sz 40 40 -wb
echo
echo "./sup.py min2d posterior.dat 0 1 2 -sz 40 40"
./sup.py min2d posterior.dat 0 1 2 -sz 40 40

echo
echo
echo "./sup.py plr2d posterior.dat 0 1 8 -sz 40 40 -wb"
./sup.py plr2d posterior.dat 0 1 8 -sz 40 40 -wb
echo
echo "./sup.py plr2d posterior.dat 0 1 8 -sz 40 40"
./sup.py plr2d posterior.dat 0 1 8 -sz 40 40


