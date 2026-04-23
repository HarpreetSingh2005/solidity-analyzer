// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Strict equality on balance can be broken by forced ETH transfer.
contract VulnNewStrictEquality {
    function execute() external {
        require(address(this).balance == 10 ether, "Must be exactly 10");
        // An attacker can selfdestruct 1 wei to this contract, permanently breaking this logic
    }
}