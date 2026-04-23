// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract IncorrectLiquidation {
    mapping(address => uint256) public collateral;
    mapping(address => uint256) public debt;
    function isHealthy(address user) public view returns (bool) {
        return collateral[user] >= debt[user]; // BUG: should be collateral * 0.75 >= debt
    }
}