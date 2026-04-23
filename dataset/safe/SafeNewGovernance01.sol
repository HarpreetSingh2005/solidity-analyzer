// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe Governance utilizing strict proposal checks.
contract SafeNewGovernance01 {
    error VotingEnded();
    error AlreadyVoted();
    
    struct Proposal { uint256 id; uint256 endTime; uint256 votes; }
    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    function vote(uint256 proposalId) external {
        Proposal storage p = proposals[proposalId];
        if (block.timestamp >= p.endTime) revert VotingEnded();
        if (hasVoted[proposalId][msg.sender]) revert AlreadyVoted();
        
        hasVoted[proposalId][msg.sender] = true;
        p.votes += 1;
    }
}