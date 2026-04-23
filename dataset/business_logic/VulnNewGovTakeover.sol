// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Governance voting uses spot balances, allowing flash-loan takeover.
contract VulnNewGovTakeover {
    mapping(address => uint256) public balances;
    uint256 public yesVotes;
    function vote() external {
        yesVotes += balances[msg.sender]; // Uses spot balance
    }
}