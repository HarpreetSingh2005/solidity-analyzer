// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Governance Double-Vote via Flash Loan / Transfer
 * CATEGORY: Business Logic — Missing Snapshot on Delegation
 *
 * Votes are counted from live balances at the time of castVote(), NOT
 * from a snapshot taken at proposal creation. A whale (or flash loan attacker)
 * can buy tokens, vote, transfer tokens to a second address, and vote again —
 * effectively double-spending their voting power within one proposal.
 */
contract GovernanceDoubleVote {
    mapping(address => uint256) public tokenBalance;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    mapping(uint256 => uint256) public votesFor;
    mapping(uint256 => uint256) public votesAgainst;
    uint256 public proposalCount;
    uint256 public totalSupply = 1_000_000e18;

    constructor() {
        tokenBalance[msg.sender] = totalSupply;
    }

    function transfer(address to, uint256 amount) external {
        require(tokenBalance[msg.sender] >= amount);
        tokenBalance[msg.sender] -= amount;
        tokenBalance[to]         += amount;
    }

    function createProposal() external returns (uint256) {
        // BUG: no snapshot of balances taken here
        return ++proposalCount;
    }

    function castVote(uint256 proposalId, bool support) external {
        require(!hasVoted[proposalId][msg.sender], "Already voted");
        hasVoted[proposalId][msg.sender] = true;

        // BUG: uses LIVE balance — attacker votes, transfers tokens, votes again
        uint256 weight = tokenBalance[msg.sender];
        if (support) votesFor[proposalId]     += weight;
        else         votesAgainst[proposalId] += weight;
    }

    function isProposalPassed(uint256 proposalId) external view returns (bool) {
        return votesFor[proposalId] > totalSupply / 2;
    }
}
