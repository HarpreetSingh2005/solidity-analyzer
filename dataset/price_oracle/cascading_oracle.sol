// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract CascadingOracle {
    function getPrice(uint256 base, uint256 multiplier) public pure returns (uint256) {
        return base * multiplier / 1e18; // BUG: cascading dependency
    }
}