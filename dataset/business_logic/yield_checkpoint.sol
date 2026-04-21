// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Missing Yield Checkpoint on Deposit
 * CATEGORY: Business Logic — Retroactive Reward Capture
 *
 * Yield accrues globally as yieldPerToken increases over time.
 * When a user deposits, their rewardDebt should be set to the CURRENT
 * accumulated yield so they don't receive retroactive rewards.
 * The missing checkpoint lets a new depositor claim all past yield
 * immediately after joining the pool.
 */
contract YieldCheckpoint {
    mapping(address => uint256) public deposited;
    mapping(address => uint256) public rewardDebt;
    uint256 public totalDeposited;
    uint256 public yieldPerToken;        // accumulated yield per token (scaled 1e18)
    uint256 public lastUpdateTime;
    uint256 public yieldRate = 1e15;     // 0.001 token per second per token

    function _updateYield() internal {
        if (totalDeposited == 0) { lastUpdateTime = block.timestamp; return; }
        uint256 dt = block.timestamp - lastUpdateTime;
        yieldPerToken   += (dt * yieldRate);
        lastUpdateTime   = block.timestamp;
    }

    function deposit(uint256 amount) external {
        _updateYield();
        deposited[msg.sender]  += amount;
        totalDeposited         += amount;
        // BUG: rewardDebt not updated here — user retroactively earns all past yield
        // FIX: rewardDebt[msg.sender] = yieldPerToken * deposited[msg.sender] / 1e18;
    }

    function claimYield() external {
        _updateYield();
        uint256 gross = (yieldPerToken * deposited[msg.sender]) / 1e18;
        uint256 net   = gross - rewardDebt[msg.sender];
        rewardDebt[msg.sender] = gross;
        payable(msg.sender).transfer(net);
    }

    receive() external payable {}
}
