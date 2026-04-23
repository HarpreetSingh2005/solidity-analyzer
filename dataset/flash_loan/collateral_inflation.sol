// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract CollateralInflation {
    mapping(address => uint256) public collateral;
    function deposit() external payable {
        collateral[msg.sender] += msg.value;
    }
}