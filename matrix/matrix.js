"use strict"

//* Matrix

export class Matrix extends Float32Array {

    /**
     * A matrix representation based on Float32Array to easely manipulate geometry.
     * @param {Number} n Number of rows
     * @param {Number} m Number of cols
     * @param {Array} array Content
     */
    constructor(n, m = n, array) {
        super(n * m);
        this.rows = n;
        this.cols = m;
        Object.assign(this, array);
    }

    /**
     * Create a new matrix without the i row
     * @param {Number} i Index of the row
     * @param {Matrix} matrix Matrix filled
     * @returns {Matrix}
     */
    delRow(i, matrix = new Matrix(this.rows - 1, this.cols)) {
        const array = [...this];
        array.splice(i * this.cols, this.cols);
        Object.assign(matrix, array);
        return matrix
    }

    /**
     * Create a new matrix without the i colone
     * @param {Number} i Index of the colone
     * @param {Matrix} matrix Matrix filled
     * @returns {Matrix}
     */
    delCol(i, matrix = new Matrix(this.rows, this.cols - 1)) {
        const array = [...this];
        for (let j = 0; j < this.rows; j++) array.splice(j * this.cols + i--, 1);
        Object.assign(matrix, array);
        return matrix
    }

    /**
     * Get the determinant of the matrix (ported from : https://integratedmlai.com/find-the-determinant-of-a-matrix-with-pure-python-without-numpy-or-scipy/)
     * @param {Matrix} matrix Default to this
     * @returns {Number} The determinant
     */
    det(matrix = this) {
        if (matrix.rows === 2 && matrix.cols === 2) return matrix[0] * matrix[3] - matrix[1] * matrix[2];
        let det = 0;
        const subMatrix = matrix.delRow(0);
        for (let i = 0; i < matrix.cols; i++) det += matrix[i] * this.det(subMatrix.delCol(i)) * (i % 2 ? -1 : 1);
        return det
    }

    /**
     * Transpos matrix
     * @returns {Matrix}
     */
    transpos() {
        const transMatrix = new Matrix(this.cols, this.rows);
        for (let i = 0; i < this.rows; i++) {
            for (let j = 0; j < this.cols; j++) {
                transMatrix[j * transMatrix.cols + i] = this[i * this.cols + j];
            }
        }
        return transMatrix
    }

    /**
     * Create his minor matrix (need a square matrix)
     * @returns {Matrix} The minor matrix
     */
    minor() {
        const minorMatrix = new Matrix(this.rows, this.cols);
        if (this.rows === 2 && this.cols === 2) {
            minorMatrix[0] = this[3];
            minorMatrix[1] = -this[2];
            minorMatrix[2] = -this[1];
            minorMatrix[3] = this[0];
            return minorMatrix;
        };
        for (let i = 0; i < this.rows; i++) {
            for (let j = 0; j < this.cols; j++) {
                minorMatrix[i * this.cols + j] = this.det(this.delRow(i).delCol(j)) * ((i + j) % 2 === 0 ? 1 : -1);
            }
        }
        return minorMatrix
    }

    /**
     * Create his adjugate matrix (need a square matrix)
     * @returns {Matrix} The adjugate matrix
     */
    adj() {
        return this.minor().transpos()
    }

    /**
     * Invert itself (need to be a square matrix)
     * @returns {Matrix} This
     */
    invert() {
        const det = this.det();
        if (det === null) return;
        const invertMatrix = this.adj();
        for (let i = 0; i < invertMatrix.length; i++) invertMatrix[i] /= det;
        return invertMatrix
    }

    /**
     * Sum with another matrix (must share the same dimensions)
     * @param {Matrix} matrix 
     * @returns The resulted matrix
     */
    sum(matrix) {
        const sumMatrix = new Matrix(this.rows, this.cols);
        for (let i = 0; i < this.length; i++) sumMatrix[i] = this[i] + matrix[i];
        return sumMatrix
    }

    /**
     * Substract by another matrix (must share the same dimensions)
     * @param {Matrix} matrix 
     * @returns The resulted matrix
     */
    sub(matrix) {
        const subMatrix = new Matrix(this.rows, this.cols);
        for (let i = 0; i < this.length; i++) subMatrix[i] = this[i] - matrix[i];
        return subMatrix
    }

    /**
     * Naive matrix multiplycation algorithm: O(n^3)
     * @param {Matrix} matrix The other matrix
     * @returns {Matrix} The resulted matrix
     */
    mult(matrix) {
        if (matrix.rows !== this.cols) return;
        const multMatrix = new Matrix(this.rows, matrix.cols);
        for (let i = 0; i < this.rows; i++) {
            for (let j = 0; j < matrix.cols; j++) {
                for (let k = 0; k < this.cols; k++) {
                    multMatrix[multMatrix.cols * i + j] += this[this.cols * i + k] * matrix[matrix.cols * k + j]
                }
            }
        }
        return multMatrix
    }

    /**
     * Divide by another matrix (must share at least one dimension in common)
     * @param {Matrix} matrix The other matrix
     * @returns {Matrix} The resulted matrix
     */
    div(matrix) {
        return this.mult(matrix.invert())
    }

    /**
     * Multipliate each value by a scalar number
     * @param {Number} n 
     * @returns {Matrix} This
     */
    scale(n) {
        const scaleMatrix = new Matrix(this.rows, this.cols);
        for (let i = 0; i < this.length; i++) scaleMatrix[i] = this[i] * n;
        return scaleMatrix
    }

