// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SelfReferentialOracle {
    uint256 public ethReserve;
    uint256 public tokenReserve;
    function getPrice() public view returns (uint256) {
        return (ethReserve * 1e18) / tokenReserve; // BUG: self-referential price
    }
}