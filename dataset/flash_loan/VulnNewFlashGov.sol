// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Governance proposal can be passed using flash-loaned tokens.
contract VulnNewFlashGov {
    mapping(address => uint256) public tokenBalances;
    function vote(uint256 proposalId) external {
        // Uses spot balance, attacker can flash loan, vote, and repay in 1 tx
        uint256 weight = tokenBalances[msg.sender]; 
    }
}