    /**
     * Round each value
     */
    round(precision = 10e3) {
        for (let i = 0; i < this.length; i++) this[i] = Math.round(this[i] * precision) / precision;
        return this
    }

    /**
     * Create a more readable matrix
     * @returns This in the form of : Array [ Array ]
     */
    toTab() {
        let content = new Array(this.rows);
        for (let i = 0; i < this.rows; i++) {
            content[i] = new Array(this.cols);
            for (let j = 0; j < this.cols; j++) {
                content[i][j] = this[i * this.cols + j];
            }
        }
        return content
    }
}

export class IdentityMatrix extends Matrix {
    /**
     * An identity matrix
     */
    constructor(n) {
        super(n, n);
        let i = 0;
        for (let j = 0; j < n; j++) {
            this[i + j] = 1;
            i += n
        }
    }
}

export class TransformMatrix extends Matrix {
    constructor() {
        super(4, 4);
    }

    scale(sx, sy, sz) {
        return this.mult(new ScalingMatrix(sx, sy, sz))
    }

    rotateX(rad) {
        const s = Math.sin(rad),
            c = Math.cos(rad),
            a10 = this[4],
            a11 = this[5],
            a12 = this[6],
            a13 = this[7],
            a20 = this[8],
            a21 = this[9],
            a22 = this[10],
            a23 = this[11];
        this[4] = a10 * c + a20 * s;
        this[5] = a11 * c + a21 * s;
        this[6] = a12 * c + a22 * s;
        this[7] = a13 * c + a23 * s;
        this[8] = a20 * c - a10 * s;
        this[9] = a21 * c - a11 * s;
        this[10] = a22 * c - a12 * s;
        this[11] = a23 * c - a13 * s;
    }

    rotateY(rad) {
        const s = Math.sin(rad),
            c = Math.cos(rad),
            a00 = this[0],
            a01 = this[1],
            a02 = this[2],
            a03 = this[3],
            a20 = this[8],
            a21 = this[9],
            a22 = this[10],
            a23 = this[11];

        this[0] = a00 * c - a20 * s;
        this[1] = a01 * c - a21 * s;
        this[2] = a02 * c - a22 * s;
        this[3] = a03 * c - a23 * s;
        this[8] = a00 * s + a20 * c;
        this[9] = a01 * s + a21 * c;
        this[10] = a02 * s + a22 * c;
        this[11] = a03 * s + a23 * c;
    }

    rotateZ(rad) {
        const s = Math.sin(rad),
            c = Math.cos(rad),
            a00 = this[0],
            a01 = this[1],
            a02 = this[2],
            a03 = this[3],
            a10 = this[4],
            a11 = this[5],
            a12 = this[6],
            a13 = this[7];

        this[0] = a00 * c + a10 * s;
        this[1] = a01 * c + a11 * s;
        this[2] = a02 * c + a12 * s;
        this[3] = a03 * c + a13 * s;
        this[4] = a10 * c - a00 * s;
        this[5] = a11 * c - a01 * s;
        this[6] = a12 * c - a02 * s;
        this[7] = a13 * c - a03 * s;
    }
}

export class ScalingMatrix extends TransformMatrix {
    /**
     * Scalar matrix
     * @param {Number} sx 
     * @param {Number} sy 
     * @param {Number} sz 
     */
    constructor(sx, sy, sz) {
        super();
        this[0] = sx;
        this[5] = sy;
        this[10] = sz;
        this[15] = 1;
    }
}

export class PerspectiveMatrix extends TransformMatrix {
    /**
     * Perspective projection matrix
     * @param {Number} fov 
     * @param {Number} ratio 
     * @param {Number} near 
     * @param {Number} far 
     */
    constructor(fov, ratio, near, far) {
        super();
        this[11] = -1;
        this.ratio = ratio;
        this.setFov(fov);
        this.setDepth(near, far);
    }
    /**
     * Set fov
     * @param {Number} fov 
     */
    setFov(fov) {
        this.f = 1 / Math.tan(fov * .5);
        this[5] = -this.f; // Get y coord positive on top and negative under 
        this.setAspectRatio(this.ratio);
    }
    /**
     * Set depth
     * @param {Number} near 
     * @param {Number} far 
     */
    setDepth(near, far) {
        if (far != null && far != Infinity) {
            let nf = 1 / (near - far);
            this[10] = (far + near) * nf;
            this[14] = 2 * far * near * nf;
        } else {
            this[10] = -1
            this[14] = -2 * near
        }
    }
    /**
     * Set aspect ratio
     * @param {Number} ratio 
     */
    setAspectRatio(ratio) {
        this[0] = this.f / ratio;
        this.ratio = ratio;
    }
}

export class OrthogonalMatrix extends TransformMatrix {

    /**
     * Orthographic projection matrix
     * @param {Number} ratio 
     */
    constructor(ratio) {
        super();
        this[5] = -1; // Get y coord positive on top and negative under 
        this[10] = -10e-2; // Need a little offset to do depth test 
        this[14] = -1;
        this[15] = 1;
        this.setAspectRatio(ratio);
    }
    /**
     * Set aspect ratio
     * @param {Number} ratio 
     */
    setAspectRatio(ratio) {
        this[0] = 1 / ratio;
    }
}
