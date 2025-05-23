
# Test 1d modes

echo
echo
echo "sup graph1d \"x * np.cos(2 * np.pi * x)\" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20 -wb"
sup graph1d "x * np.cos(2 * np.pi * x)" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20 -wb
echo
echo "sup graph1d \"x * np.cos(2 * np.pi * x)\" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20"
sup graph1d "x * np.cos(2 * np.pi * x)" --x-range 0.0 2.0 --y-range -2 2 -sz 40 20

echo
echo
echo "sup hist1d posterior.dat 0 -sz 40 20 -wb"
sup hist1d posterior.dat 0 -sz 40 20 -wb
echo
echo "sup hist1d posterior.dat 0 -sz 40 20"
sup hist1d posterior.dat 0 -sz 40 20

echo
echo
echo "sup post1d posterior.dat 0 -sz 40 20 -wb"
sup post1d posterior.dat 0 -sz 40 20 -wb
echo
echo "sup post1d posterior.dat 0 -sz 40 20"
sup post1d posterior.dat 0 -sz 40 20

echo
echo
echo "sup avg1d posterior.dat 0 1 -sz 40 20 -wb"
sup avg1d posterior.dat 0 1 -sz 40 20 -wb
echo
echo "sup avg1d posterior.dat 0 1 -sz 40 20"
sup avg1d posterior.dat 0 1 -sz 40 20

echo
echo
echo "sup max1d posterior.dat 0 1 -sz 40 20 -wb"
sup max1d posterior.dat 0 1 -sz 40 20 -wb
echo
echo "sup max1d posterior.dat 0 1 -sz 40 20"
sup max1d posterior.dat 0 1 -sz 40 20

echo
echo
echo "sup min1d posterior.dat 0 1 -sz 40 20 -wb"
sup min1d posterior.dat 0 1 -sz 40 20 -wb
echo
echo "sup min1d posterior.dat 0 1 -sz 40 20"
sup min1d posterior.dat 0 1 -sz 40 20

echo
echo
echo "sup plr1d posterior.dat 0 1 -sz 40 20 -wb"
sup plr1d posterior.dat 0 8 -sz 40 20 -wb
echo
echo "sup plr1d posterior.dat 0 1 -sz 40 20"
sup plr1d posterior.dat 0 8 -sz 40 20


# Test 2d modes

echo
echo
echo "sup graph2d \"np.sin(x**2 + y**2) / (x**2 + y**2)\" --x-range -5 5 --y-range -5 5 -sz 40 40 -wb"
sup graph2d "np.sin(x**2 + y**2) / (x**2 + y**2)" --x-range -5 5 --y-range -5 5 -sz 40 40 -wb
echo
echo "sup graph2d \"np.sin(x**2 + y**2) / (x**2 + y**2)\" --x-range -5 5 --y-range -5 5 -sz 40 40"
sup graph2d "np.sin(x**2 + y**2) / (x**2 + y**2)" --x-range -5 5 --y-range -5 5 -sz 40 40

echo
echo
echo "sup hist2d posterior.dat 0 1 -sz 40 40 -wb"
sup hist2d posterior.dat 0 1 -sz 40 40 -wb
echo
echo "sup hist2d posterior.dat 0 1 -sz 40 40"
sup hist2d posterior.dat 0 1 -sz 40 40

echo
echo
echo "sup post2d posterior.dat 0 1 -sz 40 40 -wb"
sup post2d posterior.dat 0 1 -sz 40 40 -wb
echo
echo "sup post2d posterior.dat 0 1 -sz 40 40"
sup post2d posterior.dat 0 1 -sz 40 40

echo
echo
echo "sup avg2d posterior.dat 0 1 2 -sz 40 40 -wb"
sup avg2d posterior.dat 0 1 2 -sz 40 40 -wb
echo
echo "sup avg2d posterior.dat 0 1 2 -sz 40 40"
sup avg2d posterior.dat 0 1 2 -sz 40 40

echo
echo
echo "sup max2d posterior.dat 0 1 2 -sz 40 40 -wb"
sup max2d posterior.dat 0 1 2 -sz 40 40 -wb
echo
echo "sup max2d posterior.dat 0 1 2 -sz 40 40"
sup max2d posterior.dat 0 1 2 -sz 40 40

echo
echo
echo "sup min2d posterior.dat 0 1 2 -sz 40 40 -wb"
sup min2d posterior.dat 0 1 2 -sz 40 40 -wb
echo
echo "sup min2d posterior.dat 0 1 2 -sz 40 40"
sup min2d posterior.dat 0 1 2 -sz 40 40

echo
echo
echo "sup plr2d posterior.dat 0 1 8 -sz 40 40 -wb"
sup plr2d posterior.dat 0 1 8 -sz 40 40 -wb
echo
echo "sup plr2d posterior.dat 0 1 8 -sz 40 40"
sup plr2d posterior.dat 0 1 8 -sz 40 40


