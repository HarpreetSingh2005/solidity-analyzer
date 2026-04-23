// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Price inversion division rounds to zero.
contract VulnNewOracleInversion {
    function getInvertedPrice(uint256 price) public pure returns (uint256) {
        // If price > 1e18, 1e18 / price rounds to 0!
        return 1e18 / price;
    }
}