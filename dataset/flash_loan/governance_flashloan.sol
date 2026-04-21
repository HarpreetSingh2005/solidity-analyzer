// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Governance Attack via Flash-Loaned Voting Tokens
 * CATEGORY: Flash Loan — Single-Block Governance Takeover
 *
 * Governance uses live token balance at vote time (no snapshot).
 * Flash-loaning a majority stake allows passing any proposal in one tx:
 * 1. Flash borrow 51% of governance tokens
 * 2. Create + vote on malicious proposal (e.g., drain() treasury)
 * 3. Execute proposal (no timelock)
 * 4. Repay flash loan
 */
interface IFlashLender {
    function flashLoan(address token, uint256 amount, address receiver) external;
}

contract GovernanceFlashloan {
    mapping(address => uint256) public tokenBalance;
    mapping(uint256 => uint256) public proposalVotes;
    mapping(uint256 => bool)    public proposalPassed;
    mapping(uint256 => address) public proposalTarget;
    mapping(uint256 => bytes)   public proposalCalldata;
    uint256 public proposalCount;
    uint256 public totalSupply = 1_000_000e18;
    address public treasury;

    constructor(address _treasury) {
        treasury = _treasury;
        tokenBalance[msg.sender] = totalSupply;
    }

    function transfer(address to, uint256 amount) external {
        tokenBalance[msg.sender] -= amount;
        tokenBalance[to]         += amount;
    }

    function propose(address target, bytes calldata data) external returns (uint256) {
        uint256 id = ++proposalCount;
        proposalTarget[id]   = target;
        proposalCalldata[id] = data;
        return id;
    }

    // BUG: no snapshot — flash-loaned balance counts
    function vote(uint256 proposalId) external {
        proposalVotes[proposalId] += tokenBalance[msg.sender];
    }

    // BUG: no timelock — execute immediately if >50%
    function execute(uint256 proposalId) external {
        require(proposalVotes[proposalId] > totalSupply / 2, "Not passed");
        require(!proposalPassed[proposalId], "Already executed");
        proposalPassed[proposalId] = true;
        (bool ok,) = proposalTarget[proposalId].call(proposalCalldata[proposalId]);
        require(ok, "Execution failed");
    }
}
