// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnBridgeFakeDeposit {
    mapping(address => uint256) public bridgedTokens;

    // Vulnerability: Anyone can mint fake tokens on the destination chain without depositing
    function notifyDeposit(address user, uint256 amount) external {
        // Missing check that msg.sender is the actual bridge contract!
        bridgedTokens[user] += amount;
    }
}