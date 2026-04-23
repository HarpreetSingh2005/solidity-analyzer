// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Out of bounds array deletion/manipulation logic.
contract VulnNewArrayOutofBounds {
    uint256[] public data;
    function popElement(uint256 index) external {
        // No check if index < data.length, though 0.8+ reverts on out of bounds. 
        // Vulnerability: Replaces with last element but doesn't check if array is empty
        data[index] = data[data.length - 1];
        data.pop();
    }
}