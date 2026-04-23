// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract MultiSourceOracle {
    function getPrice(uint256 p1, uint256 p2) public pure returns (uint256) {
        return (p1 + p2) / 2; // BUG: correlated sources
    }
}