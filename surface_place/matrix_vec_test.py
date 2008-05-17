import math

'''
Multiplies a matrix by a vector (both are represented by list data
structure).

Code from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/121574
by Xunning Yue (19th April 2002)
Note: There could possibly be a better way of doing this now in 2008.

@param matrix
@param vector
@return list multiplied vector
'''
def multiply_matrix_by_vector(m, v):
	nrows = len(m)
	ncols = len(m[0])
	w = [None] * nrows
	for row in range(nrows):
		sum = 0
		for col in range(ncols):
			sum += m[row][col]*v[col]
			w[row] = sum
	return w

def main():
	#m, n = 2, 2
	#vec = range(1, n+1)
	#mat = [map(lambda x: i*n+x+1, range(n)) for i in range(m)]
	#print 'vec=', vec
	#print 'mat=', mat
	#print 'mat . vec=', multiply_matrix_by_vector(vec, mat)

	#NOTE: All of these rotation matrices follow the left-hand rule.

	#Testing x-axis rotation
	vec = [0.0, 1.0, 0.0] #(x, y, z)
	w = math.radians(90.0)
	mat = [
			[1.0, 0.0, 0.0],
			[0.0, math.cos(w), math.sin(w)],
			[0.0, -math.sin(w), math.cos(w)]
			]
	print 'vec=', vec
	print 'mat=', mat
	print 'mat . vec=', multiply_matrix_by_vector(mat, vec)

	#Testing y-axis rotation
	vec = [1.0, 0.0, 0.0] #(x, y, z)
	w = math.radians(90.0)
	mat = [
			[math.cos(w), 0.0, -math.sin(w)],
			[0.0, 1.0, 0.0],
			[math.sin(w), 0.0, math.cos(w)]
			]
	print 'vec=', vec
	print 'mat=', mat
	print 'mat . vec=', multiply_matrix_by_vector(mat, vec)

	#Testing z-axis rotation
	vec = [1.0, 0.0, 0.0] #(x, y, z)
	w = math.radians(90.0)
	mat = [
			[math.cos(w), math.sin(w), 0.0],
			[-math.sin(w), math.cos(w), 0.0],
			[0.0, 0.0, 1.0]
			]
	print 'vec=', vec
	print 'mat=', mat
	print 'mat . vec=', multiply_matrix_by_vector(mat, vec)

	#Testing 3d rotation matrix
	#vec = [1.0, 0.0, 0.0] #(x, y, z)
	#rx = math.radians(90.0)
	#ry = 0.0
	#rz = 0.0 #math.radians(90.0)
	#mat = [
	#		[math.cos(ry)*math.cos(rz), math.cos(rx)*math.sin(rz)+math.sin(rx)*math.sin(ry)*math.cos(rz), math.sin(rx)*math.sin(rz)-math.cos(rx)*math.sin(ry)*math.cos(rz)],
	#		[-math.cos(ry)*math.sin(rz), math.cos(rx)*math.cos(rz)-math.sin(rx)*math.sin(ry)*math.sin(rz), math.sin(rx)*math.cos(rz)+math.cos(rx)*math.sin(ry)*math.sin(rz)],
	#		[math.sin(ry), -math.sin(rx)*math.cos(ry), math.cos(rx)*math.cos(ry)]
	#		]
	#print 'vec=', vec
	#print 'mat=', mat
	#print 'mat . vec=', multiply_matrix_by_vector(mat, vec)


if __name__ == '__main__':
	main()
