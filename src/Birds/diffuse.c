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

/* Create Carray from PyArray
 * Assumes PyArray is contiguous in memory.
 * Memory is allocated!
 */
double **pymatrix_to_Carrayptrs(PyArrayObject *arrayin)  {
    double **c, *a;
    int i,n,m;
    
    n=arrayin->dimensions[0];
    m=arrayin->dimensions[1];
    // Allocate a double *vector (vec of pointers)
    c = (double **)malloc((size_t) (n*sizeof(double)));
    a = (double *)arrayin->data;  /* pointer to arrayin data as double */
    for (i = 0; i < n; i++)  {
        c[i]=a+i*m;
    }
    return c;
}

/*
 * Diffuse a 2d numpy array using the given number of iterations, rate,
 * metric array and obstacle array.
 
 * Usage: newMetricArray = diffuse(int numIterations, float rate,
 *                                 2dNpAry metricArray, 2dNpAry obstacleAry)
 */
static PyObject *diffuse(PyObject *self, PyObject *args) {
    PyArrayObject *metricArray, *obstacleArray, *resultArray;
    double rate;
    double **cMetricArray, **cResultArray, **cObstacleArray;
    int numIterations, i, col, row, left, right, up, down, numCols, numRows;
    int dimensions[2];

    // parse metric and obstacle arrays and check return value
    if (!PyArg_ParseTuple(args, "idO!O!", &numIterations, &rate,
                          &PyArray_Type, &metricArray,
                          &PyArray_Type, &obstacleArray))
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

    // copy metric array into result array
    for (col = 0; col < numCols; col++) {
        for (row = 0; row < numRows; row++) {
            cResultArray[col][row] = cMetricArray[col][row];
        }
    }
    
    for (i = 0; i < numIterations; i++) {
        for (col = 0; col < numCols; col++) {
            left = col - 1 < 0 ? numCols - 1 : col - 1;
            right = col + 1 >= numCols ? 0 : col + 1;
            for (row = 0; row < numRows; row++) {
                if (cObstacleArray[col][row] > 0.0 && cMetricArray[col][row] < 1.0) {
                    up = row - 1 < 0 ? numRows - 1 : row - 1;
                    down = row + 1 >= numRows ? 0 : row + 1;
                    // final diffusion value for col, row is the sum of neighbors times diffusion rate
                    cResultArray[col][row] = rate * (cResultArray[left][row] +
                                                     cResultArray[right][row] +
                                                     cResultArray[col][up] +
                                                     cResultArray[col][down]);
                }
            }
        }

        // multiply metric array by obstacle array to zero out obstacle cells in each iteration
        for (col = 0; col < numCols; col++) {
            for (row = 0; row < numRows; row++) {
                cResultArray[col][row] *= cObstacleArray[col][row];
            }
        }
    }

    // free allocated memory
    free((char*)cMetricArray);
    free((char*)cObstacleArray);
    free((char*)cResultArray);
    
    return PyArray_Return(resultArray);
}
