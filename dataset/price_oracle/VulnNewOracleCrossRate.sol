// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Cross rate math loses precision.
contract VulnNewOracleCrossRate {
    function getCrossRate(uint256 priceA, uint256 priceB) public pure returns (uint256) {
        // Division before multiplication loses precision
        return (priceA / priceB) * 1e18; 
    }
}