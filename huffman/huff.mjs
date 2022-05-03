"use strict"

/**
 * A simple implementation of Huffman tree, work fine with String & Array of String.
 * This have some part of the worst code possible (especially in encode / decode function),
 * due to the non bit manipulation support in js.
 * @author Lucas Maillet
 */

import { inspect } from "util";

const X_SPACE = 2,
    Y_SPACE = 0,
    X_INDENT = ' '.repeat(X_SPACE),
    X_STROKE = '─'.repeat(X_SPACE),
    DECO_WEIGHT = "\x1b[33m",
    END = "\x1b[0m";

//* Class

class Leaf {

    /** @type {Number} */
    #weight

    /**
    * Create a leaf of the tree
    * @param {Any} content
    * @param {Number} weight 
    */
    constructor(content, weight) {
        /** @type {Any} */
        this.content = content;
        this.#weight = weight;
    }

    /**
     * Hidded function to get node depth
     * @param {Number} depthOffset Starting depth
     * @return {Number}
     */
    _depth(depthOffset) {
        return depthOffset + 1
    }

    /**
     * Hidded function to generate a visualisation of the tree
     * @returns {String}
     */
    _toTree() {
        return ` ${DECO_WEIGHT + this.#weight + END} ${X_STROKE}╼ ${inspect(this.content, { colors: true })}`
    }

    /**
     * Get weight
     * @returns {Number}
     */
    [Symbol.toPrimitive]() {
        return this.#weight
    }

    /**
     * Fill a CodeMap with the binary code corresponding to the leaf
     * @param {CodeMap} codeMap
     * @param {String} bits
     */
    setBits(codeMap, bits) {
        codeMap.charMap.set(this.content, bits);
        codeMap.binMap.set(bits, this.content);
    }
}

class Node extends Array {

    /** @type {Number} */
    #weight

    /**
     * Create a node of the tree
     * @param {Array<Node | Leaf>} content
     * @param {Number} weight 
     */
    constructor(content, weight) {
        super(...content);
        this.#weight = weight;
    }

    /**
     * Hidded function to get node depth
     * @param {Number} depthOffset Starting depth
     */
    _depth(depthOffset) {
        return Math.max(this[0]._depth(depthOffset + 1), this[1]._depth(depthOffset + 1))
    }

    /**
     * Hidded function to generate a visualisation of the tree
     * @param {String} lineOffset Starting lineOffset
     * @returns {String}
     */
    _toTree(lineOffset) {
        const yIndent = `${lineOffset}${`│\n${lineOffset}`.repeat(Y_SPACE)}`;
        return `┮ ${DECO_WEIGHT + this + END}\n${yIndent}├${X_STROKE}${this[0]._toTree(`${lineOffset}│${X_INDENT}`)}\n${yIndent}└${X_STROKE}${this[1]._toTree(`${lineOffset} ${X_INDENT}`)}`
    }

    /**
     * Get depth
     * @return {Number}
     */
    get depth() {
        return this._depth(0);
    }

    /**
     * Get a visual representation of the tree
     * @return {String}
     */
    get tree() {
        return this._toTree("");
    }

    /**
     * Get weight
     * @returns {Number}
     */
    [Symbol.toPrimitive]() {
        return this.#weight
    }

    /**
     * Fill a CodeMap with the binary code mapping to the tree's leafs
     * @param {CodeMap} codeMap
     * @param {String} bits
     */
    setBits(codeMap, bits,) {
        this[0].setBits(codeMap, `${bits}0`);
        this[1].setBits(codeMap, `${bits}1`);
    }
}

class Root extends Node {

    /** @type {Number} */
    #weight

    /**
     * Create an accurate Huffman tree
     * @param {Map} occurence 
     */
    constructor(occurence) {
        // Create nodes
        super([...occurence.entries()].map(l => new Leaf(...l)));
        // Then start building the tree
        while (this.length !== 2) {
            // Get child nodes
            let left = this._popLight(),
                right = this._popLight();
            // Then push the new Node
            this.push(
                new Node(
                    [
                        left,
                        right
                    ],
                    left + right,
                )
            )
        }
        this.#weight = this[0] + this[1];
    }

    /**
     * Pop the ligthest node
     * @returns {Node}
     */
     _popLight() {
        // Find the lightest node
        let lightest = this[0],
            i = 0;
        for (let j = 1; j < this.length; j++) if (this[j] < lightest) {
            lightest = this[j];
            i = j;
        }
        // Moove node to reduce the array
        this[i] = this[0];
        this.shift();
        return lightest
    }

    /**
     * Return correct class name
     * @returns {String}
     */
    get [Symbol.toStringTag]() {
        return "Root"
    }

    /**
     * Return correct class name
     * @returns {String}
     */
    static get [Symbol.toStringTag]() {
        return "Root"
    }

    /**
     * Get weight
     * @returns {Number}
     */
    [Symbol.toPrimitive]() {
        return this.#weight
    }

    /**
     * Get the CodeMap mapping the tree
     * @returns {CodeMap}
     */
    getCodeMap() {
        const codeMap = new CodeMap();
        this.setBits(codeMap, "", "");
        return codeMap
    }
}

class CodeMap {

    /**
     * Create a code map (yeah this take me time to choose the name)
     */
    constructor() {
        this.charMap = new Map();
        this.binMap = new Map();
    }

    /**
     * Return correct class name
     * @returns {String}
     */
    get [Symbol.toStringTag]() {
        return "CodeMap"
    }

    /**
     * Return correct class name
     * @returns {String}
     */
    static get [Symbol.toStringTag]() {
        return "CodeMap"
    }

    /**
     * Encode something iterable in a Uint8Array
     * @param {Iterable} decoded 
     * @returns {Uint8Array}
     */
    encode(decoded) {
        let bitString = "1"; // Need first 1 to preserve first 0 digits (so we technically lost 1 bit)
        for (const item of decoded) bitString += this.charMap.get(item);
        return new Uint8Array(`${'0'.repeat(8 - bitString.length % 8)}${bitString}`.match(/.{1,8}/g).map(byteString => parseInt(byteString, 2)))
    }

    /**
     * Decode an encoded Uint8Array
     * @param {Uint8Array} encoded 
     * @returns {Array<Any>}
     */
    decode(encoded) {
        // Convert to a fake bit Iterable.
        encoded = [...encoded].map(byteInt => {
            const byteString = byteInt.toString(2);
            return `${'0'.repeat(8 - byteString.length)}${byteString}`
        });
        const bitString = encoded.join('').slice(encoded[0].indexOf('1') + 1),
            decoded = [];

        let bitStringBuffer = "";

        for (const bit of bitString) {
            bitStringBuffer += bit;
            for (const [bin, char] of this.binMap) {
                if (bitStringBuffer !== bin) continue;
                decoded.push(char);
                bitStringBuffer = "";
            }
        }
        return decoded
    }
}

//* Prototypes

/**
 * Get items' occurences
 * @returns {Map}
 */
String.prototype.occurence = Array.prototype.occurence = function () {
    const occ = new Map();
    for (const k of this) {
        if (occ.has(k)) occ.set(k, 1 + occ.get(k));
        else occ.set(k, 1);
    }
    return occ
}

//* Exports

export default {
    Root,
    CodeMap
}