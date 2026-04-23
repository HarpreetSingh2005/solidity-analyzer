// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract GovernanceFlashloan {
    mapping(address => uint256) public balance;
    mapping(uint256 => uint256) public votesFor;
    function vote(uint256 proposalId) external {
        votesFor[proposalId] += balance[msg.sender];
    }
}