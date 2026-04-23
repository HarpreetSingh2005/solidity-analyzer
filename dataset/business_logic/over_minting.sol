// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract OverMinting {
    uint256 public totalSupply;
    function mint(address to, uint256 amount) external {
        totalSupply += amount; // BUG: no cap or access control
    }
}