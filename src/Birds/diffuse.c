#include "Python.h"
#include "arrayobject.h"

static PyObject *diffuse(PyObject *self, PyObject *args);

static char module_docstring[] =
    "This module provides an interface for calculating diffusion using C.";
static char diffusion_docstring[] =
    "Return the diffused array calculated from a 2D input array and obstacle array.";

static PyMethodDef module_methods[] = {
    {"diffuse", diffuse, METH_VARARGS, diffusion_docstring},
    {NULL, NULL}
};

PyMODINIT_FUNC initdiffuse(void) {
    Py_InitModule3("diffuse", module_methods, module_docstring);
    /* Load `numpy` functionality. */
    import_array();
}

/* Allocate a double *vector (vec of pointers)
 * Memory is Allocated!  See void free_Carray(double ** )
 */
double **ptrvector(long n)  {
    double **v;
    v=(double **)malloc((size_t) (n*sizeof(double)));
    if (!v)   {
        printf("In **ptrvector. Allocation of memory for double array failed.");
        exit(0);  }
    return v;
}

/* Create Carray from PyArray
 * Assumes PyArray is contiguous in memory.
 * Memory is allocated!
 */
double **pymatrix_to_Carrayptrs(PyArrayObject *arrayin)  {
    double **c, *a;
    int i,n,m;
    
    n=arrayin->dimensions[0];
    m=arrayin->dimensions[1];
    c=ptrvector(n);
    a=(double *) arrayin->data;  /* pointer to arrayin data as double */
    for ( i=0; i<n; i++)  {
        c[i]=a+i*m;  }
    return c;
}

/* Free a double *vector (vec of pointers) */ 
void free_Carrayptrs(double **v)  {
    free((char*) v);
}

static PyObject *diffuse(PyObject *self, PyObject *args) {
    PyArrayObject *metricArray, *obstacleArray, *resultArray;
    double **cMetricArray, **cResultArray, **cObstacleArray;
    int col, row, numCols, numRows, left, right, up, down, obstacleValue;
    int dimensions[2];
    double total, localValue, leftValue, rightValue, upValue, downValue;

    // parse metric and obstacle arrays and check return value
    if (!PyArg_ParseTuple(args, "O!O!", &PyArray_Type, &metricArray, &PyArray_Type, &obstacleArray))
        return NULL;
    if (metricArray == NULL || obstacleArray == NULL)
        return NULL;
    numCols = metricArray->dimensions[0];
    numRows = metricArray->dimensions[1];
    dimensions[0] = numCols;
    dimensions[1] = numRows;
    resultArray = (PyArrayObject *)PyArray_FromDims(2, dimensions, NPY_DOUBLE);
    cMetricArray = pymatrix_to_Carrayptrs(metricArray);
    cObstacleArray = pymatrix_to_Carrayptrs(obstacleArray);
    cResultArray = pymatrix_to_Carrayptrs(resultArray);
    
    for (col = 0; col < numCols; col++) {
        left = col - 1 < 0 ? numCols - 1 : col - 1;
        right = col + 1 >= numCols ? 0 : col + 1;
        for (row = 0; row < numRows; row++) {
            obstacleValue = cObstacleArray[col][row];
            localValue = cMetricArray[col][row];
            if (obstacleValue > 0 && localValue < 1.0) {
                up = row - 1 < 0 ? numRows - 1 : row - 1;
                down = row + 1 >= numRows ? 0 : row + 1;
                leftValue =  cMetricArray[left][row];
                rightValue = cMetricArray[right][row];
                upValue =    cMetricArray[col][up];
                downValue =  cMetricArray[col][down];
                // sum of neighbors
                total = leftValue + rightValue + upValue + downValue;
                // final diffusion value for col, row
                cResultArray[col][row] = 0.2 * total;
            } else {
                cResultArray[col][row] = cMetricArray[col][row];
            }
        }
    }
    
    free_Carrayptrs(cMetricArray);
    free_Carrayptrs(cObstacleArray);
    free_Carrayptrs(cResultArray);
    
    return PyArray_Return(resultArray);
}
