// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Vesting Cliff Bypass via Token Transfer
 * CATEGORY: Business Logic — Incorrect State Transition
 *
 * The vesting cliff is keyed to msg.sender at deposit time.
 * If tokens are transferable (standard ERC-20), a user can simply
 * transfer their unvested position to a fresh wallet and immediately
 * claim — the new address has no cliff recorded, so `startTime` defaults
 * to 0 and the cliff check passes for any timestamp.
 */
contract VestingBypass {
    struct VestingSchedule {
        uint256 amount;
        uint256 startTime;
        uint256 cliffDuration;  // seconds before any withdrawal allowed
        uint256 totalDuration;
        bool    exists;
    }

    mapping(address => VestingSchedule) public schedules;
    mapping(address => uint256) public balances; // internal "token"

    function createVesting(uint256 amount, uint256 cliff, uint256 total) external {
        require(!schedules[msg.sender].exists, "Already vesting");
        schedules[msg.sender] = VestingSchedule(amount, block.timestamp, cliff, total, true);
        balances[msg.sender]  = amount;
    }

    // BUG: transferring balance moves funds but NOT the vesting schedule
    function transferBalance(address to, uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient");
        balances[msg.sender] -= amount;
        balances[to]         += amount;
        // schedule not transferred — recipient has no schedule → defaults allow full claim
    }

    function withdraw(uint256 amount) external {
        VestingSchedule storage s = schedules[msg.sender];
        // BUG: if no schedule, startTime=0 → cliff always passed, vestedAmount = amount
        uint256 elapsed = block.timestamp - s.startTime;
        require(elapsed >= s.cliffDuration, "Cliff not reached");
        uint256 vestedAmount = s.totalDuration == 0
            ? balances[msg.sender]  // BUG: no duration means 100% vested instantly
            : (s.amount * elapsed) / s.totalDuration;
        require(balances[msg.sender] >= amount && amount <= vestedAmount, "Not vested");
        balances[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
    }

    receive() external payable {}
}
